#!/usr/bin/env python3
"""
Command-line interface for Legion LM Studio MCP Bridge
"""

import asyncio
import json
import logging
import os
import signal
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from legion.mcp.bridges.lmstudio_bridge import LMStudioAdapter


def setup_logging():
    """Setup logging for LM Studio MCP bridge CLI."""
    log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


async def run_lmstudio_bridge():
    """Run the LM Studio MCP bridge with JSON-RPC over stdio."""
    logger = logging.getLogger(__name__)

    # Initialize LM Studio adapter
    logger.info("Initializing LM Studio MCP Bridge...")
    adapter = LMStudioAdapter()

    logger.info("LM Studio MCP Bridge ready for connections via stdio")
    logger.info("Available operations:")
    logger.info("  - Chat completions")
    logger.info("  - Model discovery")
    logger.info("  - Raw generation")
    logger.info("  - Health checks")

    # Simple JSON-RPC handler for stdio
    async def handle_request(request_data):
        """Handle incoming JSON-RPC requests."""
        try:
            request = json.loads(request_data)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            response = {"jsonrpc": "2.0", "id": request_id}

            # Route requests to appropriate adapter methods
            if method == "chat/completions":
                result = await adapter.chat_complete(**params)
                response["result"] = result

            elif method == "models/discover":
                result = await adapter.discover_model()
                response["result"] = result

            elif method == "generate":
                result = await adapter.raw_generate(params)
                response["result"] = result

            elif method == "stats":
                result = await adapter.stats()
                response["result"] = result

            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }

            return json.dumps(response)

        except json.JSONDecodeError as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            })
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {e}"
                }
            })

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
        logger.error(f"Bridge error: {e}")


def main():
    """Main entry point for LM Studio MCP bridge CLI."""
    setup_logging()

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...", file=sys.stderr)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the async bridge
    try:
        asyncio.run(run_lmstudio_bridge())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
