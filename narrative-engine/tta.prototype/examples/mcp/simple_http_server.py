#!/usr/bin/env python3
"""
Simple HTTP Server Example

This script demonstrates a simple HTTP server that can be used to test the MCP integration.
"""

import argparse
import http.server
import json
import logging
import socketserver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for MCP HTTP requests."""

    def do_GET(self):
        """Handle GET requests."""
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Create response data
        response = {
            "name": "TTA Simple HTTP Server",
            "description": "A simple HTTP server for testing MCP integration",
            "version": "1.0.0",
            "tools": [
                {
                    "name": "echo",
                    "description": "Echo a message back to the user"
                },
                {
                    "name": "calculate",
                    "description": "Safely evaluate a mathematical expression"
                }
            ],
            "resources": [
                {
                    "name": "info://server",
                    "description": "Get information about this server"
                },
                {
                    "name": "info://system",
                    "description": "Get basic system information"
                }
            ]
        }

        # Send response
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Log messages with the logger."""
        logger.info(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Simple HTTP Server Example")

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    return parser.parse_args()

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    args = parse_args()

    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Create server
    with socketserver.TCPServer((args.host, args.port), MCPHandler) as httpd:
        logger.info(f"Starting HTTP server on {args.host}:{args.port}")

        try:
            # Serve until interrupted
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped")

if __name__ == "__main__":
    main()
