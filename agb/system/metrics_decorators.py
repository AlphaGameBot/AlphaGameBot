# Copyright (c) 2025 Damien Boisvert (AlphaGameDeveloper)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import functools
import time
import logging
from typing import Optional, Callable, Any

# Global prometheus exporter reference
_prometheus_exporter = None

def set_prometheus_exporter(exporter):
    """Set the global prometheus exporter instance."""
    global _prometheus_exporter
    _prometheus_exporter = exporter

def get_prometheus_exporter():
    """Get the global prometheus exporter instance."""
    return _prometheus_exporter

def track_execution_time(metric_name: str, track_errors: bool = True):
    """
    Decorator to track function execution time and optionally errors.
    
    Args:
        metric_name: Name to use for the metric
        track_errors: Whether to track errors as well
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            exporter = get_prometheus_exporter()
            logger = logging.getLogger("metrics")
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                if track_errors and exporter:
                    try:
                        error_type = f"{metric_name}_error"
                        exporter.track_error(error_type)
                        logger.debug("Tracked error for %s: %s", metric_name, str(e))
                    except Exception as track_error:
                        logger.warning("Failed to track error metric: %s", track_error)
                raise
            finally:
                if exporter:
                    try:
                        execution_time = time.time() - start_time
                        # Track as API response time for now, could be extended for other metric types
                        exporter.track_api_call(metric_name, execution_time)
                        logger.debug("Tracked execution time for %s: %.4f seconds", metric_name, execution_time)
                    except Exception as track_error:
                        logger.warning("Failed to track execution time metric: %s", track_error)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            exporter = get_prometheus_exporter()
            logger = logging.getLogger("metrics")
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if track_errors and exporter:
                    try:
                        error_type = f"{metric_name}_error"
                        exporter.track_error(error_type)
                        logger.debug("Tracked error for %s: %s", metric_name, str(e))
                    except Exception as track_error:
                        logger.warning("Failed to track error metric: %s", track_error)
                raise
            finally:
                if exporter:
                    try:
                        execution_time = time.time() - start_time
                        exporter.track_api_call(metric_name, execution_time)
                        logger.debug("Tracked execution time for %s: %.4f seconds", metric_name, execution_time)
                    except Exception as track_error:
                        logger.warning("Failed to track execution time metric: %s", track_error)
        
        # Return the appropriate wrapper based on whether the function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def track_api_call(api_name: str):
    """
    Decorator specifically for tracking external API calls.
    
    Args:
        api_name: Name of the external API
    """
    return track_execution_time(f"api_{api_name}", track_errors=True)

def track_database_operation(operation_name: str):
    """
    Decorator for tracking database operations.
    
    Args:
        operation_name: Name of the database operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            exporter = get_prometheus_exporter()
            logger = logging.getLogger("metrics")
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                if exporter:
                    try:
                        exporter.track_error(f"database_{operation_name}_error")
                        logger.debug("Tracked database error for %s: %s", operation_name, str(e))
                    except Exception as track_error:
                        logger.warning("Failed to track database error metric: %s", track_error)
                raise
            finally:
                if exporter:
                    try:
                        query_time = time.time() - start_time
                        exporter.track_database_query(query_time)
                        logger.debug("Tracked database operation %s: %.4f seconds", operation_name, query_time)
                    except Exception as track_error:
                        logger.warning("Failed to track database metric: %s", track_error)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            exporter = get_prometheus_exporter()
            logger = logging.getLogger("metrics")
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if exporter:
                    try:
                        exporter.track_error(f"database_{operation_name}_error")
                        logger.debug("Tracked database error for %s: %s", operation_name, str(e))
                    except Exception as track_error:
                        logger.warning("Failed to track database error metric: %s", track_error)
                raise
            finally:
                if exporter:
                    try:
                        query_time = time.time() - start_time
                        exporter.track_database_query(query_time)
                        logger.debug("Tracked database operation %s: %.4f seconds", operation_name, query_time)
                    except Exception as track_error:
                        logger.warning("Failed to track database metric: %s", track_error)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def track_feature_usage(feature_name: str):
    """
    Decorator for tracking feature usage (like commands, games, etc.).
    
    Args:
        feature_name: Name of the feature being used
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            exporter = get_prometheus_exporter()
            logger = logging.getLogger("metrics")
            
            # Track feature usage
            if exporter:
                try:
                    # Use command tracking for features
                    exporter.data.command_counts[f"feature_{feature_name}"] += 1
                    logger.debug("Tracked feature usage: %s", feature_name)
                except Exception as track_error:
                    logger.warning("Failed to track feature usage metric: %s", track_error)
            
            # Execute the original function
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            exporter = get_prometheus_exporter()
            logger = logging.getLogger("metrics")
            
            # Track feature usage
            if exporter:
                try:
                    exporter.data.command_counts[f"feature_{feature_name}"] += 1
                    logger.debug("Tracked feature usage: %s", feature_name)
                except Exception as track_error:
                    logger.warning("Failed to track feature usage metric: %s", track_error)
            
            # Execute the original function
            return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator