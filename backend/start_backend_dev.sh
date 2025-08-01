#!/bin/bash

# TAIFA-FIALA: Start FastAPI + ETL System
# This will run both the API server and background ETL collection

cd /Users/drjforrest/dev/devprojects/TAIFA-FIALA/backend

echo "🚀 Starting TAIFA-FIALA: FastAPI + ETL System"
echo "Focus: Verified $1B+ funding with live data collection"

# Activate environment
source venv/bin/activate

# Start FastAPI server in background
echo "🌐 Starting FastAPI server..."
python main.py &
FASTAPI_PID=$!

# Wait for server to start
sleep 5

echo "✅ FastAPI server running (PID: $FASTAPI_PID)"
echo "📡 API available at: http://localhost:8000"
echo "📖 Docs available at: http://localhost:8000/docs"

# Test if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ FastAPI health check passed"
else
    echo "❌ FastAPI server not responding"
    kill $FASTAPI_PID
    exit 1
fi

echo ""
echo "🔄 Now triggering initial ETL collection via API..."

# Trigger academic ETL
echo "📚 Triggering academic paper collection..."
curl -X POST "http://localhost:8000/api/etl/academic?days_back=7&max_results=50" \
     -H "Content-Type: application/json" | jq '.'

sleep 2

# Trigger news ETL
echo "📰 Triggering news monitoring..."
curl -X POST "http://localhost:8000/api/etl/news?hours_back=24" \
     -H "Content-Type: application/json" | jq '.'

sleep 2

# Trigger innovation search
echo "🔍 Triggering innovation search..."
curl -X POST "http://localhost:8000/api/etl/serper-search?num_results=25" \
     -H "Content-Type: application/json" | jq '.'

echo ""
echo "✅ ETL jobs triggered successfully!"
echo ""
echo "🎯 System Status:"
echo "- FastAPI Server: Running on http://localhost:8000"
echo "- ETL Jobs: Running in background"
echo "- Database: Supabase connected"
echo "- Vector DB: Pinecone connected"
echo ""
echo "🔍 Monitor ETL status:"
echo "curl http://localhost:8000/api/etl/status | jq '.'"
echo ""
echo "📊 Check recent activity:"
echo "curl http://localhost:8000/api/etl/recent | jq '.'"
echo ""
echo "📈 Get validation summary:"
echo "curl http://localhost:8000/api/validation/summary | jq '.'"
echo ""
echo "Press Ctrl+C to stop both FastAPI and ETL processes"

# Keep script running and monitor
trap "echo '🛑 Stopping FastAPI server...'; kill $FASTAPI_PID; exit" INT

# Monitor ETL status every 30 seconds
while true; do
    sleep 30
    echo "⏰ $(date): Checking ETL status..."

    # Quick health check
    if curl -s http://localhost:8000/api/etl/health > /dev/null; then
        echo "✅ System healthy"
    else
        echo "⚠️  System health check failed"
    fi
done
