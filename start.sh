#!/bin/bash

# UK Property Valuation - Startup Script
# This script helps you get both the backend and frontend running

set -e

echo "🏠 UK Property Valuation - Startup Helper"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}✗ Python 3 not found${NC}"
  echo "Please install Python 3.9 or higher"
  exit 1
fi
echo -e "${GREEN}✓ Python found${NC}"

# Check Node
if ! command -v npm &> /dev/null; then
  echo -e "${RED}✗ npm not found${NC}"
  echo "Please install Node.js 16 or higher"
  exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"
echo ""

# Setup Backend
echo "📦 Setting up backend..."
cd backend

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  if ! python3 -m venv venv 2>/dev/null; then
    echo -e "${RED}⚠ Python venv module not found${NC}"
    echo "Installing python3-venv package..."
    if command -v sudo &> /dev/null; then
      sudo apt-get update -qq && sudo apt-get install -qq -y python3-venv
    else
      apt-get update -qq && apt-get install -qq -y python3-venv
    fi
    echo "Trying venv creation again..."
    python3 -m venv venv
  fi
fi

# Activate venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Backend setup complete${NC}"

# Check if model exists
if [ ! -f "ml/model.joblib" ]; then
  echo ""
  echo "⚠️  ML Model not found. Training model..."
  python3 ml/train_model.py
  echo -e "${GREEN}✓ Model trained${NC}"
else
  echo -e "${GREEN}✓ ML Model found${NC}"
fi

cd ..
echo ""

# Setup Frontend
echo "⚛️  Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
  echo "Installing npm dependencies (this may take a minute)..."
  npm install -q
fi
echo -e "${GREEN}✓ Frontend setup complete${NC}"

cd ..
echo ""

# Display next steps
echo -e "${YELLOW}=========================================="
echo "Setup complete! ✨"
echo "==========================================${NC}"
echo ""
echo "To start the application:"
echo ""
echo "1️⃣  Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2️⃣  Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "The app will open at http://localhost:3000"
echo ""
echo "For more help, see SETUP.md"
echo ""
