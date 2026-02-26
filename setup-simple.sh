#!/bin/bash

# Simple setup without venv (for systems where venv isn't available)

set -e

echo "🏠 UK Property Valuation - Simple Setup"
echo "========================================"
echo ""

# Check Python and Node
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
  echo "❌ Python 3 not found"
  exit 1
fi
echo "✓ Python 3 found"

if ! command -v npm &> /dev/null; then
  echo "❌ npm not found"
  exit 1
fi
echo "✓ npm found"
echo ""

# Check if python3-venv exists
echo "📦 Checking venv availability..."
if ! python3 -m venv --help &> /dev/null 2>&1; then
  echo ""
  echo "⚠️  Python venv module is not installed!"
  echo ""
  echo "Please run this command first:"
  echo "  sudo apt-get install -y python3.12-venv"
  echo ""
  echo "Then run this script again."
  exit 1
fi
echo "✓ venv module available"
echo ""

# Setup backend
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

if [ ! -f "ml/model.joblib" ]; then
  echo "Training ML model (this may take ~30 seconds)..."
  python3 ml/train_model.py
  echo "✓ Model trained"
else
  echo "✓ Model already exists"
fi

cd ..
echo ""

# Setup frontend
echo "⚛️  Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
  echo "Installing npm dependencies (this may take a minute)..."
  npm install -q
fi

cd ..
echo ""

# Done!
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "1️⃣  Start backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2️⃣  Start frontend (in another terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "Then open http://localhost:3000 in your browser!"
echo ""
