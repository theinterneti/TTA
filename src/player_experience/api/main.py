"""
Main entry point for running the Player Experience API server.

This module provides a CLI interface for starting the FastAPI server
with appropriate configuration.
"""

import uvicorn
from src.player_experience.api.app import create_app
from src.player_experience.api.config import settings


def run_server():
    """Run the FastAPI server with uvicorn."""
    if settings.reload:
        # Use import string for reload functionality
        uvicorn.run(
            "src.player_experience.api.app:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.lower(),
        )
    else:
        # Create the app instance directly for production
        app = create_app()
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            reload=False,
            log_level=settings.log_level.lower(),
        )


if __name__ == "__main__":
    run_server()