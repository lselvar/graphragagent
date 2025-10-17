"""
Model Context Protocol (MCP) Service for GraphRAG Agent

This module exposes the GraphRAG chat functionality as an MCP service,
allowing AI assistants and other tools to interact with the knowledge base.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from backend.config import settings
from backend.graph_store import GraphStore
from backend.embeddings import embedding_service

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = Server("graphrag-agent")

# Global instances (will be initialized on startup)
graph_store: Optional[GraphStore] = None


def initialize_services():
    """Initialize backend services for MCP."""
    global graph_store
    
    if graph_store is None:
        logger.info("Initializing GraphRAG services for MCP...")
        graph_store = GraphStore()
        logger.info("GraphRAG services initialized successfully")


def _generate_response_with_gemini(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Generate response using Gemini directly (without GeminiAgent to avoid circular dependency).
    
    Args:
        query: The user's question
        retrieved_chunks: Retrieved context chunks
        
    Returns:
        Generated response text
    """
    from google.genai import Client
    from google.genai.types import Content, Part
    
    try:
        client = Client(api_key=settings.google_api_key)
        
        # Format context
        context_parts = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"[Source {idx} - {chunk.get('filename', 'Unknown')}]\n"
                f"{chunk.get('content', '')}\n"
            )
        context = "\n".join(context_parts)
        
        # Build prompt
        prompt = f"""Context from knowledge base:
{context}

Question: {query}

Please provide a helpful answer based on the context above. If the context doesn't contain relevant information, say so."""
        
        # Generate response
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[Content(role="user", parts=[Part(text=prompt)])],
            config={
                "temperature": settings.temperature,
                "max_output_tokens": settings.max_tokens
            }
        )
        
        return response.text if response and response.text else "Unable to generate response."
        
    except Exception as e:
        logger.error(f"Error generating response with Gemini: {e}")
        return f"Error generating response: {str(e)}"


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="query_knowledge_base",
            description="Query the GraphRAG knowledge base with a natural language question",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask about the documents/code"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of relevant chunks to retrieve",
                        "default": 5
                    },
                    "include_sources": {
                        "type": "boolean",
                        "description": "Whether to include source information",
                        "default": True
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="list_documents",
            description="List all documents and repositories in the knowledge base",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_similar_content",
            description="Search for similar content using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "query_knowledge_base":
        result = await query_knowledge_base(**arguments)
    elif name == "list_documents":
        result = await list_documents()
    elif name == "search_similar_content":
        result = await search_similar_content(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def query_knowledge_base(
    question: str,
    top_k: int = 5,
    include_sources: bool = True
) -> Dict[str, Any]:
    """
    Query the GraphRAG knowledge base with a natural language question.
    
    This tool searches through uploaded documents and GitHub repositories
    to find relevant information and generates an AI-powered response.
    
    Args:
        question: The question to ask about the documents/code
        top_k: Number of relevant chunks to retrieve (default: 5)
        include_sources: Whether to include source information (default: True)
    
    Returns:
        Dictionary containing:
        - response: The AI-generated answer
        - sources: List of source documents/files (if include_sources=True)
        - chunks_used: Number of context chunks used
        - timestamp: When the query was processed
    
    Examples:
        - "What does the codeagent repository do?"
        - "Explain the main.py file"
        - "What is Raj's experience with Python?"
        - "How is authentication implemented?"
    """
    try:
        # Ensure services are initialized
        initialize_services()
        
        logger.info(f"MCP query received: {question[:100]}...")
        
        # Generate query embedding
        query_embedding = embedding_service.embed_text(question)
        
        # Retrieve relevant chunks from graph
        retrieved_chunks = graph_store.vector_search(query_embedding, top_k=top_k)
        
        if not retrieved_chunks:
            return {
                "response": "I don't have any relevant information to answer your question. The knowledge base may be empty.",
                "sources": [],
                "chunks_used": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate response using Gemini (direct call to avoid circular dependency)
        response_text = _generate_response_with_gemini(
            query=question,
            retrieved_chunks=retrieved_chunks
        )
        
        # Prepare response
        result = {
            "response": response_text,
            "chunks_used": len(retrieved_chunks),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add sources if requested
        if include_sources:
            sources = []
            seen_sources = set()
            
            for chunk in retrieved_chunks:
                source_key = f"{chunk.get('filename', 'Unknown')}:{chunk.get('file_path', '')}"
                if source_key not in seen_sources:
                    source_info = {
                        "filename": chunk.get('filename', 'Unknown'),
                        "document_id": chunk.get('document_id', ''),
                    }
                    
                    # Add file path for code chunks
                    if chunk.get('file_path'):
                        source_info['file_path'] = chunk['file_path']
                    
                    sources.append(source_info)
                    seen_sources.add(source_key)
            
            result["sources"] = sources
        
        logger.info(f"MCP query completed successfully with {len(retrieved_chunks)} chunks")
        return result
        
    except Exception as e:
        logger.error(f"Error processing MCP query: {e}")
        return {
            "response": f"Error processing query: {str(e)}",
            "sources": [],
            "chunks_used": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


async def list_documents() -> Dict[str, Any]:
    """
    List all documents and repositories in the knowledge base.
    
    Returns information about all uploaded documents and processed
    GitHub repositories, including their metadata and chunk counts.
    
    Returns:
        Dictionary containing:
        - total_documents: Total number of documents
        - documents: List of document information
    """
    try:
        initialize_services()
        
        logger.info("MCP: Listing all documents")
        
        # Get all documents
        docs = graph_store.get_all_documents()
        
        documents = []
        for doc in docs:
            doc_info = {
                "id": doc["document_id"],
                "filename": doc["filename"],
                "uploaded_at": str(doc["uploaded_at"]) if doc.get("uploaded_at") else None,
                "chunk_count": doc.get("chunk_count", 0),
            }
            
            # Add repository-specific fields
            if doc.get("repo_url"):
                doc_info["type"] = "github_repository"
                doc_info["repo_url"] = doc["repo_url"]
                doc_info["repo_name"] = doc.get("repo_name", "")
                doc_info["file_count"] = doc.get("file_count", 0)
            else:
                doc_info["type"] = "document"
            
            documents.append(doc_info)
        
        return {
            "total_documents": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return {
            "total_documents": 0,
            "documents": [],
            "error": str(e)
        }


async def get_document_info(document_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific document.
    
    Args:
        document_id: The UUID of the document
    
    Returns:
        Dictionary containing detailed document information including
        all chunks and their metadata.
    """
    try:
        initialize_services()
        
        logger.info(f"MCP: Getting info for document {document_id}")
        
        # Get document chunks
        chunks = graph_store.get_document_chunks(document_id)
        
        if not chunks:
            return {
                "error": f"Document {document_id} not found or has no chunks"
            }
        
        # Get document metadata
        docs = graph_store.get_all_documents()
        doc_metadata = next((d for d in docs if d["document_id"] == document_id), None)
        
        result = {
            "document_id": document_id,
            "total_chunks": len(chunks),
            "chunks": []
        }
        
        if doc_metadata:
            result["filename"] = doc_metadata.get("filename")
            result["uploaded_at"] = str(doc_metadata.get("uploaded_at"))
            if doc_metadata.get("repo_url"):
                result["repo_url"] = doc_metadata["repo_url"]
                result["repo_name"] = doc_metadata.get("repo_name")
        
        # Add chunk information
        for chunk in chunks[:10]:  # Limit to first 10 chunks for brevity
            chunk_info = {
                "chunk_id": chunk.get("chunk_id"),
                "chunk_index": chunk.get("chunk_index"),
                "content_preview": chunk.get("content", "")[:200] + "...",
            }
            
            if chunk.get("file_path"):
                chunk_info["file_path"] = chunk["file_path"]
            if chunk.get("language"):
                chunk_info["language"] = chunk["language"]
            
            result["chunks"].append(chunk_info)
        
        if len(chunks) > 10:
            result["note"] = f"Showing first 10 of {len(chunks)} chunks"
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting document info: {e}")
        return {
            "error": str(e)
        }


async def search_similar_content(
    query: str,
    top_k: int = 10
) -> Dict[str, Any]:
    """
    Search for similar content in the knowledge base using semantic search.
    
    This performs a vector similarity search without generating an AI response,
    useful for finding relevant code snippets or document sections.
    
    Args:
        query: The search query
        top_k: Number of results to return (default: 10)
    
    Returns:
        Dictionary containing:
        - total_results: Number of results found
        - results: List of matching chunks with similarity scores
    """
    try:
        initialize_services()
        
        logger.info(f"MCP: Searching for similar content: {query[:100]}...")
        
        # Generate query embedding
        query_embedding = embedding_service.embed_text(query)
        
        # Search for similar chunks
        results = graph_store.vector_search(query_embedding, top_k=top_k)
        
        formatted_results = []
        for result in results:
            result_info = {
                "content": result.get("content", "")[:300] + "...",
                "filename": result.get("filename", "Unknown"),
                "chunk_index": result.get("chunk_index", 0),
                "similarity_score": result.get("score", 0.0),
            }
            
            if result.get("file_path"):
                result_info["file_path"] = result["file_path"]
            if result.get("language"):
                result_info["language"] = result["language"]
            
            formatted_results.append(result_info)
        
        return {
            "total_results": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        return {
            "total_results": 0,
            "results": [],
            "error": str(e)
        }


def get_service_status() -> str:
    """
    Get the current status of the GraphRAG service.
    
    Returns a text description of the service status including
    database connectivity and available documents.
    """
    try:
        initialize_services()
        
        # Get document count
        docs = graph_store.get_all_documents()
        
        status = f"""GraphRAG Agent Status
===================

Service: Running
Model: {settings.gemini_model}
Embedding Model: {settings.embedding_model}

Knowledge Base:
- Total Documents: {len(docs)}
- Documents: {', '.join([d['filename'] for d in docs]) if docs else 'None'}

Database: Connected
Neo4j URI: {settings.neo4j_uri}
"""
        return status
        
    except Exception as e:
        return f"GraphRAG Agent Status: Error - {str(e)}"


# Cleanup function
def cleanup():
    """Cleanup resources when MCP server shuts down."""
    global graph_store
    if graph_store:
        graph_store.close()
        logger.info("GraphRAG services cleaned up")


async def main():
    """Main entry point for MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting GraphRAG MCP Server...")
    
    try:
        # Initialize services
        initialize_services()
        
        # Run the MCP server using stdio
        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(
                read_stream,
                write_stream,
                mcp.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server...")
        cleanup()
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        cleanup()


if __name__ == "__main__":
    asyncio.run(main())
