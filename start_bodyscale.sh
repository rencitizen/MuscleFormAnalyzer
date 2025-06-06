#!/bin/bash

echo "=========================================="
echo " BodyScale Pose Analyzer - Quick Starter"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed."
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[1/5] Setting up backend environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install minimal dependencies
echo "Installing backend dependencies..."
pip install -q flask flask-cors numpy opencv-python-headless mediapipe python-dotenv

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend configuration..."
    cat > .env << EOF
# Backend Configuration
USE_SQLITE=true
SQLITE_DB_PATH=bodyscale.db
SESSION_SECRET=dev-secret-key-change-in-production
ENV=development
LOG_LEVEL=INFO
EOF
fi

echo "[2/5] Setting up frontend environment..."

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "[ERROR] Frontend directory not found!"
    echo "Please ensure you're in the MuscleFormAnalyzer directory"
    exit 1
fi

cd frontend

# Create .env.local for demo mode if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating frontend configuration for demo mode..."
    cat > .env.local << EOF
# Demo Mode Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=demo-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=demo.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=demo-project
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=demo.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:demo

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:5000

# Enable Demo Mode
NEXT_PUBLIC_DEMO_MODE=true
EOF
fi

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a few minutes)..."
    npm install
fi

cd ..

echo "[3/5] Initializing database..."

# Initialize database with Python
python3 << EOF
import sqlite3
conn = sqlite3.connect('bodyscale.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY, user_id TEXT, date DATE, exercise TEXT, weight_kg REAL, reps INTEGER)')
cur.execute('CREATE TABLE IF NOT EXISTS user_profiles (id INTEGER PRIMARY KEY, user_id TEXT, height_cm REAL, weight_kg REAL)')
conn.commit()
conn.close()
print('Database initialized')
EOF

# Function to start backend
start_backend() {
    echo "[4/5] Starting backend server..."
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    echo "Starting backend server on http://localhost:5000"
    python app.py &
    BACKEND_PID=$!
}

# Function to start frontend
start_frontend() {
    echo "[4/5] Starting frontend server..."
    cd frontend
    echo "Starting frontend server on http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
}

# Function to stop servers
stop_servers() {
    echo ""
    echo "Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up trap to stop servers on script exit
trap stop_servers INT TERM

# Start both servers
start_backend
sleep 3
start_frontend

echo "[5/5] Setup complete!"
echo ""
echo "=========================================="
echo " BodyScale is starting up..."
echo "=========================================="
echo ""
echo " Frontend: http://localhost:3000"
echo " Backend:  http://localhost:5000"
echo ""
echo " Demo Account:"
echo " Email:    demo@example.com"
echo " Password: demo123"
echo ""
echo " Press Ctrl+C to stop all servers"
echo "=========================================="
echo ""

# Try to open browser after delay
sleep 5
if command -v open &> /dev/null; then
    # macOS
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:3000
fi

# Wait for user interrupt
while true; do
    sleep 1
done