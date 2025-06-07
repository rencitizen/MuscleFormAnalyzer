@echo off
REM BodyScale Pose Analyzer - Quick Setup Script for Windows
REM This script sets up the local development environment

echo BodyScale Pose Analyzer - Quick Setup
echo =====================================

REM Check prerequisites
echo Checking prerequisites...

REM Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)

REM Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed. Please install npm 9 or higher.
    exit /b 1
)

echo Prerequisites check passed!
echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install Node dependencies
echo Installing Node.js dependencies...
npm install

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
npm install
cd ..

REM Copy environment file
echo Setting up environment configuration...
if not exist .env.local (
    copy .env.example .env.local
    echo Created .env.local from template
) else (
    echo .env.local already exists
)

REM Create necessary directories
echo Creating necessary directories...
if not exist static\videos mkdir static\videos
if not exist static\analysis_results mkdir static\analysis_results
if not exist ml\data\raw mkdir ml\data\raw
if not exist ml\data\processed mkdir ml\data\processed
if not exist ml\data\synthetic mkdir ml\data\synthetic
if not exist logs mkdir logs

REM Initialize database (if needed)
if exist init_database.py (
    echo Initializing database...
    python init_database.py
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env.local with your configuration
echo 2. Run 'npm run dev' to start the development server
echo 3. Open http://localhost:3000 in your browser
echo.
echo Happy coding!

pause