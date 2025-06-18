#!/bin/bash

# Run backend tests

echo "Running MuscleFormAnalyzer Backend Tests..."
echo "========================================="

# Set test environment
export ENVIRONMENT=test
export DATABASE_URL="sqlite:///./test.db"
export FIREBASE_PROJECT_ID="test-project"

# Run pytest with coverage
python -m pytest $@

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "Coverage report generated at: htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi