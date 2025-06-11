#!/usr/bin/env python3
"""
Test script to verify database connection for Railway deployment
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection with detailed diagnostics"""
    logger.info("=== Database Connection Test ===")
    
    # Check environment variables
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment!")
        
        # Check individual PG variables
        pg_vars = {
            "PGHOST": os.getenv("PGHOST"),
            "PGPORT": os.getenv("PGPORT", "5432"),
            "PGDATABASE": os.getenv("PGDATABASE"),
            "PGUSER": os.getenv("PGUSER"),
            "PGPASSWORD": os.getenv("PGPASSWORD")
        }
        
        if all(pg_vars.values()):
            database_url = f"postgresql://{pg_vars['PGUSER']}:{pg_vars['PGPASSWORD']}@{pg_vars['PGHOST']}:{pg_vars['PGPORT']}/{pg_vars['PGDATABASE']}"
            logger.info("Constructed DATABASE_URL from individual variables")
        else:
            logger.error("Neither DATABASE_URL nor complete PG variables found!")
            return False
    
    # Mask the URL for logging
    masked_url = database_url[:20] + "***" + database_url[-20:] if len(database_url) > 40 else "***"
    logger.info(f"DATABASE_URL: {masked_url}")
    
    # Handle Railway PostgreSQL URL format
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        logger.info("Converted to SQLAlchemy format")
    
    # Add SSL for Railway
    if "railway.app" in database_url and "sslmode" not in database_url:
        separator = "?" if "?" not in database_url else "&"
        database_url += f"{separator}sslmode=require"
        logger.info("Added SSL mode for Railway")
    
    # Test connection
    try:
        logger.info("Creating engine...")
        engine = create_engine(database_url, echo=True)
        
        logger.info("Testing connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Connection successful!")
            logger.info(f"Database version: {version}")
            
            # Test if we can create tables
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            logger.info(f"Connected to database: {db_name} as user: {user}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed!")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        
        # Specific error diagnostics
        error_str = str(e)
        if "/var/run/postgresql/" in error_str:
            logger.error("PROBLEM: Attempting to connect to local PostgreSQL socket!")
            logger.error("This indicates DATABASE_URL is not being read correctly.")
        elif "Connection refused" in error_str:
            logger.error("PROBLEM: Connection refused - check host and port")
        elif "authentication failed" in error_str:
            logger.error("PROBLEM: Authentication failed - check username and password")
        elif "database" in error_str and "does not exist" in error_str:
            logger.error("PROBLEM: Database does not exist")
        
        return False

if __name__ == "__main__":
    # Load settings if available
    try:
        from backend.app.config import settings
        logger.info(f"Settings loaded - Environment: {settings.ENVIRONMENT}")
    except ImportError:
        logger.warning("Could not import settings")
    
    success = test_connection()
    sys.exit(0 if success else 1)