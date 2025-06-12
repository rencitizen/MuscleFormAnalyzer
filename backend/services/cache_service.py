"""
Redis caching service for performance optimization
"""
import json
import redis
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service"""
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        Initialize cache service
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client = None
        
        if redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_keepalive_options={
                        1: 1,  # TCP_KEEPIDLE
                        2: 1,  # TCP_KEEPINTVL
                        3: 3,  # TCP_KEEPCNT
                    }
                )
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Running without cache.")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
            
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
            
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False
            
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return 0
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
        
        return 0
    
    @staticmethod
    def make_key(*args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)
        
        # Hash long keys
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"cache:{key_hash}"
        
        return f"cache:{key_string}"

def cached(ttl: Optional[int] = None, key_prefix: Optional[str] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Optional prefix for cache key
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get cache service from app state or create dummy
            cache_service = getattr(args[0], 'cache_service', None) if args else None
            
            if not cache_service or not cache_service.redis_client:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            cache_key_parts.extend([str(arg) for arg in args[1:]])  # Skip self
            cache_key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = CacheService.make_key(*cache_key_parts)
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_service.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get cache service from app state or create dummy
            cache_service = getattr(args[0], 'cache_service', None) if args else None
            
            if not cache_service or not cache_service.redis_client:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            cache_key_parts.extend([str(arg) for arg in args[1:]])  # Skip self
            cache_key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = CacheService.make_key(*cache_key_parts)
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_service.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator