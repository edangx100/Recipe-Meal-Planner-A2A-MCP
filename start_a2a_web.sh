#!/bin/bash

# Start A2A Web Interface
# This script starts both the Recipe Planner A2A Server and the ADK Web Interface

echo "================================================================================"
echo "🚀 Starting Recipe Meal Planner - A2A Web Interface"
echo "================================================================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Please create a .env file with your GOOGLE_API_KEY:"
    echo "  echo 'GOOGLE_API_KEY=your_api_key_here' > .env"
    echo ""
    exit 1
fi

# Check if GOOGLE_API_KEY is set in .env
if ! grep -q "GOOGLE_API_KEY" .env; then
    echo "❌ ERROR: GOOGLE_API_KEY not found in .env file!"
    echo ""
    echo "Please add your GOOGLE_API_KEY to .env:"
    echo "  echo 'GOOGLE_API_KEY=your_api_key_here' >> .env"
    echo ""
    exit 1
fi

echo "✅ Environment configured"
echo ""

# Step 1: Start Recipe Planner A2A Server
echo "📡 Step 1: Starting Recipe Planner A2A Server (port 8001)..."
echo ""

# Kill any existing server on port 8001
lsof -ti:8001 | xargs kill -9 2>/dev/null

# Start server in background
python recipe_planner_a2a_server.py > /tmp/a2a_server.log 2>&1 &
SERVER_PID=$!

echo "   Server started (PID: $SERVER_PID)"
echo "   Waiting for server to be ready..."
echo ""

# Wait for server to be ready (max 30 seconds)
for i in {1..30}; do
    if curl -s http://localhost:8001/.well-known/agent-card.json > /dev/null 2>&1; then
        echo "   ✅ Recipe Planner A2A Server is ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""
echo ""

# Verify server is running
if ! curl -s http://localhost:8001/.well-known/agent-card.json > /dev/null 2>&1; then
    echo "❌ ERROR: Recipe Planner A2A Server failed to start!"
    echo ""
    echo "Check the logs:"
    echo "  tail -50 /tmp/a2a_server.log"
    echo ""
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Step 2: Start ADK Web Interface
echo "🌐 Step 2: Starting ADK Web Interface (port 8000)..."
echo ""

# Kill any existing web server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo "================================================================================"
echo "✅ READY!"
echo "================================================================================"
echo ""
echo "🎯 Architecture:"
echo "   • Recipe Planner: http://localhost:8001 (A2A Server)"
echo "   • Web Interface:  http://localhost:8000 (Starting...)"
echo ""
echo "📋 Agent Card:"
echo "   curl http://localhost:8001/.well-known/agent-card.json"
echo ""
echo "📖 Documentation:"
echo "   • agents_web/recipe_meal_planner/README.md"
echo "   • A2A_IMPLEMENTATION.md"
echo "   • A2A_QUICKSTART.md"
echo ""
echo "🛑 To stop:"
echo "   Press Ctrl+C, then run:"
echo "   pkill -f recipe_planner_a2a_server.py"
echo ""
echo "================================================================================"
echo ""

# Start ADK web interface (this will run in foreground)
adk web --agent_path agents_web/recipe_meal_planner

# Cleanup when web interface exits
echo ""
echo "Stopping Recipe Planner A2A Server..."
kill $SERVER_PID 2>/dev/null
echo "✅ Shutdown complete"
