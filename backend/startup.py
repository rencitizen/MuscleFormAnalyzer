#!/usr/bin/env python3
"""
Startup script for Railway deployment
Ensures proper environment configuration before starting the application
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check and log environment configuration"""
    logger.info("=== MuscleFormAnalyzer Backend Startup ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'not set')}")
    logger.info(f"Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Mask the URL for security
        if "@" in database_url:
            parts = database_url.split("@")
            masked = parts[0][:20] + "***@" + parts[1] if len(parts) > 1 else database_url[:30] + "..."
        else:
            masked = database_url[:30] + "..."
        logger.info(f"DATABASE_URL found: {masked}")
        
        # Check if it's trying to use local socket
        if "localhost" in database_url and "postgresql" in database_url and "@" not in database_url:
            logger.warning("DATABASE_URL appears to be using local socket connection!")
            logger.warning("This will not work on Railway. Please use a proper connection string.")
    else:
        logger.error("DATABASE_URL not found in environment variables!")
        
        # Check for individual PG variables
        pg_vars = {
            "PGHOST": os.getenv("PGHOST"),
            "PGPORT": os.getenv("PGPORT"),
            "PGDATABASE": os.getenv("PGDATABASE"),
            "PGUSER": os.getenv("PGUSER"),
            "PGPASSWORD": os.getenv("PGPASSWORD", "***" if os.getenv("PGPASSWORD") else None)
        }
        
        logger.info("Checking individual PostgreSQL variables:")
        for var, value in pg_vars.items():
            logger.info(f"  {var}: {value if var != 'PGPASSWORD' else '***' if value else 'not set'}")
        
        # Try to construct DATABASE_URL if all variables are present
        if all(v for k, v in pg_vars.items() if k != "PGPASSWORD"):
            password = os.getenv("PGPASSWORD")
            if password:
                constructed_url = f"postgresql://{pg_vars['PGUSER']}:{password}@{pg_vars['PGHOST']}:{pg_vars['PGPORT']}/{pg_vars['PGDATABASE']}"
                os.environ["DATABASE_URL"] = constructed_url
                logger.info("DATABASE_URL constructed from individual variables and set in environment")

def start_server():
    """Start the FastAPI server"""
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    # Run uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    check_environment()
    start_server()