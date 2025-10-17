# ✅ ADK Agent with MCP Service Integration

## Overview

The Gemini ADK Agent now uses the **MCP Service toolset** instead of implementing its own tools. This creates a clean separation of concerns and enables both the ADK agent and Claude Desktop to use the same underlying tool implementations.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              ADK Agent (GeminiAgent)                 │
│              Uses MCP Service Tools                  │
│                                                      │
│  Tools (delegate to MCP):                           │
│  - _query_knowledge_base_tool                       │
│  - _list_documents_tool                             │
│  - _search_similar_content_tool                     │
└────────────────────┬────────────────────────────────┘
                     │ Delegates to
                     ↓
┌─────────────────────────────────────────────────────┐
│              MCP Service                             │
│              (mcp_service.py)                        │
│                                                      │
│  MCP Tools (shared implementation):                 │
│  - query_knowledge_base()                           │
│  - list_documents()                                 │
│  - search_similar_content()                         │
│                                                      │
│  Helper:                                            │
│  - _generate_response_with_gemini()                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│              GraphStore (Neo4j)                      │
│              - Vector search                         │
│              - Document queries                      │
└─────────────────────────────────────────────────────┘
```

## Key Changes

### 1. **GeminiAgent Now Delegates to MCP Service**

**Before:**
```python
def _search_knowledge_base_tool(self, query: str, top_k: int = 5):
    # Direct implementation
    query_embedding = embedding_service.embed_text(query)
    chunks = self.graph_store.vector_search(query_embedding, top_k)
    return {"results": chunks}
```

**After:**
```python
def _query_knowledge_base_tool(self, question: str, top_k: int = 5, include_sources: bool = True):
    # Delegate to MCP service
    result = asyncio.run(self.mcp_service.query_knowledge_base(
        question=question,
        top_k=top_k,
        include_sources=include_sources
    ))
    return result
```

### 2. **MCP Service is Self-Contained**

The MCP service no longer imports `GeminiAgent` to avoid circular dependencies. Instead, it has its own response generation function:

```python
def _generate_response_with_gemini(query: str, retrieved_chunks: List[Dict]) -> str:
    """Generate response using Gemini directly."""
    client = Client(api_key=settings.google_api_key)
    # ... generate response
    return response.text
```

### 3. **Three Tools Available**

Both ADK Agent and Claude Desktop can use:

#### 1. **query_knowledge_base**
- **Purpose**: Ask questions and get AI-powered responses
- **Parameters**: 
  - `question` (str): The question to ask
  - `top_k` (int): Number of chunks to retrieve (default: 5)
  - `include_sources` (bool): Include source attribution (default: True)
- **Returns**: AI-generated response with sources

#### 2. **list_documents**
- **Purpose**: List all documents and GitHub repos
- **Parameters**: None
- **Returns**: Document list with metadata

#### 3. **search_similar_content**
- **Purpose**: Semantic search without AI generation
- **Parameters**:
  - `query` (str): Search query
  - `top_k` (int): Number of results (default: 10)
- **Returns**: Similar chunks with scores

## Benefits

### 1. **Single Source of Truth**
- MCP service contains the canonical tool implementations
- ADK agent and Claude Desktop use the same tools
- No code duplication

### 2. **No Circular Dependencies**
- MCP service is independent
- GeminiAgent can import and use MCP service
- Clean dependency graph

### 3. **Consistent Behavior**
- Same results whether using ADK agent or Claude Desktop
- Easier to test and maintain
- Single place to update tool logic

### 4. **Flexibility**
- Can use ADK agent standalone
- Can use MCP service with Claude Desktop
- Can use both simultaneously

## Usage Examples

### Using ADK Agent

```python
from backend.gemini_agent import GeminiAgent
from backend.graph_store import GraphStore

# Initialize
graph_store = GraphStore()
agent = GeminiAgent(graph_store=graph_store)

# Ask a question (agent will use MCP tools automatically)
response = await agent.generate_response(
    query="What documents are in the knowledge base?"
)
print(response)
```

**What happens:**
1. ADK agent analyzes the query
2. Decides to call `_list_documents_tool`
3. Tool delegates to `mcp_service.list_documents()`
4. MCP service queries GraphStore
5. Results returned to agent
6. Agent generates final response

### Using MCP Service Directly

```python
from backend.mcp_service import query_knowledge_base

# Query directly
result = await query_knowledge_base(
    question="What does the codeagent repository do?",
    top_k=5,
    include_sources=True
)

print(result["response"])
print(result["sources"])
```

### Using with Claude Desktop

Claude Desktop automatically uses the MCP tools when configured:

```
User: "What documents are in the GraphRAG knowledge base?"

Claude: [Calls list_documents tool]
        [Receives document list]
        [Generates response]
        
        "The knowledge base contains 2 items:
        1. GitHub repository: codeagent (213 chunks)
        2. Document: resume.pdf (45 chunks)"
```

## Implementation Details

### ADK Agent Tool Methods

Each tool method in `GeminiAgent`:
1. Accepts parameters matching the MCP tool
2. Uses `asyncio.run()` to call async MCP function
3. Returns the result directly
4. Handles errors gracefully

```python
def _query_knowledge_base_tool(self, question: str, top_k: int = 5, include_sources: bool = True):
    try:
        import asyncio
        result = asyncio.run(self.mcp_service.query_knowledge_base(
            question=question,
            top_k=top_k,
            include_sources=include_sources
        ))
        return result
    except Exception as e:
        logger.error(f"Error in query_knowledge_base tool: {e}")
        return {"response": f"Error: {str(e)}", "sources": [], "error": str(e)}
```

### MCP Service Functions

Each MCP function:
1. Is async (for MCP protocol)
2. Initializes services if needed
3. Performs the actual work
4. Returns structured data
5. Handles errors

```python
async def query_knowledge_base(question: str, top_k: int = 5, include_sources: bool = True):
    try:
        initialize_services()
        query_embedding = embedding_service.embed_text(question)
        chunks = graph_store.vector_search(query_embedding, top_k)
        response_text = _generate_response_with_gemini(question, chunks)
        return {"response": response_text, "sources": [...], ...}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "sources": [], "error": str(e)}
```

## Testing

### Test ADK Agent with MCP Tools

```bash
poetry run python -c "
from backend.gemini_agent import GeminiAgent
from backend.graph_store import GraphStore
import asyncio

async def test():
    graph_store = GraphStore()
    agent = GeminiAgent(graph_store=graph_store)
    
    # Test query
    response = await agent.generate_response(
        query='What documents are available?'
    )
    print(response)

asyncio.run(test())
"
```

### Test MCP Service Directly

```bash
poetry run python -c "
from backend.mcp_service import list_documents
import asyncio

async def test():
    result = await list_documents()
    print(result)

asyncio.run(test())
"
```

### Test Imports (No Circular Dependencies)

```bash
poetry run python -c "from backend.gemini_agent import GeminiAgent; print('✅')"
poetry run python -c "from backend.mcp_service import mcp; print('✅')"
poetry run python -c "from backend.main import app; print('✅')"
```

## Error Handling

### ADK Agent Level
- Catches tool execution errors
- Returns error in tool result
- Agent can handle gracefully

### MCP Service Level
- Catches service errors
- Returns structured error response
- Logs errors for debugging

### Example Error Flow

```python
# User asks question with empty knowledge base
query = "What's in the codebase?"

# ADK agent calls tool
result = agent._query_knowledge_base_tool(query)

# MCP service returns
{
    "response": "I don't have any relevant information...",
    "sources": [],
    "chunks_used": 0,
    "timestamp": "2025-10-16T19:46:00"
}

# Agent generates final response
"The knowledge base appears to be empty. Please upload some documents first."
```

## Configuration

### Environment Variables

Both ADK agent and MCP service use the same configuration:

```bash
# .env
GOOGLE_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.7
MAX_TOKENS=8192
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Deployment

### Start Backend with ADK Agent

```bash
poetry run uvicorn backend.main:app --reload --port 8000
```

The backend uses `GeminiAgent` which delegates to MCP service.

### Start MCP Server for Claude Desktop

```bash
poetry run python run_mcp_server.py
```

Claude Desktop connects via stdio and uses MCP tools directly.

### Both Can Run Simultaneously

- Backend API uses ADK agent
- Claude Desktop uses MCP service
- Both use the same tool implementations
- No conflicts

## Troubleshooting

### Issue: "Circular import error"

**Solution:** Already fixed! MCP service no longer imports GeminiAgent.

### Issue: "asyncio.run() cannot be called from running loop"

**Solution:** The tool methods use `asyncio.run()` which works when called from ADK agent (not in async context).

### Issue: "Graph store not available"

**Solution:** Ensure GraphStore is passed to GeminiAgent:
```python
agent = GeminiAgent(graph_store=graph_store)
```

## Summary

✅ **ADK Agent now uses MCP Service tools**  
✅ **No circular dependencies**  
✅ **Single source of truth for tool implementations**  
✅ **Works with both ADK agent and Claude Desktop**  
✅ **Clean separation of concerns**  
✅ **All imports working correctly**

---

**Status**: ✅ Fully Implemented  
**Architecture**: ADK Agent → MCP Service → GraphStore  
**Date**: October 16, 2025

Your ADK agent now properly delegates to the MCP service toolset! 🚀
