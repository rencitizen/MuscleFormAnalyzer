"""
MuscleFormAnalyzer Backend - FastAPI Main Application
Railway deployment optimized
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import os
import logging
import uvicorn
import time
from typing import Optional
from datetime import datetime

from .config import settings
from .database import engine, get_db
from ..models import user, workout, nutrition, progress
from ..api import auth, form_analysis, height_measurement, nutrition_api, progress_api, health_check
from ..api.v3 import v3_router
from .exceptions import (
    APIException,
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from .middleware import (
    RequestIDMiddleware,
    ResponseTimeMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting MuscleFormAnalyzer Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL configured: {'Yes' if settings.DATABASE_URL else 'No'}")
    
    # Check database connection first
    from .database import check_database_connection
    db_connected = check_database_connection()
    
    if db_connected:
        # Create database tables
        try:
            user.Base.metadata.create_all(bind=engine)
            workout.Base.metadata.create_all(bind=engine)
            nutrition.Base.metadata.create_all(bind=engine)
            progress.Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
    else:
        logger.warning("Database connection failed - running in degraded mode")
        logger.warning("Database-dependent features will not be available")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MuscleFormAnalyzer Backend...")

# FastAPI application initialization
app = FastAPI(
    title="MuscleFormAnalyzer API",
    description="AI-powered fitness form analysis and nutrition management system",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MuscleFormAnalyzer Backend API",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

# Remove duplicate health check endpoints since they're now in health_check.py

# Health check router (no prefix for direct access)
app.include_router(
    health_check.router,
    tags=["Health Check"]
)

# API router registration
app.include_router(
    auth.router, 
    prefix="/api/auth", 
    tags=["Authentication"]
)

app.include_router(
    form_analysis.router, 
    prefix="/api/form", 
    tags=["Form Analysis"]
)

app.include_router(
    height_measurement.router, 
    prefix="/api/height", 
    tags=["Height Measurement"]
)

app.include_router(
    nutrition_api.router, 
    prefix="/api/nutrition", 
    tags=["Nutrition Management"]
)

app.include_router(
    progress_api.router, 
    prefix="/api/progress", 
    tags=["Progress Tracking"]
)

# V3 API router (new scientific features)
app.include_router(
    v3_router,
    tags=["V3 API"]
)

# Register exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# General exception handler for production
if settings.ENVIRONMENT == "production":
    app.add_exception_handler(Exception, general_exception_handler)

# Store environment in app state for exception handlers
app.state.environment = settings.ENVIRONMENT

# Add custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ResponseTimeMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Legacy global exception handlers (kept for backward compatibility)
@app.exception_handler(HTTPException)
async def legacy_http_exception_handler(request: Request, exc: HTTPException):
    """Legacy HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )

# Rate limiting for production
if settings.ENVIRONMENT == "production":
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Additional startup configuration"""
    logger.info(f"Starting in {settings.ENVIRONMENT} environment")
    logger.info(f"Database URL: {settings.DATABASE_URL[:20]}...")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )