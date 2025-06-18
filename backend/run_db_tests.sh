#!/bin/bash

# Run database tests

echo "Running Database Connection and Operation Tests..."
echo "================================================"

# Set test environment
export ENVIRONMENT=test
export DATABASE_URL="sqlite:///./test_operations.db"

# Run pytest for database tests
echo ""
echo "1. Running pytest database tests..."
python -m pytest tests/test_database.py -v

# Check if pytest succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database tests passed!"
else
    echo ""
    echo "❌ Some database tests failed!"
fi

# Clean up test database
if [ -f "test_operations.db" ]; then
    rm test_operations.db
    echo "Test database cleaned up"
fi