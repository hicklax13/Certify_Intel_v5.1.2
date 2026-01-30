#!/bin/bash
# ============================================================
# Certify Intel - One-Click Launcher
# Works on macOS (Apple Silicon M1/M2/M3/M4 and Intel)
# ============================================================

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "============================================================"
echo "  Certify Intel v5.1.2 - Starting..."
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR"

# Check if .env exists, create if not
if [ ! -f ".env" ]; then
    echo "Creating default configuration..."
    cat > .env << 'EOF'
SECRET_KEY=certify-intel-production-secret-key-2026-MSFWINTERCLINIC
ADMIN_EMAIL=admin@certifyintel.com
ADMIN_PASSWORD=MSFWINTERCLINIC2026
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./certify_intel.db
EOF
fi

# Check and install dependencies if needed
echo "Checking dependencies..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "Installing required packages (first run only)..."
    pip3 install fastapi uvicorn sqlalchemy python-jose passlib python-multipart aiofiles reportlab python-dotenv apscheduler httpx beautifulsoup4 --quiet
}

# Kill any existing server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo ""
echo "Starting Certify Intel server..."
echo ""

# Start the server in the background
python3 main.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if lsof -i:8000 > /dev/null 2>&1; then
    echo "============================================================"
    echo "  SERVER STARTED SUCCESSFULLY!"
    echo "============================================================"
    echo ""
    echo "  Opening browser to: http://localhost:8000"
    echo ""
    echo "  Login credentials:"
    echo "    Email:    admin@certifyintel.com"
    echo "    Password: MSFWINTERCLINIC2026"
    echo ""
    echo "============================================================"
    echo "  Press Ctrl+C to stop the server"
    echo "============================================================"
    echo ""

    # Open browser
    open http://localhost:8000

    # Wait for the server process
    wait $SERVER_PID
else
    echo "ERROR: Server failed to start."
    echo "Check the error messages above."
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi
