# 🚀 MCP HTTP Server + ADK MCPToolset Architecture

## Overview

The system now runs with **MCP Service as an independent HTTP server** and the **Gemini ADK Agent uses MCPToolset** to connect via `StreamableHTTPConnectionParams`.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Gemini ADK Agent (GeminiAgent)               │
│         Uses MCPToolset                              │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  MCPToolset                                 │    │
│  │  - Connects via StreamableHTTPConnection    │    │
│  │  - Auto-discovers tools from MCP server     │    │
│  │  - Handles tool calling automatically       │    │
│  └────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (Streamable)
                       │ http://localhost:8001/mcp
                       ↓
┌─────────────────────────────────────────────────────┐
│      MCP HTTP Server (Independent Process)           │
│      run_mcp_http_server.py                          │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  FastAPI + StreamableHTTPServerTransport   │    │
│  │  POST /mcp - MCP protocol endpoint          │    │
│  │  GET /health - Health check                 │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  MCP Service (mcp_service.py)              │    │
│  │  - query_knowledge_base                     │    │
│  │  - list_documents                           │    │
│  │  - search_similar_content                   │    │
│  └────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────┐
│              GraphStore (Neo4j)                      │
│              - Vector search                         │
│              - Document queries                      │
└─────────────────────────────────────────────────────┘
```

## Key Components

### 1. **MCP HTTP Server** (`run_mcp_http_server.py`)

**Independent FastAPI server** that exposes MCP service via HTTP:

```python
# Start the server
poetry run python run_mcp_http_server.py

# Server runs on:
# - URL: http://localhost:8001
# - MCP Endpoint: http://localhost:8001/mcp
# - Health Check: http://localhost:8001/health
```

**Features:**
- ✅ Streamable HTTP transport (SSE - Server-Sent Events)
- ✅ Session management
- ✅ Health check endpoint
- ✅ Independent process (can run separately)
- ✅ Can serve multiple clients simultaneously

**Implementation:**
```python
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    session_id = request.headers.get("mcp-session-id", str(uuid.uuid4()))
    
    if session_id not in transports:
        transport = StreamableHTTPServerTransport(
            mcp_session_id=session_id,
            is_json_response_enabled=False
        )
        transports[session_id] = transport
        
        asyncio.create_task(mcp.run(
            transport.read_stream,
            transport.write_stream,
            mcp.create_initialization_options()
        ))
    
    response_data = await transport.handle_post_message(
        body=await request.body(),
        last_event_id=request.headers.get("last-event-id")
    )
    
    return StreamingResponse(
        response_data,
        media_type="text/event-stream",
        headers={"mcp-session-id": session_id}
    )
```

### 2. **Gemini ADK Agent with MCPToolset** (`backend/gemini_agent.py`)

**ADK Agent that connects to MCP HTTP server**:

```python
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams

# Create connection parameters
connection_params = StreamableHTTPConnectionParams(
    url="http://localhost:8001/mcp",
    timeout=10.0,
    sse_read_timeout=300.0
)

# Create MCPToolset
mcp_toolset = MCPToolset(connection_params=connection_params)

# Create Agent with MCPToolset
agent = Agent(
    model="gemini-2.0-flash-exp",
    api_key=settings.google_api_key,
    tools=[mcp_toolset]  # MCPToolset auto-discovers tools
)
```

**Features:**
- ✅ Automatic tool discovery from MCP server
- ✅ No manual tool definitions needed
- ✅ HTTP connection to MCP server
- ✅ Handles tool calling automatically
- ✅ Configurable via environment variable

### 3. **MCP Service** (`backend/mcp_service.py`)

**Unchanged** - Still defines the 3 MCP tools:
- `query_knowledge_base`
- `list_documents`
- `search_similar_content`

## How It Works

### 1. **Startup Sequence**

```bash
# Terminal 1: Start MCP HTTP Server
poetry run python run_mcp_http_server.py
# Server starts on http://localhost:8001

# Terminal 2: Start Backend API
poetry run uvicorn backend.main:app --reload --port 8000
# Backend creates GeminiAgent which connects to MCP server
```

### 2. **Tool Discovery Flow**

```
1. GeminiAgent initializes
2. Creates MCPToolset with HTTP connection params
3. MCPToolset connects to http://localhost:8001/mcp
4. MCPToolset calls MCP initialize
5. MCP server returns list of available tools
6. MCPToolset registers tools with ADK Agent
7. Agent is ready with all MCP tools
```

### 3. **Tool Calling Flow**

```
User: "What documents are in the knowledge base?"
    ↓
ADK Agent analyzes query
    ↓
Agent decides to call "list_documents" tool
    ↓
MCPToolset sends HTTP request to MCP server
    ↓
MCP server receives tool call request
    ↓
MCP service executes list_documents()
    ↓
MCP server returns results via SSE
    ↓
MCPToolset receives results
    ↓
Agent integrates results into response
    ↓
Final response returned to user
```

## Benefits

### 1. **True Separation of Concerns**
- MCP server runs independently
- Can be deployed separately
- Can be scaled independently
- Can serve multiple clients

### 2. **No Direct Dependencies**
- GeminiAgent doesn't import mcp_service
- No circular dependencies
- Clean architecture

### 3. **Flexibility**
- MCP server can run on different machine
- Can use load balancer for MCP servers
- Easy to test components separately

### 4. **Standard Protocol**
- Uses MCP protocol over HTTP
- Compatible with any MCP client
- Can be used by Claude Desktop too

### 5. **Automatic Tool Discovery**
- MCPToolset discovers tools automatically
- No manual tool definitions in agent
- Tools defined once in MCP service

## Configuration

### Environment Variables

```bash
# .env

# MCP Server URL (optional, defaults to http://localhost:8001/mcp)
MCP_SERVER_URL=http://localhost:8001/mcp

# Google AI
GOOGLE_API_KEY=your_api_key

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# App Settings
GEMINI_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=8192
```

### Ports

- **8000**: Backend API (FastAPI)
- **8001**: MCP HTTP Server
- **7687**: Neo4j (bolt)
- **7474**: Neo4j Browser

## Usage

### Start MCP HTTP Server

```bash
poetry run python run_mcp_http_server.py
```

**Output:**
```
============================================================
Starting MCP Service as Streamable HTTP Server
============================================================
Server URL: http://localhost:8001
MCP Endpoint: http://localhost:8001/mcp
Health Check: http://localhost:8001/health
============================================================
ADK Agent can connect using:
  StreamableHTTPConnectionParams(url='http://localhost:8001/mcp')
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Start Backend API

```bash
poetry run uvicorn backend.main:app --reload --port 8000
```

**Agent will connect to MCP server automatically:**
```
INFO:backend.gemini_agent:Connecting to MCP server at: http://localhost:8001/mcp
INFO:backend.gemini_agent:MCPToolset created successfully
INFO:backend.gemini_agent:Initialized Gemini ADK Agent with MCPToolset
```

### Test Health Check

```bash
curl http://localhost:8001/health
```

**Response:**
```json
{"status":"healthy","service":"MCP HTTP Server"}
```

### Use the Agent

```python
from backend.gemini_agent import GeminiAgent

# Agent connects to MCP server automatically
agent = GeminiAgent()

# Ask a question - agent uses MCP tools via HTTP
response = await agent.generate_response(
    query="What documents are in the knowledge base?"
)
print(response)
```

## Testing

### Test MCP Server Independently

```bash
# Start MCP server
poetry run python run_mcp_http_server.py

# In another terminal, check health
curl http://localhost:8001/health

# Should return:
# {"status":"healthy","service":"MCP HTTP Server"}
```

### Test Agent Connection

```python
poetry run python -c "
from backend.gemini_agent import GeminiAgent
import asyncio

async def test():
    # This will try to connect to MCP server
    agent = GeminiAgent()
    print('✅ Agent created and connected to MCP server')

asyncio.run(test())
"
```

### Test End-to-End

```bash
# Terminal 1: Start Neo4j
docker-compose up -d

# Terminal 2: Start MCP HTTP Server
poetry run python run_mcp_http_server.py

# Terminal 3: Start Backend
poetry run uvicorn backend.main:app --reload --port 8000

# Terminal 4: Test API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What documents are available?", "conversation_history": []}'
```

## Deployment

### Development

```bash
# Run all services locally
docker-compose up -d  # Neo4j
poetry run python run_mcp_http_server.py  # MCP Server
poetry run uvicorn backend.main:app --reload  # Backend API
```

### Production

**Option 1: Same Machine**
```bash
# Use process manager (e.g., systemd, supervisor)
# Service 1: MCP HTTP Server on port 8001
# Service 2: Backend API on port 8000
```

**Option 2: Separate Machines**
```bash
# Machine 1: MCP HTTP Server
MCP_SERVER_URL=http://mcp-server.internal:8001/mcp

# Machine 2: Backend API
# Set MCP_SERVER_URL environment variable
export MCP_SERVER_URL=http://mcp-server.internal:8001/mcp
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Option 3: Docker Compose**
```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    ports:
      - "7687:7687"
      - "7474:7474"
  
  mcp-server:
    build: .
    command: poetry run python run_mcp_http_server.py
    ports:
      - "8001:8001"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
  
  backend:
    build: .
    command: poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - MCP_SERVER_URL=http://mcp-server:8001/mcp
      - NEO4J_URI=bolt://neo4j:7687
```

## Troubleshooting

### Issue: "Failed to create MCPToolset"

**Cause:** MCP HTTP server not running

**Solution:**
```bash
# Start MCP server first
poetry run python run_mcp_http_server.py

# Then start backend
poetry run uvicorn backend.main:app --reload
```

### Issue: "Connection refused to localhost:8001"

**Cause:** MCP server not accessible

**Solution:**
```bash
# Check if MCP server is running
curl http://localhost:8001/health

# Check logs
# Look for "Uvicorn running on http://0.0.0.0:8001"
```

### Issue: "Agent created without MCP tools"

**Cause:** MCPToolset creation failed

**Solution:**
```bash
# Check MCP server logs
# Ensure MCP server is healthy
# Verify MCP_SERVER_URL is correct
```

### Issue: "Tools not discovered"

**Cause:** MCP server not returning tools

**Solution:**
```bash
# Check MCP service has tools defined
# Verify @mcp.list_tools() decorator
# Check MCP server logs for errors
```

## Comparison: Before vs After

### Before (Direct Delegation)

```python
# GeminiAgent directly imported mcp_service
from backend import mcp_service

def _query_tool(self, question):
    return asyncio.run(mcp_service.query_knowledge_base(question))

# Problems:
# - Tight coupling
# - Same process
# - Can't scale independently
```

### After (HTTP + MCPToolset)

```python
# GeminiAgent uses MCPToolset over HTTP
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8001/mcp"
    )
)

# Benefits:
# - Loose coupling
# - Separate processes
# - Can scale independently
# - Standard MCP protocol
```

## Summary

✅ **MCP Service runs as independent HTTP server**  
✅ **ADK Agent uses MCPToolset with StreamableHTTPConnectionParams**  
✅ **True separation of concerns**  
✅ **No circular dependencies**  
✅ **Automatic tool discovery**  
✅ **Standard MCP protocol over HTTP**  
✅ **Can scale independently**  
✅ **Production-ready architecture**

---

**Status**: ✅ Fully Implemented  
**Architecture**: ADK Agent → HTTP → MCP Server → GraphStore  
**Protocol**: MCP over Streamable HTTP (SSE)  
**Date**: October 16, 2025

Your system now uses a proper microservices architecture with MCP over HTTP! 🚀
