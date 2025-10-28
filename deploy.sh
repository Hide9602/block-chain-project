#!/bin/bash

# MetaSleuth NextGen - One-Click Deployment Script
# This script guides you through deploying to Vercel + Railway

set -e

echo "🚀 MetaSleuth NextGen Deployment Script"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"
echo ""

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git is installed${NC}"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo -e "${RED}✗ Please run this script from the project root directory${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Current directory is correct${NC}"

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠ You have uncommitted changes${NC}"
    read -p "Do you want to commit them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
        git push origin main
        echo -e "${GREEN}✓ Changes committed and pushed${NC}"
    else
        echo -e "${YELLOW}⚠ Proceeding with uncommitted changes${NC}"
    fi
else
    echo -e "${GREEN}✓ No uncommitted changes${NC}"
fi

echo ""
echo -e "${GREEN}All prerequisites met!${NC}"
echo ""

# Step 2: Railway deployment
echo "========================================"
echo -e "${BLUE}Step 2: Deploy Backend to Railway${NC}"
echo "========================================"
echo ""
echo "1. Open Railway: ${YELLOW}https://railway.app${NC}"
echo "2. Click 'Login With GitHub'"
echo "3. Click 'New Project'"
echo "4. Select 'Deploy from GitHub repo'"
echo "5. Choose: ${YELLOW}Hide9602/block-chain-project${NC}"
echo "6. Railway will automatically detect the configuration"
echo ""
echo "7. Add PostgreSQL:"
echo "   - Click 'New' → 'Database' → 'Add PostgreSQL'"
echo ""
echo "8. Add Redis:"
echo "   - Click 'New' → 'Database' → 'Add Redis'"
echo ""
echo "9. Set environment variables:"
echo "   - Click on your service → 'Variables' tab"
echo "   - Add the following:"
echo ""
echo "   ${YELLOW}SECRET_KEY${NC}=<generate with: openssl rand -hex 32>"
echo "   ${YELLOW}ENVIRONMENT${NC}=production"
echo "   ${YELLOW}CORS_ORIGINS${NC}=* (we'll update this later)"
echo ""
echo "10. Wait for deployment to complete (~2 minutes)"
echo ""
echo "11. Get your Railway URL:"
echo "    - Click 'Settings' → 'Generate Domain'"
echo "    - Copy the URL (e.g., https://your-app.railway.app)"
echo ""

read -p "Press Enter when Railway deployment is complete and you have the URL..."
echo ""

read -p "Enter your Railway backend URL: " railway_url

if [ -z "$railway_url" ]; then
    echo -e "${RED}✗ Railway URL is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Railway URL recorded: $railway_url${NC}"
echo ""

# Step 3: Vercel deployment
echo "========================================"
echo -e "${BLUE}Step 3: Deploy Frontend to Vercel${NC}"
echo "========================================"
echo ""
echo "1. Open Vercel: ${YELLOW}https://vercel.com/new${NC}"
echo "2. Click 'Continue with GitHub'"
echo "3. Import 'Hide9602/block-chain-project'"
echo "4. Configure project:"
echo ""
echo "   ${YELLOW}Framework Preset${NC}: Next.js"
echo "   ${YELLOW}Root Directory${NC}: frontend"
echo "   ${YELLOW}Build Command${NC}: npm run build"
echo "   ${YELLOW}Output Directory${NC}: .next"
echo "   ${YELLOW}Install Command${NC}: npm install"
echo ""
echo "5. Add Environment Variable:"
echo ""
echo "   ${YELLOW}Name${NC}:  NEXT_PUBLIC_API_URL"
echo "   ${YELLOW}Value${NC}: $railway_url"
echo ""
echo "6. Click 'Deploy'"
echo "7. Wait for deployment (~2-3 minutes)"
echo ""

read -p "Press Enter when Vercel deployment is complete and you have the URL..."
echo ""

read -p "Enter your Vercel frontend URL: " vercel_url

if [ -z "$vercel_url" ]; then
    echo -e "${RED}✗ Vercel URL is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Vercel URL recorded: $vercel_url${NC}"
echo ""

# Step 4: Update CORS
echo "========================================"
echo -e "${BLUE}Step 4: Update CORS Configuration${NC}"
echo "========================================"
echo ""
echo "Return to Railway:"
echo "1. Go to your Railway project"
echo "2. Click on backend service → 'Variables'"
echo "3. Update ${YELLOW}CORS_ORIGINS${NC}:"
echo ""
echo "   ${YELLOW}Old value${NC}: *"
echo "   ${YELLOW}New value${NC}: $vercel_url"
echo ""
echo "4. Save (will auto-redeploy)"
echo ""

read -p "Press Enter when CORS is updated..."
echo ""

# Step 5: Test deployment
echo "========================================"
echo -e "${BLUE}Step 5: Testing Deployment${NC}"
echo "========================================"
echo ""

echo "Testing backend health..."
if curl -f -s "${railway_url}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend health check failed (this is okay if /health endpoint doesn't exist)${NC}"
fi

echo ""
echo "Testing frontend..."
if curl -f -s -I "$vercel_url" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend is not accessible${NC}"
fi

echo ""

# Step 6: Summary
echo "========================================"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "========================================"
echo ""
echo "Your MetaSleuth NextGen is now live!"
echo ""
echo "📍 Frontend: ${YELLOW}$vercel_url${NC}"
echo "📍 Backend:  ${YELLOW}$railway_url${NC}"
echo "📍 API Docs: ${YELLOW}${railway_url}/docs${NC}"
echo ""
echo "Next steps:"
echo "1. Visit your frontend URL to test"
echo "2. Try searching for an address"
echo "3. Test language switching (🌐 button)"
echo "4. Check all 4 tabs (Graph, Patterns, Risk, AI Report)"
echo ""
echo "📚 Documentation:"
echo "- Deployment Guide: DEPLOYMENT.md"
echo "- Quick Guide: DEPLOY_NOW.md"
echo "- Project README: README.md"
echo ""
echo -e "${GREEN}Happy investigating! 🔍🚀${NC}"
echo ""

# Save URLs to file
cat > deployment-urls.txt << EOF
# MetaSleuth NextGen - Deployment URLs
# Generated: $(date)

Frontend: $vercel_url
Backend: $railway_url
API Docs: ${railway_url}/docs

# Environment Variables Used
NEXT_PUBLIC_API_URL=$railway_url
CORS_ORIGINS=$vercel_url

# To update CORS in Railway:
# 1. Go to Railway dashboard
# 2. Select backend service
# 3. Go to Variables tab
# 4. Update CORS_ORIGINS
EOF

echo -e "${GREEN}✓ Deployment URLs saved to: deployment-urls.txt${NC}"
echo ""
