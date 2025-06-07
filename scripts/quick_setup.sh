#!/bin/bash

# BodyScale Pose Analyzer - Quick Setup Script
# This script sets up the local development environment

echo "🚀 BodyScale Pose Analyzer - Quick Setup"
echo "========================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm 9 or higher."
    exit 1
fi

echo "✅ Prerequisites check passed!"
echo ""

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix-like
    source venv/bin/activate
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend && npm install && cd ..

# Copy environment file
echo "📝 Setting up environment configuration..."
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "✅ Created .env.local from template"
else
    echo "ℹ️  .env.local already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p static/videos static/analysis_results ml/data/raw ml/data/processed ml/data/synthetic logs

# Initialize database (if needed)
if [ -f init_database.py ]; then
    echo "🗄️  Initializing database..."
    python init_database.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit .env.local with your configuration"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "Happy coding! 🎉"