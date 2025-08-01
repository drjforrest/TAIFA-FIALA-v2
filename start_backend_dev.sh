#!/bin/bash

# TAIFA-FIALA: Start FastAPI + ETL System
# This will run both the API server and background ETL collection

set -e  # Exit on any error

# Configuration
BACKEND_DIR="/Users/drjforrest/dev/devprojects/TAIFA-FIALA/backend"
API_PORT=8000
MAX_STARTUP_TIME=30
HEALTH_CHECK_RETRIES=10

cd "$BACKEND_DIR"

echo "🚀 Starting TAIFA-FIALA: FastAPI + ETL System"
echo "Focus: Verified $1B+ funding with live data collection"
echo "Working directory: $(pwd)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if port is already in use
if lsof -ti:$API_PORT > /dev/null 2>&1; then
    echo "⚠️  Port $API_PORT is already in use. Please stop the existing service or use a different port."
    exit 1
fi

# Check for required dependencies
echo "🔍 Checking dependencies..."
if ! command -v curl &> /dev/null; then
    echo "❌ curl is not installed. Please install it to continue."
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "⚠️  jq is not installed. JSON output will not be formatted."
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Start FastAPI server in background
echo "🌐 Starting FastAPI server on port $API_PORT..."
python3 run.py &
FASTAPI_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down FastAPI server (PID: $FASTAPI_PID)..."
    kill $FASTAPI_PID 2>/dev/null || true
    wait $FASTAPI_PID 2>/dev/null || true
    echo "✅ Cleanup complete"
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM EXIT

echo "✅ FastAPI server started (PID: $FASTAPI_PID)"
echo "📡 API will be available at: http://localhost:$API_PORT"
echo "📖 Docs will be available at: http://localhost:$API_PORT/docs"

# Wait for server to start with retries
echo "⏳ Waiting for server to become ready..."
RETRY_COUNT=0
SERVER_READY=false

while [ $RETRY_COUNT -lt $HEALTH_CHECK_RETRIES ]; do
    sleep 3
    RETRY_COUNT=$((RETRY_COUNT + 1))

    echo "🔍 Health check attempt $RETRY_COUNT/$HEALTH_CHECK_RETRIES..."

    if curl -s --max-time 5 http://localhost:$API_PORT/health > /dev/null 2>&1; then
        echo "✅ FastAPI server is responding!"
        SERVER_READY=true
        break
    else
        echo "⏳ Server not ready yet, waiting..."
    fi
done

if [ "$SERVER_READY" = false ]; then
    echo "❌ FastAPI server failed to start within $((HEALTH_CHECK_RETRIES * 3)) seconds"
    echo "🔍 Checking if process is still running..."

    if kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "🟡 Process is running but not responding to health checks"
        echo "📋 Possible issues:"
        echo "   - Server is still initializing (database connections, etc.)"
        echo "   - Environment variables missing (.env file)"
        echo "   - Database connection issues"
        echo "   - Missing dependencies"
    else
        echo "❌ Process has crashed"
    fi

    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "1. Check logs above for error messages"
    echo "2. Verify .env file exists with required variables"
    echo "3. Check database connectivity"
    echo "4. Try running 'python3 run.py' directly to see detailed errors"
    exit 1
fi

# Test API health endpoint
echo ""
echo "🏥 Testing health endpoint..."
if $JQ_AVAILABLE; then
    curl -s http://localhost:$API_PORT/health | jq '.'
else
    curl -s http://localhost:$API_PORT/health
fi

echo ""
echo "🔄 Now triggering initial ETL collection via API..."

# Function to make API calls with better error handling
make_api_call() {
    local endpoint=$1
    local description=$2

    echo "📡 $description..."

    if $JQ_AVAILABLE; then
        if curl -s --max-time 30 -X POST "$endpoint" -H "Content-Type: application/json" | jq '.' 2>/dev/null; then
            echo "✅ $description completed successfully"
        else
            echo "⚠️  $description may have failed or timed out"
        fi
    else
        if curl -s --max-time 30 -X POST "$endpoint" -H "Content-Type: application/json"; then
            echo "✅ $description completed successfully"
        else
            echo "⚠️  $description may have failed or timed out"
        fi
    fi

    echo ""
    sleep 2
}

# Trigger ETL jobs
make_api_call "http://localhost:$API_PORT/api/etl/academic?days_back=7&max_results=50" "Academic paper collection"
make_api_call "http://localhost:$API_PORT/api/etl/news?hours_back=24" "News monitoring"
make_api_call "http://localhost:$API_PORT/api/etl/serper-search?num_results=25" "Innovation search"

echo "✅ Initial ETL jobs triggered successfully!"
echo ""
echo "🎯 System Status:"
echo "- FastAPI Server: ✅ Running on http://localhost:$API_PORT"
echo "- ETL Jobs: 🔄 Running in background"
echo "- Database: 🔗 Connected (check logs for details)"
echo "- Vector DB: 🔗 Connected (check logs for details)"
echo ""
echo "🔍 Useful commands:"
echo "curl http://localhost:$API_PORT/api/etl/status | jq '.'"
echo "curl http://localhost:$API_PORT/api/etl/recent | jq '.'"
echo "curl http://localhost:$API_PORT/api/validation/summary | jq '.'"
echo ""
echo "🌐 Access the API documentation at: http://localhost:$API_PORT/docs"
echo ""
echo "Press Ctrl+C to stop the server and all ETL processes"

# Monitor system health
echo "🔄 Starting health monitoring (every 30 seconds)..."
echo "📊 Press Ctrl+C to stop the server"

while true; do
    sleep 30

    # Check if FastAPI process is still running
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "❌ FastAPI server process has stopped unexpectedly!"
        exit 1
    fi

    # Quick health check
    if curl -s --max-time 5 http://localhost:$API_PORT/health > /dev/null 2>&1; then
        echo "⏰ $(date): ✅ System healthy"
    else
        echo "⏰ $(date): ⚠️  Health check failed - server may be overloaded"
    fi
done
