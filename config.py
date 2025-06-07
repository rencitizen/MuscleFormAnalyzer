"""
Configuration module for BodyScale Pose Analyzer
Loads settings from environment variables with fallback defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.local if it exists
env_path = Path('.') / '.env.local'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fall back to .env if .env.local doesn't exist
    load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # URLs
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./bodyscale_local.db')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')
    
    # File upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './static/videos')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'mp4,mov,avi,webm').split(','))
    
    # ML settings
    MODEL_MODE = os.getenv('MODEL_MODE', 'lite')
    ML_MODELS_PATH = os.getenv('ML_MODELS_PATH', './ml/models')
    ENABLE_ML_FEATURES = os.getenv('ENABLE_ML_FEATURES', 'true').lower() == 'true'
    
    # Data collection
    DATA_COLLECTION_ENABLED = os.getenv('DATA_COLLECTION_ENABLED', 'false').lower() == 'true'
    DATA_STORAGE_PATH = os.getenv('DATA_STORAGE_PATH', './ml/data')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    
    # Feature flags
    ENABLE_MEAL_ANALYSIS = os.getenv('ENABLE_MEAL_ANALYSIS', 'true').lower() == 'true'
    ENABLE_TRAINING_DATA_COLLECTION = os.getenv('ENABLE_TRAINING_DATA_COLLECTION', 'true').lower() == 'true'
    ENABLE_ADVANCED_ANALYTICS = os.getenv('ENABLE_ADVANCED_ANALYTICS', 'true').lower() == 'true'
    
    # Development settings
    AUTO_RELOAD = os.getenv('AUTO_RELOAD', 'true').lower() == 'true'
    TEMPLATES_AUTO_RELOAD = os.getenv('TEMPLATES_AUTO_RELOAD', 'true').lower() == 'true'
    SEND_FILE_MAX_AGE_DEFAULT = int(os.getenv('SEND_FILE_MAX_AGE_DEFAULT', 0))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Override with production-specific settings
    FLASK_ENV = 'production'
    SESSION_SECRET = os.getenv('SESSION_SECRET')  # Must be set in production


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///./test.db'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)