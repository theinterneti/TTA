#!/usr/bin/env python3
"""
API Gateway Main Entry Point.

This module provides the main entry point for the TTA API Gateway service.
It creates and configures the FastAPI application instance for production deployment.
"""

import logging
import os
import sys

import uvicorn

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.api_gateway.app import create_gateway_app
from src.api_gateway.config import get_gateway_settings


def setup_logging() -> None:
    """Configure logging for the API Gateway service."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("api_gateway.log"),
        ],
    )


def main() -> None:
    """Main entry point for the API Gateway service."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Get configuration
        settings = get_gateway_settings()

        # Create the FastAPI application
        app = create_gateway_app()

        logger.info("Starting TTA API Gateway service...")
        logger.info(f"Host: {settings.host}")
        logger.info(f"Port: {settings.port}")
        logger.info(f"Debug mode: {settings.debug}")

        # Start the server
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            log_level="info" if not settings.debug else "debug",
            reload=settings.debug,
            access_log=True,
        )

    except Exception as e:
        logger.error(f"Failed to start API Gateway service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
