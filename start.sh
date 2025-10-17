#!/bin/bash

# GraphRAG Agent Startup Script

echo "🚀 Starting GraphRAG Agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    exit 1
fi

# Start Neo4j
echo "📊 Starting Neo4j database..."
docker-compose up -d

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
sleep 10

# Check if Neo4j is running
echo -e "${BLUE}Checking Neo4j...${NC}"
if ! docker ps | grep -q neo4j; then
    echo "Starting Neo4j..."
    docker-compose up -d
    echo -e "${GREEN}✅ Neo4j started${NC}"
    sleep 5
else
    echo -e "${GREEN}✅ Neo4j already running${NC}"
fi

# Start MCP HTTP Server in background
echo -e "${BLUE}Starting MCP HTTP Server...${NC}"
poetry run python run_mcp_http_server.py > logs/mcp_server.log 2>&1 &
MCP_PID=$!
echo $MCP_PID > .mcp_server.pid
echo -e "${GREEN}✅ MCP HTTP Server started (PID: $MCP_PID)${NC}"
echo "   URL: http://localhost:8001"
echo "   Logs: logs/mcp_server.log"
sleep 3

# Check if MCP server is healthy
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ MCP HTTP Server is healthy${NC}"
else
    echo "❌ MCP HTTP Server failed to start"
    exit 1
fi

# Check if Poetry is installed
if command -v poetry &> /dev/null; then
    echo "📦 Installing Python dependencies with Poetry..."
    poetry install
    
    echo "🐍 Starting backend server..."
    poetry run python -m backend.main &
    BACKEND_PID=$!
else
    echo "⚠️  Poetry not found. Please install dependencies manually."
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend
echo "⚛️  Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ GraphRAG Agent is running!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 Frontend UI: http://localhost:3000"
echo "📍 Neo4j Browser: http://localhost:7474"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
