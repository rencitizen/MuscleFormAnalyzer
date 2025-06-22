"""
API Performance Monitoring Endpoints
For internal monitoring and optimization
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timedelta

from ..utils.performance import perf_monitor, profile_memory, optimize_memory
from ..api.auth import get_current_user
from ..models.user import User
from ..services.cache_service import CacheService

router = APIRouter()

@router.get("/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    Get API performance metrics
    Only accessible to admin users
    """
    # Check if user is admin (you might want to add an is_admin field to User model)
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    metrics = perf_monitor.get_metrics_summary()
    memory = profile_memory()
    
    return {
        "performance": metrics,
        "memory": memory,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/detailed")
async def get_detailed_health():
    """
    Get detailed health status of the API
    """
    memory = profile_memory()
    
    # Check if memory usage is high
    memory_status = "healthy"
    if memory["percent"] > 80:
        memory_status = "critical"
    elif memory["percent"] > 60:
        memory_status = "warning"
    
    return {
        "status": "healthy",
        "memory_status": memory_status,
        "memory": {
            "used_mb": memory["rss"],
            "percent": memory["percent"],
            "available_mb": memory["available"]
        },
        "uptime": {
            "started_at": "2024-01-01T00:00:00Z",  # You'd track this properly
            "uptime_seconds": 3600  # Calculate from actual start time
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/optimize/memory")
async def optimize_api_memory(
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger memory optimization
    Only accessible to admin users
    """
    # Check if user is admin
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = optimize_memory()
    
    return {
        "success": True,
        "optimization_result": result,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/cache/stats")
async def get_cache_statistics(
    current_user: User = Depends(get_current_user),
    request = None
):
    """
    Get cache statistics
    Only accessible to admin users
    """
    # Check if user is admin
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cache_service = getattr(request.app.state, 'cache_service', None) if request else None
    
    if not cache_service or not cache_service.redis_client:
        return {
            "cache_enabled": False,
            "message": "Cache service not available"
        }
    
    try:
        # Get Redis info
        info = cache_service.redis_client.info()
        
        return {
            "cache_enabled": True,
            "stats": {
                "used_memory_mb": info.get("used_memory", 0) / 1024 / 1024,
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)),
                "evicted_keys": info.get("evicted_keys", 0),
                "total_keys": sum(int(db.split("=")[1].split(",")[0]) for db in info.keys() if db.startswith("db"))
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "cache_enabled": True,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    request = None
):
    """
    Clear cache entries
    Only accessible to admin users
    """
    # Check if user is admin
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cache_service = getattr(request.app.state, 'cache_service', None) if request else None
    
    if not cache_service or not cache_service.redis_client:
        return {
            "success": False,
            "message": "Cache service not available"
        }
    
    try:
        if pattern:
            # Clear specific pattern
            cleared = cache_service.clear_pattern(f"cache:{pattern}*")
            message = f"Cleared {cleared} keys matching pattern: {pattern}"
        else:
            # Clear all cache keys
            cleared = cache_service.clear_pattern("cache:*")
            message = f"Cleared {cleared} cache keys"
        
        return {
            "success": True,
            "message": message,
            "keys_cleared": cleared,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }