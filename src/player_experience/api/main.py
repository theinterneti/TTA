"""
Main entry point for running the Player Experience API server.

This module provides a CLI interface for starting the FastAPI server
with appropriate configuration.
"""

import uvicorn

from .config import get_settings


def run_server():
    """Run the FastAPI server with uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "src.player_experience.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run_server()
