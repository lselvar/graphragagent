"""
Gemini Agent using Google Agent Development Kit (ADK)

This module implements a Gemini-powered agent using the official Google ADK
with MCPToolset to connect to MCP service via HTTP.
"""

from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents.run_config import RunConfig
from google.genai.types import Part, Content
from typing import List, Dict, Any, Optional
import logging
import os
import uuid
from backend.config import settings
from backend.models import ChatMessage

logger = logging.getLogger(__name__)


class GeminiAgent:
    """Gemini LLM agent using Google Agent Development Kit (ADK) with MCPToolset."""
    
    APP_NAME = "GraphRAG Agent"
    
    def __init__(self, graph_store=None, mcp_server_url: str = None):
        """
        Initialize Gemini ADK agent with MCPToolset connecting to MCP HTTP server.
        
        Args:
            graph_store: Optional GraphStore instance (for backward compatibility)
            mcp_server_url: URL of the MCP HTTP server (default: http://localhost:8001/mcp)
        """
        self.graph_store = graph_store
        
        # Ensure GOOGLE_API_KEY is set in environment for ADK
        if not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = settings.google_api_key
            logger.info("Set GOOGLE_API_KEY from settings")
        
        # Get MCP server URL from environment or use default
        if mcp_server_url is None:
            mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
        
        logger.info(f"Connecting to MCP server at: {mcp_server_url}")
        
        # Create MCP connection parameters
        connection_params = StreamableHTTPConnectionParams(
            url=mcp_server_url,
            timeout=10.0,
            sse_read_timeout=300.0
        )
        
        # Create MCPToolset
        try:
            mcp_toolset = MCPToolset(connection_params=connection_params)
            logger.info("MCPToolset created successfully")
        except Exception as e:
            logger.error(f"Failed to create MCPToolset: {e}")
            logger.warning("Agent will be created without MCP tools")
            mcp_toolset = None
        
        # Create ADK Agent with MCPToolset
        from google.genai import types
        
        # Create model configuration
        model_config = types.GenerateContentConfig(
            temperature=settings.temperature,
            max_output_tokens=settings.max_tokens
        )
        
        # Build agent configuration
        agent_config = {
            "name": "graphrag_agent",
            "description": "GraphRAG agent with access to knowledge base via MCP tools",
            "model": settings.gemini_model,
            "instruction": """You are an intelligent AI assistant with access to a GraphRAG knowledge base containing documents and code repositories.

Your capabilities (via MCP tools):
1. **query_knowledge_base**: Query the knowledge base with natural language questions and get AI-powered responses
2. **list_documents**: View all available documents and repositories in the knowledge base
3. **search_similar_content**: Search for similar content using semantic vector search

When answering questions:
- Use the available MCP tools to access the knowledge base
- query_knowledge_base provides AI-generated responses with sources
- list_documents shows what's available in the knowledge base
- search_similar_content finds relevant chunks without AI generation
- Analyze the retrieved information carefully
- Provide accurate, well-structured responses
- Cite sources when relevant
- If information is not in the knowledge base, clearly state that
- Maintain conversation context

Always be helpful, accurate, and transparent about your knowledge limitations.""",
            "generate_content_config": model_config
        }
        
        # Add tools if MCPToolset was created successfully
        if mcp_toolset:
            agent_config["tools"] = [mcp_toolset]
        
        self.agent = Agent(**agent_config)
        
        # Initialize session service and runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name=self.APP_NAME,
            agent=self.agent,
            session_service=self.session_service
        )
        
        # Session will be created lazily on first use
        self.default_user_id = "default_user"
        self.default_session_id = None
        self._session_initialized = False
        
        logger.info(f"Initialized Gemini ADK Agent with MCPToolset, model: {settings.gemini_model}")
    
    # MCPToolset automatically provides tools from the MCP server
    # No need to define tool methods - they're discovered from the MCP service
    
    async def _ensure_session(self):
        """Ensure a session exists, creating one if necessary."""
        if not self._session_initialized:
            session = await self.session_service.create_session(
                app_name=self.APP_NAME,
                user_id=self.default_user_id
            )
            self.default_session_id = session.id
            self._session_initialized = True
            logger.info(f"Created session: {self.default_session_id}")
    
    def _format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context for the LLM."""
        if not retrieved_chunks:
            return "No relevant context found."
        
        context_parts = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"[Source {idx} - {chunk.get('filename', 'Unknown')}]\n"
                f"{chunk.get('content', '')}\n"
            )
        
        return "\n".join(context_parts)
    
    async def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]] = None,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """
        Generate a response using Gemini ADK agent with tool support.
        
        The agent can autonomously decide to use tools (search_knowledge_base, list_documents, etc.)
        or use the provided retrieved_chunks directly.
        
        Args:
            query: The user's question
            retrieved_chunks: Optional pre-retrieved context chunks
            conversation_history: Optional conversation history
            
        Returns:
            Generated response text
        """
        try:
            logger.info(f"Generating response for query: {query[:100]}...")
            
            # Ensure session exists
            await self._ensure_session()
            
            # Build the prompt
            if retrieved_chunks:
                # If chunks provided, include them as context
                context = self._format_context(retrieved_chunks)
                prompt = f"""Context from knowledge base:
{context}

Question: {query}"""
            else:
                # Let agent decide whether to use tools
                prompt = query
            
            # Create user message in ADK format
            user_message = Content(role="user", parts=[Part.from_text(text=prompt)])
            
            # Create run configuration
            run_config = RunConfig(response_modalities=["TEXT"])
            
            # Use ADK Runner to generate response (async)
            response_parts = []
            async for event in self.runner.run_async(
                user_id=self.default_user_id,
                session_id=self.default_session_id,
                new_message=user_message,
                run_config=run_config
            ):
                # Collect response parts from events
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
                        elif part.function_call:
                            logger.info(f"Function call: {part.function_call.name}")
            
            # Combine all response parts
            full_response = "".join(response_parts).strip()
            
            if not full_response:
                return "I apologize, but I couldn't generate a response. Please try again."
            
            return full_response
            
        except Exception as e:
            logger.error(f"Error generating response with Gemini ADK: {e}")
            raise
    
    async def generate_summary(self, text: str) -> str:
        """Generate a summary of the given text."""
        try:
            # Ensure session exists
            await self._ensure_session()
            
            prompt = f"""Please provide a concise summary of the following text:

{text}

Summary:"""
            
            # Create user message
            user_message = Content(role="user", parts=[Part.from_text(text=prompt)])
            run_config = RunConfig(response_modalities=["TEXT"])
            
            # Generate response (async)
            response_parts = []
            async for event in self.runner.run_async(
                user_id=self.default_user_id,
                session_id=self.default_session_id,
                new_message=user_message,
                run_config=run_config
            ):
                # Collect response
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
            
            full_response = "".join(response_parts).strip()
            return full_response if full_response else "Unable to generate summary."
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    async def extract_entities(self, text: str) -> List[str]:
        """Extract key entities from the text."""
        try:
            # Ensure session exists
            await self._ensure_session()
            
            prompt = f"""Extract the key entities (people, organizations, locations, concepts) from the following text.
Return them as a comma-separated list.

Text: {text}

Entities:"""
            
            # Create user message
            user_message = Content(role="user", parts=[Part.from_text(text=prompt)])
            run_config = RunConfig(response_modalities=["TEXT"])
            
            # Generate response (async)
            response_parts = []
            async for event in self.runner.run_async(
                user_id=self.default_user_id,
                session_id=self.default_session_id,
                new_message=user_message,
                run_config=run_config
            ):
                # Collect response
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
            
            response_text = "".join(response_parts).strip()
            
            if response_text:
                entities = [e.strip() for e in response_text.split(',')]
                return entities
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
