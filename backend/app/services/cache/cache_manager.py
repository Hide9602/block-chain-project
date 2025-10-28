"""
Cache Manager for Performance Optimization
パフォーマンス最適化のためのキャッシュマネージャー
"""

from typing import Any, Optional, Callable
from functools import wraps
import hashlib
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Cache manager for application-level caching
    In production, use Redis or Memcached
    """
    
    def __init__(self):
        """Initialize cache manager"""
        # In-memory cache for development
        # In production, replace with Redis client
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self.default_ttl = 300  # 5 minutes default TTL
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        
        # Check if expired
        if datetime.utcnow() > expiry:
            del self._cache[key]
            return None
        
        logger.debug(f"Cache hit: {key}")
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time > expiry
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: Optional[int] = None, prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        prefix: Cache key prefix
    
    Usage:
        @cached(ttl=600, prefix="blockchain")
        async def get_blockchain_data(address: str):
            return await fetch_data(address)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(
                prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(
                prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class QueryOptimizer:
    """Query optimization utilities"""
    
    @staticmethod
    def paginate_results(items: list, page: int = 1, page_size: int = 50):
        """
        Paginate results for better performance
        
        Args:
            items: List of items to paginate
            page: Page number (1-indexed)
            page_size: Items per page
        
        Returns:
            Paginated results with metadata
        """
        total_items = len(items)
        total_pages = (total_items + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_items = items[start_idx:end_idx]
        
        return {
            "items": paginated_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    
    @staticmethod
    def batch_process(items: list, batch_size: int = 100):
        """
        Process items in batches
        
        Args:
            items: List of items
            batch_size: Size of each batch
        
        Yields:
            Batches of items
        """
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics: dict[str, list[float]] = {}
    
    def record_execution_time(self, operation: str, duration: float):
        """Record execution time for an operation"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append(duration)
        
        # Keep only last 1000 measurements
        if len(self.metrics[operation]) > 1000:
            self.metrics[operation] = self.metrics[operation][-1000:]
    
    def get_statistics(self, operation: str) -> dict:
        """Get statistics for an operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
        
        durations = self.metrics[operation]
        
        return {
            "operation": operation,
            "count": len(durations),
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations),
            "total": sum(durations)
        }
    
    def get_all_statistics(self) -> dict:
        """Get statistics for all operations"""
        return {
            operation: self.get_statistics(operation)
            for operation in self.metrics.keys()
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str):
    """
    Decorator to monitor function performance
    
    Usage:
        @monitor_performance("blockchain_fetch")
        async def fetch_blockchain_data():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = (datetime.utcnow() - start_time).total_seconds()
                performance_monitor.record_execution_time(operation_name, duration)
                
                if duration > 5.0:  # Log slow operations
                    logger.warning(
                        f"Slow operation: {operation_name} took {duration:.2f}s"
                    )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (datetime.utcnow() - start_time).total_seconds()
                performance_monitor.record_execution_time(operation_name, duration)
                
                if duration > 5.0:
                    logger.warning(
                        f"Slow operation: {operation_name} took {duration:.2f}s"
                    )
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
