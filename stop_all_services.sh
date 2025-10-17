#!/bin/bash

# Stop All Services for GraphRAG Agent

echo "============================================================"
echo "Stopping GraphRAG Agent Services"
echo "============================================================"

# Stop Backend API
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "Stopping Backend API (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend API already stopped"
    rm .backend.pid
    echo "✅ Backend API stopped"
fi

# Stop MCP HTTP Server
if [ -f .mcp_server.pid ]; then
    MCP_PID=$(cat .mcp_server.pid)
    echo "Stopping MCP HTTP Server (PID: $MCP_PID)..."
    kill $MCP_PID 2>/dev/null || echo "MCP HTTP Server already stopped"
    rm .mcp_server.pid
    echo "✅ MCP HTTP Server stopped"
fi

# Optionally stop Neo4j
read -p "Stop Neo4j? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping Neo4j..."
    docker-compose down
    echo "✅ Neo4j stopped"
fi

echo ""
echo "============================================================"
echo "All services stopped"
echo "============================================================"
