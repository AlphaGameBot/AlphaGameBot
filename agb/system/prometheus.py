# Copyright (c) 2025 Damien Boisvert (AlphaGameDeveloper)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging
import time
import os
from asyncio import sleep
from aiohttp import ClientSession
from .cogwheel import getBotInformation
from mysql.connector import MySQLConnection
from typing import Dict, List, Optional, Union
from collections import defaultdict, deque
from datetime import datetime, timedelta

# Try to import psutil, but make it optional
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# FIXME: this can be done much better with asyncio mysql connector

class PrometheusMetricsData:
    startup_time: int | float
    counted_messages: int
    
    # Performance tracking
    command_counts: Dict[str, int]
    command_execution_times: Dict[str, deque]
    error_counts: Dict[str, int]
    api_response_times: Dict[str, deque]
    database_query_times: deque
    
    # User activity tracking
    active_users_daily: set
    active_users_weekly: set
    active_users_monthly: set
    last_daily_reset: datetime
    last_weekly_reset: datetime
    last_monthly_reset: datetime
    
    # Guild tracking
    guild_activity: Dict[int, int]
    last_guild_count: int

    def __init__(self, cnx: Optional[MySQLConnection]) -> None:
        self.startup_time = time.time()
        self.counted_messages = 0
        self.cnx = cnx  # May be None if database is disabled
        
        # Initialize performance tracking
        self.command_counts = defaultdict(int)
        self.command_execution_times = defaultdict(lambda: deque(maxlen=100))
        self.error_counts = defaultdict(int)
        self.api_response_times = defaultdict(lambda: deque(maxlen=50))
        self.database_query_times = deque(maxlen=100)
        
        # Initialize user activity tracking
        self.active_users_daily = set()
        self.active_users_weekly = set()
        self.active_users_monthly = set()
        now = datetime.now()
        self.last_daily_reset = now
        self.last_weekly_reset = now
        self.last_monthly_reset = now
        
        # Initialize guild tracking
        self.guild_activity = defaultdict(int)
        self.last_guild_count = 0

    def increment_message_count(self, user_id: Optional[int] = None, guild_id: Optional[int] = None) -> int:
        """Increments the message count and returns the new count."""
        self.counted_messages += 1
        
        # Track user activity
        if user_id:
            self._track_user_activity(user_id)
        
        # Track guild activity
        if guild_id:
            self.guild_activity[guild_id] += 1
            
        return self.counted_messages
    
    def increment_command_count(self, command_name: str, execution_time: float, user_id: Optional[int] = None) -> None:
        """Track command usage and performance."""
        self.command_counts[command_name] += 1
        self.command_execution_times[command_name].append(execution_time)
        
        if user_id:
            self._track_user_activity(user_id)
    
    def track_error(self, error_type: str) -> None:
        """Track errors by type."""
        self.error_counts[error_type] += 1
    
    def track_api_response_time(self, api_name: str, response_time: float) -> None:
        """Track external API response times."""
        self.api_response_times[api_name].append(response_time)
    
    def track_database_query_time(self, query_time: float) -> None:
        """Track database query execution times."""
        self.database_query_times.append(query_time)
    
    def _track_user_activity(self, user_id: int) -> None:
        """Internal method to track user activity across different time periods."""
        now = datetime.now()
        
        # Reset counters if needed
        if now - self.last_daily_reset >= timedelta(days=1):
            self.active_users_daily.clear()
            self.last_daily_reset = now
            
        if now - self.last_weekly_reset >= timedelta(weeks=1):
            self.active_users_weekly.clear()
            self.last_weekly_reset = now
            
        if now - self.last_monthly_reset >= timedelta(days=30):
            self.active_users_monthly.clear()
            self.last_monthly_reset = now
        
        # Add user to activity sets
        self.active_users_daily.add(user_id)
        self.active_users_weekly.add(user_id)
        self.active_users_monthly.add(user_id)
    
    def get_uptime(self) -> float:
        """Returns uptime, in seconds, or -1 if not started."""
        if self.startup_time == -1:
            return -1
        return time.time() - self.startup_time
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        if not HAS_PSUTIL:
            return {'rss': 0.0, 'vms': 0.0, 'percent': 0.0}
        
        import psutil  # Import here to avoid "possibly unbound" error
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        if not HAS_PSUTIL:
            return 0.0
        
        import psutil  # Import here to avoid "possibly unbound" error
        process = psutil.Process(os.getpid())
        return process.cpu_percent()
    
    def get_message_counts_by_guild(self) -> dict[int, int]:
        """Returns a dictionary mapping guild IDs to their respective message counts."""
        if self.cnx is None:
            return {}
            
        cursor = self.cnx.cursor()
        
        # get all guild IDs
        cursor.execute("SELECT DISTINCT guildid FROM guild_user_stats")
        guild_ids = [row[0] for row in cursor.fetchall()]

        # get all message counts by guildid
        cursor.execute("SELECT guildid, SUM(messages_sent) FROM guild_user_stats GROUP BY guildid")
        result = {int(guild_id): int(message_count) for guild_id, message_count in cursor.fetchall()} # pyright: ignore[reportArgumentType]
        cursor.close()
        return result
    
    def get_command_counts_by_guild(self) -> dict[int, int]:
        """Returns command counts by guild."""
        if self.cnx is None:
            return {}
            
        cursor = self.cnx.cursor()
        cursor.execute("SELECT guildid, SUM(commands_ran) FROM guild_user_stats GROUP BY guildid")
        result = {int(guild_id): int(command_count) for guild_id, command_count in cursor.fetchall()} # pyright: ignore[reportArgumentType]
        cursor.close()
        return result
    
    def get_user_level_distribution(self) -> Dict[int, int]:
        """Get distribution of user levels."""
        if self.cnx is None:
            return {}
            
        cursor = self.cnx.cursor()
        cursor.execute("SELECT user_level, COUNT(*) FROM guild_user_stats GROUP BY user_level")
        result = {int(level): int(count) for level, count in cursor.fetchall()} # pyright: ignore[reportArgumentType]
        cursor.close()
        return result
    
    def get_guild_size_distribution(self) -> Dict[str, int]:
        """Get distribution of guild sizes."""
        if self.cnx is None:
            return {}
            
        cursor = self.cnx.cursor()
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN member_count < 10 THEN 'small'
                    WHEN member_count < 100 THEN 'medium'
                    WHEN member_count < 1000 THEN 'large'
                    ELSE 'very_large'
                END as size_category,
                COUNT(*) as count
            FROM guild_settings 
            WHERE member_count IS NOT NULL
            GROUP BY size_category
        """)
        result: Dict[str, int] = {}
        for row in cursor.fetchall():
            category, count = row
            try:
                # Convert safely using string intermediate to avoid type issues
                count_str = str(count)
                count_int = int(count_str) if count_str.isdigit() else 0
                result[str(category)] = count_int
            except (ValueError, TypeError):
                result[str(category)] = 0
        cursor.close()
        return result
    
    def get_avg_command_execution_time(self, command_name: str) -> float:
        """Get average execution time for a command."""
        times = self.command_execution_times.get(command_name, [])
        return sum(times) / len(times) if times else 0.0
    
    def get_avg_api_response_time(self, api_name: str) -> float:
        """Get average response time for an API."""
        times = self.api_response_times.get(api_name, [])
        return sum(times) / len(times) if times else 0.0
    
    def get_avg_database_query_time(self) -> float:
        """Get average database query time."""
        return sum(self.database_query_times) / len(self.database_query_times) if self.database_query_times else 0.0
    
class PrometheusMetricExporter:
    def __init__(self, cnx: Optional[MySQLConnection], pushgateway_url: str, interval: int = 15) -> None:
        self.cnx  = cnx
        self.data = PrometheusMetricsData(cnx)
        self.pushgateway_url = pushgateway_url
        self.interval = interval
        self.trackerLogger = logging.getLogger("prometheus.tracker")
        with open("assets/prometheus_template.txt", "r") as f:
            self.prometheus_template = f.read()

    def start(self) -> None:
        """Starts the metrics exporter."""
        self.data.startup_time = time.time()
    
    def track_command_execution(self, command_name: str, execution_time: float, user_id: Optional[int] = None) -> None:
        """Track command execution metrics."""
        self.trackerLogger.debug(f"Tracking command execution: {command_name}, {execution_time}, {user_id}")
        self.data.increment_command_count(command_name, execution_time, user_id)
    
    def track_message(self, user_id: Optional[int] = None, guild_id: Optional[int] = None) -> None:
        """Track message metrics."""
        self.trackerLogger.debug(f"Tracking message: {user_id}, {guild_id}")
        self.data.increment_message_count(user_id, guild_id)
    
    def track_error(self, error_type: str) -> None:
        """Track error metrics."""
        self.trackerLogger.debug(f"Tracking error: {error_type}")
        self.data.track_error(error_type)
    
    def track_api_call(self, api_name: str, response_time: float) -> None:
        """Track external API call metrics."""
        self.trackerLogger.debug(f"Tracking API call: {api_name}, {response_time}")
        self.data.track_api_response_time(api_name, response_time)
    
    def track_database_query(self, query_time: float) -> None:
        """Track database query metrics."""
        self.trackerLogger.debug(f"Tracking database query time: {query_time}")
        self.data.track_database_query_time(query_time)
    
    def generate_metrics_payload(self, bot_instance=None) -> str:
        """Generate the complete metrics payload for Pushgateway."""
        BOT_INFORMATION = getBotInformation()
        
        # Basic metrics
        messages_counted_by_guild_dict = self.data.get_message_counts_by_guild()
        commands_counted_by_guild_dict = self.data.get_command_counts_by_guild()
        
        # Generate guild-specific metrics
        messages_counted_by_guild = ""
        for guild_id, message_count in messages_counted_by_guild_dict.items():
            messages_counted_by_guild += f'bot_messages_counted_by_guild{{guild="{guild_id}"}} {message_count}\n'
        
        commands_counted_by_guild = ""
        for guild_id, command_count in commands_counted_by_guild_dict.items():
            commands_counted_by_guild += f'bot_commands_counted_by_guild{{guild="{guild_id}"}} {command_count}\n'
        
        # Command-specific metrics
        command_metrics = ""
        for command_name, count in self.data.command_counts.items():
            avg_time = self.data.get_avg_command_execution_time(command_name)
            command_metrics += f'bot_command_count{{command="{command_name}"}} {count}\n'
            command_metrics += f'bot_command_avg_duration_seconds{{command="{command_name}"}} {avg_time:.4f}\n'
        
        # Error metrics
        error_metrics = ""
        for error_type, count in self.data.error_counts.items():
            error_metrics += f'bot_errors_total{{type="{error_type}"}} {count}\n'
        
        # API metrics
        api_metrics = ""
        for api_name, times in self.data.api_response_times.items():
            if times:
                avg_time = sum(times) / len(times)
                api_metrics += f'bot_api_response_time_seconds{{api="{api_name}"}} {avg_time:.4f}\n'
        
        # User activity metrics
        user_activity_metrics = f"""
bot_active_users_daily {len(self.data.active_users_daily)}
bot_active_users_weekly {len(self.data.active_users_weekly)}
bot_active_users_monthly {len(self.data.active_users_monthly)}
"""
        
        # Performance metrics
        memory_info = self.data.get_memory_usage()
        cpu_usage = self.data.get_cpu_usage()
        avg_db_time = self.data.get_avg_database_query_time()
        
        performance_metrics = f"""
bot_memory_usage_mb{{type="rss"}} {memory_info['rss']:.2f}
bot_memory_usage_mb{{type="vms"}} {memory_info['vms']:.2f}
bot_memory_usage_percent {memory_info['percent']:.2f}
bot_cpu_usage_percent {cpu_usage:.2f}
bot_database_avg_query_time_seconds {avg_db_time:.4f}
"""
        
        # Bot-specific metrics (if bot instance available)
        bot_metrics = ""
        if bot_instance:
            try:
                guild_count = len(bot_instance.guilds)
                latency_ms = round(bot_instance.latency * 1000, 2)
                bot_metrics += f'bot_guild_count {guild_count}\n'
                bot_metrics += f'bot_latency_ms {latency_ms}\n'
                
                # Calculate total users across all guilds
                total_users = sum(len(guild.members) for guild in bot_instance.guilds)
                bot_metrics += f'bot_total_users {total_users}\n'
            except Exception as e:
                logging.getLogger("prometheus").warning(f"Failed to get bot metrics: {e}")
        
        # Level distribution metrics
        level_distribution = self.data.get_user_level_distribution()
        level_metrics = ""
        for level, count in level_distribution.items():
            level_metrics += f'bot_user_level_distribution{{level="{level}"}} {count}\n'
        
        # Generate final payload
        data = self.prometheus_template.replace(
            "{{version}}", BOT_INFORMATION["VERSION"]
        ).replace(
            "{{uptime_seconds}}", str(self.data.get_uptime())
        ).replace(
            "{{message_count}}", str(self.data.counted_messages)
        ).replace(
            "{{messages_counted_by_guild}}", messages_counted_by_guild
        ).replace(
            "{{commands_counted_by_guild}}", commands_counted_by_guild
        ).replace(
            "{{command_metrics}}", command_metrics
        ).replace(
            "{{error_metrics}}", error_metrics
        ).replace(
            "{{api_metrics}}", api_metrics
        ).replace(
            "{{user_activity_metrics}}", user_activity_metrics
        ).replace(
            "{{performance_metrics}}", performance_metrics
        ).replace(
            "{{bot_metrics}}", bot_metrics
        ).replace(
            "{{level_metrics}}", level_metrics
        )
        
        return data

    async def update_push_gateway_loop(self, bot_instance=None) -> None:
        """Periodically pushes metrics to the Pushgateway."""
        logger = logging.getLogger("listener")
        
        async with ClientSession() as session:
            while True:
                logger.debug("Pushing metrics to Pushgateway...")
                t1 = time.time()
                
                try:
                    data = self.generate_metrics_payload(bot_instance)
                    await session.post(self.pushgateway_url, data=data)
                    
                    t2 = time.time()
                    push_time = t2 - t1
                    logger.debug("Pushed metrics to Pushgateway in %.2f seconds.", push_time)
                    
                    # Track the push operation itself as a metric
                    self.data.track_api_response_time("pushgateway", push_time)
                    
                except Exception as e:
                    logger.error("Failed to push metrics to Pushgateway: %s", e)
                    self.data.track_error("prometheus_push_failed")
                
                await sleep(self.interval)

    def stop(self) -> None:
        """Stops the metrics exporter."""
        self.data.startup_time = -1