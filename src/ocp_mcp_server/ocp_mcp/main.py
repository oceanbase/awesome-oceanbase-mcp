"""Main entry point for OCP MCP Server."""

import argparse
import logging
from .server import app

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point to run the MCP server."""
    parser = argparse.ArgumentParser(description="OCP MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="Specify the MCP server transport type as stdio or sse or streamable-http.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    transport = args.transport
    logger.info(f"Starting OCP MCP server with {transport} mode...")

    if transport in {"sse", "streamable-http"}:
        app.settings.host = args.host
        app.settings.port = args.port

    app.run(transport=transport)


if __name__ == "__main__":
    main()
