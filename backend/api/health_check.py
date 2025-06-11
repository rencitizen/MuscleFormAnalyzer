"""
Health check and diagnostic endpoints for Railway deployment
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import text

from ..app.database import engine, get_db, check_database_connection
from ..app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "MuscleFormAnalyzer Backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Check database connection
    try:
        db_connected = check_database_connection()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_connected else "unhealthy",
            "type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "error": str(e)[:100]
        }
        health_status["status"] = "degraded"
    
    # Check ML models (if applicable)
    try:
        # Add ML model checks here if needed
        health_status["checks"]["ml_models"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["ml_models"] = {
            "status": "error",
            "error": str(e)[:100]
        }
    
    # Overall status
    if any(check.get("status") != "healthy" for check in health_status["checks"].values()):
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)

@router.get("/debug/env")
async def debug_environment():
    """Debug endpoint to check environment variables (disable in production)"""
    if settings.ENVIRONMENT == "production":
        return {"message": "Debug endpoint disabled in production"}
    
    env_info = {
        "environment": settings.ENVIRONMENT,
        "database_configured": bool(settings.DATABASE_URL),
        "environment_variables": {}
    }
    
    # Check database-related environment variables
    db_vars = ["DATABASE_URL", "PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "RAILWAY_ENVIRONMENT"]
    for var in db_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive information
            if var in ["DATABASE_URL", "PGPASSWORD"]:
                masked = value[:10] + "***" + value[-10:] if len(value) > 20 else "***"
                env_info["environment_variables"][var] = masked
            else:
                env_info["environment_variables"][var] = value
        else:
            env_info["environment_variables"][var] = None
    
    return env_info

@router.get("/debug/database")
async def debug_database():
    """Debug database connection details"""
    if settings.ENVIRONMENT == "production":
        return {"message": "Debug endpoint disabled in production"}
    
    debug_info = {
        "database_url_configured": bool(settings.DATABASE_URL),
        "database_type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite",
        "connection_test": False,
        "error": None,
        "engine_info": {}
    }
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            debug_info["connection_test"] = True
            debug_info["database_version"] = version
            
        # Engine information
        debug_info["engine_info"] = {
            "pool_size": getattr(engine.pool, "size", "N/A"),
            "checked_in": getattr(engine.pool, "checkedin", lambda: "N/A")(),
            "checked_out": getattr(engine.pool, "checkedout", lambda: "N/A")(),
            "dialect": engine.dialect.name
        }
        
    except Exception as e:
        debug_info["error"] = {
            "type": type(e).__name__,
            "message": str(e),
            "details": {
                "local_socket_error": "/var/run/postgresql/" in str(e),
                "connection_refused": "Connection refused" in str(e),
                "authentication_failed": "authentication failed" in str(e)
            }
        }
    
    return debug_info

@router.get("/ready")
async def ready_check():
    """Simple readiness probe for Railway"""
    return {"ready": True, "timestamp": datetime.utcnow().isoformat()}

@router.get("/live")
async def liveness_check():
    """Simple liveness probe"""
    return {"alive": True, "timestamp": datetime.utcnow().isoformat()}