"""
Configuration settings for MuscleFormAnalyzer Backend
"""
import os
from typing import List
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database - with multiple fallback options
    DATABASE_URL: str = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PRIVATE_URL") or "sqlite:///./muscle_analyzer.db"
    
    # Railway-specific database URLs (fallback)
    PGHOST: str = os.getenv("PGHOST", "")
    PGPORT: str = os.getenv("PGPORT", "5432")
    PGDATABASE: str = os.getenv("PGDATABASE", "")
    PGUSER: str = os.getenv("PGUSER", "")
    PGPASSWORD: str = os.getenv("PGPASSWORD", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "https://muscle-form-analyzer.vercel.app",
        "https://muscle-form-analyzer-*.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001"
    ]
    
    # Trusted hosts for Railway
    ALLOWED_HOSTS: List[str] = [
        "*.railway.app",
        "*.up.railway.app", 
        "localhost",
        "127.0.0.1"
    ]
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "50")) * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # MediaPipe Settings
    MEDIAPIPE_MODEL_COMPLEXITY: int = int(os.getenv("MEDIAPIPE_MODEL_COMPLEXITY", "1"))
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE: float = float(os.getenv("MEDIAPIPE_MIN_DETECTION_CONFIDENCE", "0.7"))
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE: float = float(os.getenv("MEDIAPIPE_MIN_TRACKING_CONFIDENCE", "0.7"))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Redis (for caching and rate limiting)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v, values):
        """Validate and transform database URL for Railway PostgreSQL"""
        # If DATABASE_URL is not set but individual PG variables are, construct it
        if v == "sqlite:///./muscle_analyzer.db" and values.get("PGHOST"):
            host = values.get("PGHOST")
            port = values.get("PGPORT", "5432")
            database = values.get("PGDATABASE")
            user = values.get("PGUSER")
            password = values.get("PGPASSWORD")
            
            if all([host, database, user, password]):
                v = f"postgresql://{user}:{password}@{host}:{port}/{database}"
                print(f"Constructed DATABASE_URL from individual PG variables")
        
        # Railway uses postgresql:// but SQLAlchemy needs postgresql+psycopg2://
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        
        # Add SSL mode for Railway PostgreSQL
        if "railway.app" in v and "sslmode" not in v:
            separator = "?" if "?" not in v else "&"
            v += f"{separator}sslmode=require"
        
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from environment variable"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": settings.LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}