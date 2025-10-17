#!/usr/bin/env python3
"""
Run the GraphRAG MCP Server

This script starts the Model Context Protocol server that exposes
GraphRAG functionality to AI assistants and other MCP clients.

Usage:
    python run_mcp_server.py
    
Or with Poetry:
    poetry run python run_mcp_server.py
"""

import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.mcp_service import mcp, initialize_services, cleanup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for MCP server."""
    logger.info("=" * 60)
    logger.info("GraphRAG Agent - Model Context Protocol Server")
    logger.info("=" * 60)
    
    try:
        # Initialize backend services
        logger.info("Initializing GraphRAG services...")
        initialize_services()
        logger.info("✅ Services initialized successfully")
        
        # Start MCP server
        logger.info("\n🚀 Starting MCP server...")
        logger.info("The server is now ready to accept MCP connections")
        logger.info("Press Ctrl+C to stop the server\n")
        
        # Run the server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("\n\n⏹️  Shutting down MCP server...")
        cleanup()
        logger.info("✅ Server stopped successfully")
        
    except Exception as e:
        logger.error(f"❌ Error running MCP server: {e}")
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
