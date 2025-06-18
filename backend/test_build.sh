#!/bin/bash

# Backend build process verification

echo "🔨 Testing Backend Build Process"
echo "================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# 1. Check Python version
echo -e "\n📋 Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "   Python version: $python_version"
    print_status 0 "Python is installed"
else
    print_status 1 "Python is not installed"
fi

# 2. Check required files
echo -e "\n📋 Checking required files..."
required_files=(
    "requirements.txt"
    "app/main.py"
    "app/config.py"
    "app/database.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "Found $file"
    else
        print_status 1 "Missing $file"
    fi
done

# 3. Create virtual environment
echo -e "\n📋 Creating virtual environment..."
if [ -d "venv_test" ]; then
    rm -rf venv_test
fi

python3 -m venv venv_test
print_status $? "Virtual environment created"

# 4. Activate virtual environment and install dependencies
echo -e "\n📋 Installing dependencies..."
source venv_test/bin/activate

# Upgrade pip first
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
pip install -r requirements.txt > build_log.txt 2>&1
if [ $? -eq 0 ]; then
    print_status 0 "Dependencies installed"
else
    echo -e "${RED}Failed to install dependencies. Check build_log.txt for details${NC}"
    tail -20 build_log.txt
    exit 1
fi

# 5. Check imports
echo -e "\n📋 Checking imports..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app.main import app
    print('   ✅ Main app imports successfully')
except ImportError as e:
    print(f'   ❌ Import error: {e}')
    sys.exit(1)
"
print_status $? "Import check passed"

# 6. Check environment variables
echo -e "\n📋 Checking environment configuration..."
python3 -c "
import os
os.environ['ENVIRONMENT'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
from app.config import settings
print(f'   Environment: {settings.ENVIRONMENT}')
print(f'   Database URL: {settings.DATABASE_URL[:20]}...')
"
print_status $? "Environment configuration works"

# 7. Test database initialization
echo -e "\n📋 Testing database initialization..."
python3 -c "
import os
os.environ['ENVIRONMENT'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///./test_build.db'
from app.database import engine, Base
from models.user import User
from models.workout import Exercise
from models.nutrition import Food
from models.progress import Goal
try:
    Base.metadata.create_all(bind=engine)
    print('   ✅ Database tables created')
except Exception as e:
    print(f'   ❌ Database error: {e}')
    import sys
    sys.exit(1)
"
print_status $? "Database initialization successful"

# 8. Test API startup (dry run)
echo -e "\n📋 Testing API startup..."
timeout 5s python3 -c "
import os
os.environ['ENVIRONMENT'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///./test_build.db'
from app.main import app
print('   ✅ FastAPI app initialized')
" 2>&1 | grep -v "INFO"
print_status $? "API startup test passed"

# 9. Check for syntax errors
echo -e "\n📋 Checking for syntax errors..."
python3 -m py_compile app/*.py api/*.py models/*.py services/*.py 2>&1 | grep -E "SyntaxError|Error"
if [ ${PIPESTATUS[0]} -eq 0 ] && [ ${PIPESTATUS[1]} -eq 1 ]; then
    print_status 0 "No syntax errors found"
else
    print_status 1 "Syntax errors detected"
fi

# 10. Generate requirements freeze
echo -e "\n📋 Generating requirements freeze..."
pip freeze > requirements_freeze.txt
print_status $? "Requirements freeze generated"

# Cleanup
echo -e "\n🧹 Cleaning up..."
deactivate
rm -rf venv_test
rm -f test_build.db build_log.txt

echo -e "\n${GREEN}✅ Build process verification completed successfully!${NC}"
echo -e "\n📊 Build Summary:"
echo "   - Python version: OK"
echo "   - Required files: OK"
echo "   - Dependencies: OK"
echo "   - Import checks: OK"
echo "   - Database: OK"
echo "   - API startup: OK"
echo "   - Syntax: OK"

echo -e "\n📋 Next steps for deployment:"
echo "   1. Set production environment variables"
echo "   2. Configure production database"
echo "   3. Set up reverse proxy (nginx/Apache)"
echo "   4. Configure SSL certificates"
echo "   5. Set up process manager (systemd/supervisor)"
echo "   6. Enable monitoring and logging"