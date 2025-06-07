#!/usr/bin/env python3
"""
Local development launcher for BodyScale Pose Analyzer
This file configures the app for hot-reload and local development
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the main app with config
from app import app
from config import get_config

# Apply configuration
config = get_config()
app.config.from_object(config)

# Override CORS for local development
from flask_cors import CORS
CORS(app, 
     origins=config.CORS_ORIGINS,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Enable hot reload
app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == '__main__':
    # Get settings from config
    host = config.HOST
    port = config.PORT
    debug = config.FLASK_DEBUG
    
    print(f"Starting BodyScale Pose Analyzer in {config.FLASK_ENV} mode")
    print(f"Backend URL: http://{host}:{port}")
    print(f"Frontend URL: {config.FRONTEND_URL}")
    print(f"Debug mode: {debug}")
    print(f"Hot reload: Enabled")
    print("\nPress Ctrl+C to stop the server")
    
    # Run with hot reload
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=True,
        use_debugger=debug,
        threaded=True
    )