# 🎉 Final Architecture - GraphRAG Agent with MCP over HTTP

## ✅ Implementation Complete

Your GraphRAG Agent now uses a **microservices architecture** with:
- **MCP Service** running as an independent HTTP server
- **Gemini ADK Agent** using **MCPToolset** with **StreamableHTTPConnectionParams**
- True separation of concerns and scalability

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     User / Client                             │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP
                         ↓
┌──────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                            │
│              Port: 8000                                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  GeminiAgent (ADK Agent)                               │ │
│  │  - Uses MCPToolset                                     │ │
│  │  - Connects to MCP server via HTTP                     │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP (Streamable/SSE)
                         │ http://localhost:8001/mcp
                         ↓
┌──────────────────────────────────────────────────────────────┐
│         MCP HTTP Server (Independent Process)                 │
│         Port: 8001                                            │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI + StreamableHTTPServerTransport               │ │
│  │  - POST /mcp (MCP protocol endpoint)                   │ │
│  │  - GET /health (Health check)                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MCP Service (mcp_service.py)                          │ │
│  │  Tools:                                                │ │
│  │  - query_knowledge_base                                │ │
│  │  - list_documents                                      │ │
│  │  - search_similar_content                              │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────┘
                         │ Bolt Protocol
                         ↓
┌──────────────────────────────────────────────────────────────┐
│              Neo4j Graph Database                             │
│              Port: 7687 (bolt), 7474 (browser)                │
│              - Documents & Chunks                             │
│              - Vector embeddings                              │
│              - Relationships                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Files

### 1. **run_mcp_http_server.py** (NEW)
Independent MCP HTTP server using FastAPI and StreamableHTTPServerTransport.

**Features:**
- Runs on port 8001
- Exposes MCP protocol over HTTP
- Session management
- Health check endpoint

**Start:**
```bash
poetry run python run_mcp_http_server.py
```

### 2. **backend/gemini_agent.py** (UPDATED)
ADK Agent using MCPToolset to connect to MCP HTTP server.

**Changes:**
- Imports `MCPToolset` and `StreamableHTTPConnectionParams`
- Creates HTTP connection to MCP server
- No manual tool definitions (auto-discovered)
- Configurable via `MCP_SERVER_URL` environment variable

**Usage:**
```python
agent = GeminiAgent()  # Connects to MCP server automatically
response = await agent.generate_response("What documents are available?")
```

### 3. **backend/mcp_service.py** (UNCHANGED)
MCP service with 3 tools - now exposed via HTTP server.

**Tools:**
- `query_knowledge_base` - AI-powered Q&A
- `list_documents` - List all documents
- `search_similar_content` - Vector search

### 4. **start_all_services.sh** (NEW)
Convenience script to start all services.

**Usage:**
```bash
./start_all_services.sh
```

### 5. **stop_all_services.sh** (NEW)
Convenience script to stop all services.

**Usage:**
```bash
./stop_all_services.sh
```

---

## Quick Start

### 1. **Start All Services**

```bash
# Option 1: Use convenience script
./start_all_services.sh

# Option 2: Manual start
docker-compose up -d  # Neo4j
poetry run python run_mcp_http_server.py &  # MCP Server
poetry run uvicorn backend.main:app --reload --port 8000  # Backend
```

### 2. **Verify Services**

```bash
# Check Neo4j
curl http://localhost:7474

# Check MCP Server
curl http://localhost:8001/health
# Response: {"status":"healthy","service":"MCP HTTP Server"}

# Check Backend API
curl http://localhost:8000/health
# Response: {"status": "healthy"}

# Check API docs
open http://localhost:8000/docs
```

### 3. **Test the System**

```bash
# Upload a document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/document.pdf"

# Chat with the agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What documents are in the knowledge base?",
    "conversation_history": []
  }'
```

---

## Environment Variables

Create a `.env` file:

```bash
# MCP Server URL (optional, defaults to http://localhost:8001/mcp)
MCP_SERVER_URL=http://localhost:8001/mcp

# Google AI
GOOGLE_API_KEY=your_google_api_key_here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# App Settings
GEMINI_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=8192
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
UPLOAD_DIR=./uploads
```

---

## How It Works

### 1. **Agent Initialization**

```python
# backend/gemini_agent.py
connection_params = StreamableHTTPConnectionParams(
    url="http://localhost:8001/mcp",
    timeout=10.0,
    sse_read_timeout=300.0
)

mcp_toolset = MCPToolset(connection_params=connection_params)

agent = Agent(
    model="gemini-2.0-flash-exp",
    api_key=settings.google_api_key,
    tools=[mcp_toolset]  # Tools auto-discovered from MCP server
)
```

### 2. **Tool Discovery**

When `MCPToolset` is created:
1. Connects to `http://localhost:8001/mcp`
2. Sends MCP `initialize` request
3. MCP server responds with available tools
4. MCPToolset registers tools with ADK Agent
5. Agent is ready to use tools

### 3. **Tool Execution**

When user asks a question:
1. ADK Agent analyzes query
2. Decides which tool to call (e.g., `list_documents`)
3. MCPToolset sends HTTP POST to `/mcp` with tool call
4. MCP server receives request via StreamableHTTPServerTransport
5. MCP service executes the tool function
6. Results streamed back via SSE (Server-Sent Events)
7. MCPToolset receives results
8. Agent integrates results into response
9. Final response returned to user

---

## Benefits

### 1. **Microservices Architecture**
- ✅ MCP server runs independently
- ✅ Can be deployed on different machines
- ✅ Can be scaled horizontally
- ✅ Can serve multiple clients

### 2. **True Separation of Concerns**
- ✅ No circular dependencies
- ✅ Clean import graph
- ✅ Each service has single responsibility

### 3. **Standard Protocol**
- ✅ Uses MCP protocol over HTTP
- ✅ Compatible with any MCP client
- ✅ Can be used by Claude Desktop too

### 4. **Automatic Tool Discovery**
- ✅ No manual tool definitions in agent
- ✅ Tools defined once in MCP service
- ✅ MCPToolset discovers them automatically

### 5. **Production Ready**
- ✅ Health checks
- ✅ Session management
- ✅ Error handling
- ✅ Logging
- ✅ Scalable

---

## Testing

### Test MCP Server

```bash
# Start MCP server
poetry run python run_mcp_http_server.py

# Test health check
curl http://localhost:8001/health

# Expected: {"status":"healthy","service":"MCP HTTP Server"}
```

### Test Agent Connection

```python
poetry run python -c "
from backend.gemini_agent import GeminiAgent
import asyncio

async def test():
    agent = GeminiAgent()
    print('✅ Agent connected to MCP server')
    
    response = await agent.generate_response('Hello!')
    print(f'Response: {response}')

asyncio.run(test())
"
```

### Test End-to-End

```bash
# Start all services
./start_all_services.sh

# Upload a document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@README.md"

# Query the agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is in the README?", "conversation_history": []}'
```

---

## Deployment Options

### Option 1: Single Machine (Development)

```bash
# All services on localhost
./start_all_services.sh
```

### Option 2: Separate Machines (Production)

```bash
# Machine 1: MCP Server
poetry run python run_mcp_http_server.py

# Machine 2: Backend API
export MCP_SERVER_URL=http://mcp-server.internal:8001/mcp
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Option 3: Docker Compose

```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    ports:
      - "7687:7687"
      - "7474:7474"
    environment:
      - NEO4J_AUTH=neo4j/password
  
  mcp-server:
    build: .
    command: poetry run python run_mcp_http_server.py
    ports:
      - "8001:8001"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
  
  backend:
    build: .
    command: poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - MCP_SERVER_URL=http://mcp-server:8001/mcp
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - neo4j
      - mcp-server
```

### Option 4: Kubernetes

```yaml
# mcp-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3  # Scale MCP server
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: graphrag-agent:latest
        command: ["poetry", "run", "python", "run_mcp_http_server.py"]
        ports:
        - containerPort: 8001
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
spec:
  selector:
    app: mcp-server
  ports:
  - port: 8001
    targetPort: 8001
```

---

## Monitoring

### Logs

```bash
# MCP Server logs
tail -f logs/mcp_server.log

# Backend logs
tail -f logs/backend.log

# Neo4j logs
docker logs -f neo4j
```

### Metrics

```bash
# MCP Server health
watch -n 5 'curl -s http://localhost:8001/health'

# Backend health
watch -n 5 'curl -s http://localhost:8000/health'

# Neo4j status
docker exec neo4j cypher-shell -u neo4j -p password "CALL dbms.components()"
```

---

## Troubleshooting

### Issue: "Failed to create MCPToolset"

**Cause:** MCP server not running

**Solution:**
```bash
poetry run python run_mcp_http_server.py
```

### Issue: "Connection refused to localhost:8001"

**Cause:** MCP server not accessible

**Solution:**
```bash
# Check if running
curl http://localhost:8001/health

# Check logs
tail -f logs/mcp_server.log
```

### Issue: "Tools not discovered"

**Cause:** MCP server not returning tools

**Solution:**
```bash
# Check MCP service
poetry run python -c "from backend.mcp_service import mcp; print(mcp)"

# Restart MCP server
pkill -f run_mcp_http_server.py
poetry run python run_mcp_http_server.py
```

---

## Documentation

- **`MCP_HTTP_ARCHITECTURE.md`** - Detailed architecture documentation
- **`ADK_MCP_INTEGRATION.md`** - Previous integration approach
- **`GOOGLE_ADK_IMPLEMENTATION.md`** - ADK implementation details
- **`IMPLEMENTATION_STATUS.md`** - Overall system status
- **`QUICK_START.md`** - Quick start guide

---

## Summary

### ✅ What We Built

1. **Independent MCP HTTP Server**
   - Runs on port 8001
   - Exposes MCP protocol over HTTP
   - Can be scaled independently

2. **ADK Agent with MCPToolset**
   - Connects to MCP server via HTTP
   - Auto-discovers tools
   - No manual tool definitions

3. **Microservices Architecture**
   - True separation of concerns
   - No circular dependencies
   - Production-ready

### ✅ Key Technologies

- **Google ADK** - Agent framework
- **MCPToolset** - MCP client for ADK
- **StreamableHTTPConnectionParams** - HTTP connection
- **MCP Protocol** - Model Context Protocol
- **FastAPI** - HTTP server framework
- **Neo4j** - Graph database
- **Gemini 2.0** - LLM

### ✅ Benefits

- Scalable microservices architecture
- Standard MCP protocol
- Automatic tool discovery
- Production-ready
- Easy to deploy and monitor

---

**Status**: ✅ Fully Implemented and Tested  
**Architecture**: Microservices with MCP over HTTP  
**Protocol**: MCP Streamable HTTP (SSE)  
**Date**: October 16, 2025

## 🚀 Your GraphRAG Agent is Production Ready!

Start all services:
```bash
./start_all_services.sh
```

Access:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8001
- **Neo4j Browser**: http://localhost:7474

Enjoy your scalable, production-ready GraphRAG Agent! 🎉
