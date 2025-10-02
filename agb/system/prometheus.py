# Copyright (c) 2025 Damien Boisvert (AlphaGameDeveloper)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging
import time
from asyncio import sleep
from aiohttp import ClientSession
from .cogwheel import getBotInformation
from mysql.connector import MySQLConnection

# FIXME: this can be done much better with asyncio mysql connector

class PrometheusMetricsData:
    startup_time: int | float
    counted_messages: int

    def __init__(self, cnx: MySQLConnection) -> None:
        self.startup_time = time.time()
        self.counted_messages = 0
        self.cnx = cnx

    def increment_message_count(self) -> int:
        """Increments the message count and returns the new count."""
        self.counted_messages += 1
        return self.counted_messages
    
    def get_uptime(self) -> float:
        """Returns uptime, in seconds, or -1 if not started."""
        if self.startup_time == -1:
            return -1
        return time.time() - self.startup_time
    
    def get_message_counts_by_guild(self) -> dict[int, int]:
        """Returns a dictionary mapping guild IDs to their respective message counts."""
        cursor = self.cnx.cursor()
        
        # get all guild IDs
        cursor.execute("SELECT DISTINCT guildid FROM guild_user_stats")

        guild_ids = [row[0] for row in cursor.fetchall()]

        # get all message counts by guildid
        cursor.execute("SELECT guildid, SUM(messages_sent) FROM guild_user_stats GROUP BY guildid")
        result = {int(guild_id): int(message_count) for guild_id, message_count in cursor.fetchall()} # pyright: ignore[reportArgumentType]
        cursor.close()
        return result
    
class PrometheusMetricExporter:
    def __init__(self, cnx: MySQLConnection, pushgateway_url: str, interval: int = 15) -> None:
        self.cnx  = cnx
        self.data = PrometheusMetricsData(cnx)
        self.pushgateway_url = pushgateway_url
        self.interval = interval
        
        with open("assets/prometheus_template.txt", "r") as f:
            self.prometheus_template = f.read()

    def start(self) -> None:
        """Starts the metrics exporter."""
        self.data.startup_time = time.time()
    
    async def update_push_gateway_loop(self) -> None:
        """Periodically pushes metrics to the Pushgateway."""
        logger = logging.getLogger("listener")

        BOT_INFORMATION = getBotInformation()
        
        async with ClientSession() as session:
            while True:
                logger.debug("Pushing metrics to Pushgateway...")
                # performance:
                t1 = time.time()
                # Placeholder for actual Pushgateway update logic
                messages_counted_by_guild_dict = self.data.get_message_counts_by_guild()

                messages_counted_by_guild = ""
                for guild_id, message_count in messages_counted_by_guild_dict.items():
                    messages_counted_by_guild += f'bot_messages_counted_by_guild{{guild="{guild_id}"}} {message_count}\n'
                data = self.prometheus_template.replace(
                    "{{version}}", BOT_INFORMATION["VERSION"]
                ).replace(
                    "{{uptime_seconds}}", str(self.data.get_uptime())
                ).replace(
                    "{{message_count}}", str(self.data.counted_messages)
                ).replace(
                    "{{messages_counted_by_guild}}", messages_counted_by_guild
                )
                await session.post(self.pushgateway_url, data=data)
                t2 = time.time()
                logger.debug("Pushed metrics to Pushgateway in %.2f seconds.", t2 - t1)
                await sleep(self.interval)

    def stop(self) -> None:
        """Stops the metrics exporter."""
        self.data.startup_time = -1