#!/bin/bash

# Start All Services for GraphRAG Agent
# This script starts Neo4j, MCP HTTP Server, and Backend API

set -e

echo "============================================================"
echo "Starting GraphRAG Agent Services"
echo "============================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
sleep 30

# Check if MCP server is healthy
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ MCP HTTP Server is healthy${NC}"
else
    echo "❌ MCP HTTP Server failed to start"
    exit 1
fi

# Start Backend API
echo -e "${BLUE}Starting Backend API...${NC}"
poetry run uvicorn backend.main:app --reload --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid
echo -e "${GREEN}✅ Backend API started (PID: $BACKEND_PID)${NC}"
echo "   URL: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Logs: logs/backend.log"

echo ""
echo "============================================================"
echo -e "${GREEN}All services started successfully!${NC}"
echo "============================================================"
echo ""
echo "Services:"
echo "  • Neo4j:          http://localhost:7474"
echo "  • MCP Server:     http://localhost:8001"
echo "  • Backend API:    http://localhost:8000"
echo "  • API Docs:       http://localhost:8000/docs"
echo ""
echo "To stop all services, run:"
echo "  ./stop_all_services.sh"
echo ""
echo "To view logs:"
echo "  tail -f logs/mcp_server.log"
echo "  tail -f logs/backend.log"
echo ""
echo "============================================================"
