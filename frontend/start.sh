#!/bin/bash
# Startup script for LimbGuard-Cortex Frontend Application
# This script starts both the backend API server and the React frontend

set -e

echo "🚀 Starting LimbGuard-Cortex Frontend Application..."
echo ""

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: This script must be run from the frontend/ directory"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    echo ""
fi

# Check backend dependencies
PYTHON_CMD=$(command -v python3 || command -v python)
if ! $PYTHON_CMD -c "import fastapi" &> /dev/null; then
    echo "📦 Installing Python dependencies..."
    cd api
    pip install -r requirements.txt
    cd ..
    
    # Install main project dependencies
    echo "📦 Installing main project dependencies..."
    cd ..
    pip install -r requirements.txt
    cd frontend
    echo ""
fi

# Start backend in background
echo "🔧 Starting backend API server on port 8000..."
cd api
$PYTHON_CMD server.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend API server started successfully"
else
    echo "⚠️  Backend may not have started. Check the logs above."
fi

echo ""
echo "🌐 Starting React frontend on port 3000..."
echo ""
echo "📝 Note: The frontend will open automatically in your browser."
echo "📝 To stop both servers, press Ctrl+C"
echo ""

# Trap to kill backend when script exits
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID 2>/dev/null; exit" INT TERM

# Start frontend (this will block)
npm start

# If we get here, frontend exited, so kill backend
kill $BACKEND_PID 2>/dev/null
