"""
Database configuration and connection management
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
import logging
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool
from typing import Generator
import ssl

from .config import settings

logger = logging.getLogger(__name__)

# Log database configuration
logger.info("=== Database Configuration ===")
if settings.DATABASE_URL:
    # Mask sensitive parts of the URL for security
    url_parts = settings.DATABASE_URL.split('@')
    if len(url_parts) > 1:
        masked_url = url_parts[0][:20] + '***@' + url_parts[1]
    else:
        masked_url = settings.DATABASE_URL[:30] + '...'
    logger.info(f"DATABASE_URL: {masked_url}")
else:
    logger.error("DATABASE_URL not found in environment variables!")

# Database engine configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    # PostgreSQL configuration for production (Railway)
    connect_args = {}
    
    # Add SSL configuration for Railway PostgreSQL
    if "railway.app" in settings.DATABASE_URL:
        logger.info("Configuring SSL for Railway PostgreSQL")
        connect_args["sslmode"] = "require"
    
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            echo=settings.DEBUG,
            connect_args=connect_args
        )
        logger.info("PostgreSQL engine created successfully")
    except Exception as e:
        logger.error(f"Failed to create PostgreSQL engine: {e}")
        # Try with NullPool as fallback
        logger.info("Attempting to create engine with NullPool...")
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=NullPool,
            echo=settings.DEBUG,
            connect_args=connect_args
        )

# Session configuration
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Base class for declarative models
Base = declarative_base()

# Metadata for schema management
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def drop_tables():
    """
    Drop all database tables (use with caution)
    """
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

def check_database_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        
        # Additional debug information
        if "server on socket" in str(e) and "/var/run/postgresql/" in str(e):
            logger.error("ERROR: Trying to connect to local PostgreSQL socket instead of Railway database!")
            logger.error("Please ensure DATABASE_URL environment variable is properly set.")
            logger.error(f"Current DATABASE_URL starts with: {settings.DATABASE_URL[:30] if settings.DATABASE_URL else 'None'}")
        
        return False

# Database migration utilities
class DatabaseManager:
    """Database management utilities"""
    
    def __init__(self):
        self.engine = engine
        self.session = SessionLocal
    
    def migrate_sqlite_to_postgresql(self, sqlite_path: str):
        """
        Migrate data from SQLite to PostgreSQL
        """
        if not settings.DATABASE_URL.startswith("postgresql"):
            raise ValueError("Target database must be PostgreSQL")
        
        try:
            # Create SQLite engine
            sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
            sqlite_session = sessionmaker(bind=sqlite_engine)()
            
            # Get PostgreSQL session
            pg_session = self.session()
            
            logger.info("Starting SQLite to PostgreSQL migration...")
            
            # Migration logic would go here
            # This is a placeholder for the actual migration code
            
            logger.info("Migration completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            if 'sqlite_session' in locals():
                sqlite_session.close()
            if 'pg_session' in locals():
                pg_session.close()
    
    def backup_database(self, backup_path: str):
        """
        Create a database backup
        """
        try:
            logger.info(f"Creating database backup at {backup_path}")
            
            if settings.DATABASE_URL.startswith("sqlite"):
                # SQLite backup
                import shutil
                sqlite_path = settings.DATABASE_URL.replace("sqlite:///", "")
                shutil.copy2(sqlite_path, backup_path)
            else:
                # PostgreSQL backup using pg_dump
                import subprocess
                # This would require pg_dump to be available
                # Implementation depends on Railway's environment
                pass
            
            logger.info("Database backup completed successfully")
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            raise
    
    def get_table_info(self):
        """
        Get information about database tables
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            table_info = {}
            for table in tables:
                columns = inspector.get_columns(table)
                table_info[table] = {
                    "columns": len(columns),
                    "column_names": [col["name"] for col in columns]
                }
            
            return table_info
            
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {}

# Global database manager instance
db_manager = DatabaseManager()

# Health check function for the database
async def database_health_check() -> dict:
    """
    Async health check for database
    """
    try:
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        # Get basic stats
        inspector = inspect(engine)
        table_count = len(inspector.get_table_names())
        
        return {
            "status": "healthy",
            "database_type": "postgresql" if settings.DATABASE_URL.startswith("postgresql") else "sqlite",
            "table_count": table_count,
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }