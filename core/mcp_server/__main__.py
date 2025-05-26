#!/usr/bin/env python3
"""
Command-line interface for Legion Unified MCP Server
"""

import asyncio
import json
import logging
import os
import signal
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.mcp_server import get_mcp_server


def setup_logging():
    """Setup logging for MCP server CLI."""
    log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


async def run_mcp_server():
    """Run the unified MCP server with JSON-RPC over stdio."""
    logger = logging.getLogger(__name__)

    # Load configuration
    config_path = os.getenv("MCP_CONFIG_PATH", "mcp_config.json")
    config = {}

    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")

    # Initialize MCP server
    logger.info("Initializing Legion Unified MCP Server...")
    mcp_server = await get_mcp_server(config)

    logger.info("MCP Server ready for connections via stdio")
    logger.info("Available operations:")
    logger.info("  - Vector memory storage/retrieval")
    logger.info("  - Cache management with TTL")
    logger.info("  - Event logging and querying")
    logger.info("  - Codebase analysis tracking")
    logger.info("  - DevOps operations monitoring")

    # Simple JSON-RPC handler for stdio
    async def handle_request(request_data):
        """Handle incoming JSON-RPC requests."""
        try:
            request = json.loads(request_data)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            response = {"jsonrpc": "2.0", "id": request_id}

            # Route requests to appropriate MCP server methods
            if method == "vector/store":
                result = await mcp_server.store_vector_memory(**params)
                response["result"] = {"id": result}

            elif method == "vector/retrieve":
                result = await mcp_server.retrieve_vector_memory(**params)
                response["result"] = {"memories": result}

            elif method == "cache/store":
                result = await mcp_server.store_cache(**params)
                response["result"] = {"id": result}

            elif method == "cache/get":
                result = await mcp_server.get_cache(params.get("key"))
                response["result"] = {"value": result}

            elif method == "event/log":
                result = await mcp_server.log_event(**params)
                response["result"] = {"id": result}

            elif method == "event/get":
                result = await mcp_server.get_events(**params)
                response["result"] = {"events": result}

            elif method == "codebase/store":
                result = await mcp_server.store_codebase_analysis(**params)
                response["result"] = {"id": result}

            elif method == "codebase/get":
                result = await mcp_server.get_codebase_analysis(**params)
                response["result"] = {"analysis": result}

            elif method == "devops/log":
                result = await mcp_server.log_devops_operation(**params)
                response["result"] = {"id": result}

            elif method == "devops/update":
                result = await mcp_server.update_devops_operation(**params)
                response["result"] = {"updated": result}

            elif method == "stats":
                result = await mcp_server.get_performance_stats()
                response["result"] = result

            elif method == "health":
                result = await mcp_server.health_check()
                response["result"] = result

            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                }

            return json.dumps(response)

        except json.JSONDecodeError as e:
            return json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                }
            )
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if "request" in locals() else None,
                    "error": {"code": -32603, "message": f"Internal error: {e}"},
                }
            )

    # Main event loop for stdio communication
    try:
        while True:
            # Read from stdin
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )

            if not line:
                break

            line = line.strip()
            if line:
                # Process request and write response to stdout
                response = await handle_request(line)
                print(response, flush=True)

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Shutting down MCP server...")
        await mcp_server.shutdown()


def main():
    """Main entry point for MCP server CLI."""
    setup_logging()

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...", file=sys.stderr)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the async server
    try:
        asyncio.run(run_mcp_server())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
