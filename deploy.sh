#!/bin/bash

# Railway Deployment Script for MuscleFormAnalyzer Backend
# This script helps deploy the FastAPI backend to Railway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MuscleFormAnalyzer Railway Deployment Script${NC}"
echo "=================================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found. Please install it first:${NC}"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Railway. Please login first:${NC}"
    echo "railway login"
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI found and authenticated${NC}"

# Navigate to backend directory
cd backend

# Check for required files
echo -e "${BLUE}🔍 Checking required files...${NC}"

required_files=("Dockerfile" "requirements.txt" "app/main.py")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ Required file missing: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Found: $file${NC}"
done

# Check if .env.example exists and create .env if needed
if [[ -f ".env.example" ]] && [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  Creating .env from .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env with your production values${NC}"
fi

# Initialize Railway project if not already done
if [[ ! -f "railway.toml" ]]; then
    echo -e "${BLUE}🔧 Initializing Railway project...${NC}"
    railway init
fi

# Add PostgreSQL database if not already added
echo -e "${BLUE}🗄️  Setting up PostgreSQL database...${NC}"
railway add --database postgresql

# Deploy to Railway
echo -e "${BLUE}🚀 Deploying to Railway...${NC}"
railway up

# Get the deployment URL
echo -e "${BLUE}📋 Getting deployment information...${NC}"
RAILWAY_URL=$(railway domain)

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📍 Deployment URL:${NC} $RAILWAY_URL"
echo ""
echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo "1. Set environment variables in Railway dashboard:"
echo "   - FIREBASE_CREDENTIALS (your Firebase service account JSON)"
echo "   - SECRET_KEY (generate a secure random key)"
echo "   - CORS_ORIGINS (your frontend URLs)"
echo ""
echo "2. Update your frontend API_BASE_URL to: $RAILWAY_URL"
echo ""
echo "3. Test the deployment:"
echo "   - Health check: $RAILWAY_URL/health"
echo "   - API docs: $RAILWAY_URL/docs"
echo ""
echo -e "${GREEN}✨ Your MuscleFormAnalyzer backend is now live!${NC}"

# Return to original directory
cd ..

exit 0