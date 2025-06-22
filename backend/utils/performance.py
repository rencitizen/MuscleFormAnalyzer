"""
Performance monitoring and optimization utilities
"""
import time
import logging
from functools import wraps
from typing import Callable, Optional, Dict, Any
import asyncio
import psutil
import gc

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor API performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "endpoint_times": {},
            "db_query_times": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0
        }
    
    def record_endpoint_time(self, endpoint: str, duration: float):
        """Record endpoint response time"""
        if endpoint not in self.metrics["endpoint_times"]:
            self.metrics["endpoint_times"][endpoint] = []
        
        self.metrics["endpoint_times"][endpoint].append(duration)
        
        # Keep only last 100 entries per endpoint
        if len(self.metrics["endpoint_times"][endpoint]) > 100:
            self.metrics["endpoint_times"][endpoint] = self.metrics["endpoint_times"][endpoint][-100:]
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.metrics["cache_misses"] += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        summary = {
            "cache_hit_rate": self.metrics["cache_hits"] / max(1, self.metrics["cache_hits"] + self.metrics["cache_misses"]),
            "total_requests": self.metrics["total_requests"],
            "endpoint_avg_times": {}
        }
        
        # Calculate average times per endpoint
        for endpoint, times in self.metrics["endpoint_times"].items():
            if times:
                summary["endpoint_avg_times"][endpoint] = {
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times)
                }
        
        return summary

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

def measure_performance(name: Optional[str] = None):
    """
    Decorator to measure function performance
    
    Args:
        name: Optional name for the measurement
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                measurement_name = name or f"{func.__module__}.{func.__name__}"
                logger.debug(f"Performance: {measurement_name} took {duration:.3f}s")
                perf_monitor.record_endpoint_time(measurement_name, duration)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {name or func.__name__} after {duration:.3f}s: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                measurement_name = name or f"{func.__module__}.{func.__name__}"
                logger.debug(f"Performance: {measurement_name} took {duration:.3f}s")
                perf_monitor.record_endpoint_time(measurement_name, duration)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {name or func.__name__} after {duration:.3f}s: {e}")
                raise
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def profile_memory():
    """Get current memory usage"""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss / 1024 / 1024,  # MB
        "vms": memory_info.vms / 1024 / 1024,  # MB
        "percent": process.memory_percent(),
        "available": psutil.virtual_memory().available / 1024 / 1024  # MB
    }

def optimize_memory():
    """Run garbage collection and optimize memory"""
    collected = gc.collect()
    logger.info(f"Garbage collection: {collected} objects collected")
    
    return {
        "objects_collected": collected,
        "memory_after": profile_memory()
    }

class ResourceLimiter:
    """Limit resource usage for operations"""
    
    def __init__(self, max_memory_mb: int = 500, max_time_seconds: int = 30):
        self.max_memory_mb = max_memory_mb
        self.max_time_seconds = max_time_seconds
    
    async def check_resources(self):
        """Check if resources are within limits"""
        memory = profile_memory()
        
        if memory["rss"] > self.max_memory_mb:
            logger.warning(f"Memory usage ({memory['rss']:.1f}MB) exceeds limit ({self.max_memory_mb}MB)")
            optimize_memory()
            
            # Re-check after optimization
            memory = profile_memory()
            if memory["rss"] > self.max_memory_mb:
                raise MemoryError(f"Memory usage too high: {memory['rss']:.1f}MB")
    
    def __call__(self, func: Callable):
        """Decorator to limit resources for a function"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            await self.check_resources()
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                if duration > self.max_time_seconds:
                    logger.warning(f"{func.__name__} took {duration:.1f}s (limit: {self.max_time_seconds}s)")
                
                return result
                
            except Exception as e:
                logger.error(f"Error in resource-limited function {func.__name__}: {e}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            # For sync functions, we can't do async resource checks
            return func

# Batch processing utilities
async def process_in_batches(
    items: list,
    batch_size: int,
    process_func: Callable,
    delay_between_batches: float = 0.1
):
    """
    Process items in batches to avoid overwhelming resources
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        process_func: Async function to process each batch
        delay_between_batches: Delay in seconds between batches
    
    Returns:
        List of results from all batches
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        try:
            batch_results = await process_func(batch)
            results.extend(batch_results)
            
            # Small delay to avoid overwhelming the system
            if i + batch_size < len(items):
                await asyncio.sleep(delay_between_batches)
                
        except Exception as e:
            logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
            # Continue with next batch
    
    return results