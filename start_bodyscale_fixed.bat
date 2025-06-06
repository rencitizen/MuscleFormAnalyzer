@echo off
chcp 65001 >nul
echo ==========================================
echo  BodyScale Pose Analyzer - Quick Starter
echo ==========================================
echo.

REM Change to the correct directory
cd /d "C:\Users\Owner\MuscleFormAnalyzer"
echo Working directory: %CD%
echo.

REM Check for Python3 first, then Python
where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    echo Found Python as: python3
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
        echo Found Python as: python
    ) else (
        echo [ERROR] Python is not installed or not in PATH
        echo Please install Python 3.8+ from https://python.org
        pause
        exit /b 1
    )
)

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)
echo Found Node.js
echo.

echo [1/5] Setting up backend environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing backend dependencies...
call venv\Scripts\activate.bat
pip install flask flask-cors numpy opencv-python-headless mediapipe python-dotenv

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating backend configuration...
    (
        echo # Backend Configuration
        echo USE_SQLITE=true
        echo SQLITE_DB_PATH=bodyscale.db
        echo SESSION_SECRET=dev-secret-key-change-in-production
        echo ENV=development
        echo LOG_LEVEL=INFO
    ) > .env
)

echo [2/5] Setting up frontend environment...

REM Check if frontend directory exists
if not exist "frontend" (
    echo [ERROR] Frontend directory not found!
    echo Current directory: %CD%
    dir
    pause
    exit /b 1
)

cd frontend

REM Create .env.local for demo mode if it doesn't exist
if not exist ".env.local" (
    echo Creating frontend configuration for demo mode...
    (
        echo # Demo Mode Configuration
        echo NEXT_PUBLIC_FIREBASE_API_KEY=demo-api-key
        echo NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=demo.firebaseapp.com
        echo NEXT_PUBLIC_FIREBASE_PROJECT_ID=demo-project
        echo NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=demo.appspot.com
        echo NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
        echo NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:demo
        echo.
        echo # Backend API
        echo NEXT_PUBLIC_API_URL=http://localhost:5000
        echo.
        echo # Enable Demo Mode
        echo NEXT_PUBLIC_DEMO_MODE=true
    ) > .env.local
)

REM Install frontend dependencies
if not exist "node_modules" (
    echo Installing frontend dependencies (this may take a few minutes)...
    npm install
)

cd ..

echo [3/5] Initializing database...

REM Initialize database
venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('bodyscale.db'); cur = conn.cursor(); cur.execute('CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY, user_id TEXT, date DATE, exercise TEXT, weight_kg REAL, reps INTEGER)'); cur.execute('CREATE TABLE IF NOT EXISTS user_profiles (id INTEGER PRIMARY KEY, user_id TEXT, height_cm REAL, weight_kg REAL)'); conn.commit(); conn.close(); print('Database initialized')"

echo [4/5] Starting servers...

REM Start backend server
echo Starting backend server on http://localhost:5000
start "BodyScale Backend" cmd /k "cd /d C:\Users\Owner\MuscleFormAnalyzer && venv\Scripts\activate && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo Starting frontend server on http://localhost:3000
start "BodyScale Frontend" cmd /k "cd /d C:\Users\Owner\MuscleFormAnalyzer\frontend && npm run dev"

echo [5/5] Setup complete!
echo.
echo ==========================================
echo  BodyScale is starting up...
echo ==========================================
echo.
echo  Frontend: http://localhost:3000
echo  Backend:  http://localhost:5000
echo.
echo  Demo Account:
echo  Email:    demo@example.com
echo  Password: demo123
echo.
echo  Press any key to open browser...
echo ==========================================
pause

REM Open browser
start http://localhost:3000