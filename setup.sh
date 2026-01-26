#!/bin/bash
# ============================================================================
# Certify Intel - Mac/Linux Setup Script
# ============================================================================
# This script automates the installation process for Mac and Linux users.
# Run this script from inside the extracted project folder.
#
# Usage: chmod +x setup.sh && ./setup.sh
# ============================================================================

set -e  # Exit on error

echo ""
echo "============================================================"
echo "  Certify Intel - Automated Setup for Mac/Linux"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    echo -e "${RED}[ERROR] Python is not installed.${NC}"
    echo "Please install Python 3.9+ from https://www.python.org/downloads/"
    echo "Or use your package manager:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  - Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python found"
$PYTHON_CMD --version

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo ""
    echo -e "${RED}[ERROR] Cannot find 'backend' folder.${NC}"
    echo "Please run this script from inside the Certify Intel project folder."
    echo ""
    echo "Expected structure:"
    echo "  certify_intel/"
    echo "    backend/"
    echo "    frontend/"
    echo "    setup.sh  <-- Run from here"
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Project structure verified"
echo ""

# Navigate to backend
cd backend

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}[INFO]${NC} Virtual environment already exists. Skipping creation."
else
    echo "[STEP 1/5] Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}[OK]${NC} Virtual environment created"
fi

echo ""
echo "[STEP 2/5] Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}[OK]${NC} Virtual environment activated"

echo ""
echo "[STEP 3/5] Installing Python dependencies..."
echo "This may take 2-5 minutes depending on your internet connection..."
echo ""
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}[OK]${NC} Dependencies installed"

echo ""
echo "[STEP 4/5] Setting up configuration file..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}[INFO]${NC} .env file already exists. Skipping."
else
    cp .env.example .env
    echo -e "${GREEN}[OK]${NC} Configuration file created (.env)"
    echo ""
    echo -e "${YELLOW}[IMPORTANT]${NC} To enable AI features, edit backend/.env and add your API keys:"
    echo "  - OPENAI_API_KEY=your-openai-key"
    echo "  - GOOGLE_AI_API_KEY=your-gemini-key"
fi

echo ""
echo "[STEP 5/5] Installing Playwright browsers (for web scraping)..."
playwright install chromium 2>/dev/null || {
    echo -e "${YELLOW}[INFO]${NC} Playwright browser installation skipped or failed."
    echo "        Web scraping features may not work until you run:"
    echo "        playwright install chromium"
}

echo ""
echo "============================================================"
echo -e "  ${GREEN}SETUP COMPLETE!${NC}"
echo "============================================================"
echo ""
echo "To start the server, run:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Then open your browser and go to: http://localhost:8000"
echo ""
echo "Login credentials:"
echo "  Email:    admin@certifyhealth.com"
echo "  Password: certifyintel2024"
echo ""
echo "============================================================"
echo ""

# Ask if user wants to start the server now
read -p "Start the server now? (y/n): " START_NOW
if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting Certify Intel server..."
    echo "Press Ctrl+C to stop the server."
    echo ""
    python main.py
fi
