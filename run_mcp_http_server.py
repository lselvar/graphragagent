"""
Run MCP Service as Streamable HTTP Server

This script starts the MCP service as an HTTP server that can be accessed
by the ADK Agent using MCPToolset with StreamableHTTPConnectionParams.
"""

import logging
from mcp.server.fastmcp import FastMCP
from backend.graph_store import GraphStore
from backend.config import settings
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="GraphRAG MCP Server", json_response=False, stateless_http=False)

# Initialize graph store
graph_store = None

def initialize_graph_store():
    """Initialize the graph store."""
    global graph_store
    if graph_store is None:
        logger.info("Initializing GraphStore...")
        graph_store = GraphStore()
        logger.info("GraphStore initialized")
    return graph_store


@mcp.tool()
async def query_knowledge_base(query: str, top_k: int = 5) -> str:
    """Query the GraphRAG knowledge base with natural language.
    
    Args:
        query: The natural language question to ask
        top_k: Number of relevant chunks to retrieve (default: 5)
        
    Returns:
        String with formatted answer and sources
    """
    try:
        store = initialize_graph_store()
        
        # Need to get embedding for the query first
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(settings.embedding_model)
        query_embedding = model.encode(query).tolist()
        
        # Search for relevant chunks using vector search
        results = store.vector_search(query_embedding, top_k=top_k)
        
        if not results:
            return "No relevant information found in the knowledge base for your query."
        
        # Format results as readable text
        response_parts = [f"Found {len(results)} relevant sources:\n"]
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")[:500]  # Limit content length
            filename = result.get("filename", "Unknown")
            score = result.get("score", 0.0)
            
            response_parts.append(f"\n[Source {i}] {filename} (relevance: {score:.2f})")
            response_parts.append(f"{content}...\n")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error in query_knowledge_base: {e}")
        return f"Error querying knowledge base: {str(e)}"


@mcp.tool()
async def list_documents() -> str:
    """List all documents in the knowledge base.
    
    Returns:
        String with formatted list of documents
    """
    try:
        store = initialize_graph_store()
        
        # Get all documents
        query = """
        MATCH (d:Document)
        OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
        RETURN d.filename as filename, d.doc_type as doc_type, 
               d.created_at as created_at, count(c) as chunk_count
        ORDER BY d.created_at DESC
        """
        
        result = store.driver.execute_query(query)
        
        if not result.records:
            return "No documents found in the knowledge base."
        
        # Format as readable text
        response_parts = [f"Found {len(result.records)} documents in the knowledge base:\n"]
        
        for i, record in enumerate(result.records, 1):
            filename = record["filename"]
            doc_type = record["doc_type"] or "Unknown"
            chunk_count = record["chunk_count"]
            
            response_parts.append(f"{i}. {filename}")
            response_parts.append(f"   Type: {doc_type}, Chunks: {chunk_count}")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error in list_documents: {e}")
        return f"Error listing documents: {str(e)}"


@mcp.tool()
async def search_similar_content(query: str, top_k: int = 5) -> str:
    """Search for similar content using vector similarity.
    
    Args:
        query: The search query
        top_k: Number of results to return (default: 5)
        
    Returns:
        String with formatted search results
    """
    try:
        store = initialize_graph_store()
        
        # Get embedding for the query
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(settings.embedding_model)
        query_embedding = model.encode(query).tolist()
        
        results = store.vector_search(query_embedding, top_k=top_k)
        
        if not results:
            return f"No similar content found for query: {query}"
        
        # Format as readable text
        response_parts = [f"Found {len(results)} similar chunks for '{query}':\n"]
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")[:300]  # Limit content
            filename = result.get("filename", "Unknown")
            score = result.get("score", 0.0)
            
            response_parts.append(f"\n{i}. {filename} (similarity: {score:.2f})")
            response_parts.append(f"   {content}...")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error in search_similar_content: {e}")
        return f"Error searching content: {str(e)}"


# Health check endpoint function
async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "service": "MCP HTTP Server"})

# Get the FastAPI app with Streamable HTTP support
app = mcp.streamable_http_app()

# Add health check route to the Starlette app
app.routes.append(Route("/health", health_check, methods=["GET"]))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("Starting MCP Service as Streamable HTTP Server")
    logger.info("=" * 60)
    logger.info("Server URL: http://localhost:8001")
    logger.info("MCP Endpoint: http://localhost:8001/mcp")
    logger.info("Health Check: http://localhost:8001/health")
    logger.info("=" * 60)
    logger.info("ADK Agent can connect using:")
    logger.info("  StreamableHTTPConnectionParams(url='http://localhost:8001/mcp')")
    logger.info("=" * 60)
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
