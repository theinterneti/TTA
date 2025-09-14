#!/usr/bin/env python3
"""
Agent Orchestration Main Entry Point.

This module provides the main entry point for the TTA Agent Orchestration service.
It creates and configures the FastAPI application instance for production deployment.
"""

import logging
import os
import sys

import uvicorn

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.components.agent_orchestration_component import AgentOrchestrationComponent


def setup_logging() -> None:
    """Configure logging for the Agent Orchestration service."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("agent_orchestration.log"),
        ],
    )


def get_config() -> dict:
    """Get configuration from environment variables."""
    # Default to localhost for security, allow override via environment
    default_host = "127.0.0.1"  # More secure default than 0.0.0.0
    if os.getenv("AGENT_ORCHESTRATION_ALLOW_ALL_INTERFACES", "false").lower() == "true":
        default_host = "0.0.0.0"

    return {
        "host": os.getenv("AGENT_ORCHESTRATION_HOST", default_host),
        "port": int(os.getenv("AGENT_ORCHESTRATION_PORT", "8503")),
        "debug": os.getenv("AGENT_ORCHESTRATION_DEBUG", "false").lower() == "true",
        "workers": int(os.getenv("AGENT_ORCHESTRATION_WORKERS", "1")),
    }


def create_agent_orchestration_app():
    """Create and configure the Agent Orchestration FastAPI application."""
    # Create component with basic configuration
    config = {
        "agent_orchestration.port": get_config()["port"],
        "agent_orchestration.diagnostics.enabled": True,
    }

    component = AgentOrchestrationComponent(config)

    # Start the component to initialize services
    component._start_impl()

    # Create the diagnostics app (which includes health endpoints)
    app = component._create_diagnostics_app()

    if app is None:
        # Fallback: create a minimal FastAPI app
        from fastapi import FastAPI

        app = FastAPI(
            title="TTA Agent Orchestration Service",
            description="Agent orchestration and workflow management service",
            version="1.0.0",
        )

        @app.get("/health")
        async def health():
            return {"status": "healthy", "service": "agent_orchestration"}

    return app


def main() -> None:
    """Main entry point for the Agent Orchestration service."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Get configuration
        config = get_config()

        # Create the FastAPI application
        app = create_agent_orchestration_app()

        logger.info("Starting TTA Agent Orchestration service...")
        logger.info(f"Host: {config['host']}")
        logger.info(f"Port: {config['port']}")
        logger.info(f"Debug mode: {config['debug']}")
        logger.info(f"Workers: {config['workers']}")

        # Start the server
        uvicorn.run(
            app,
            host=config["host"],
            port=config["port"],
            log_level="info" if not config["debug"] else "debug",
            reload=config["debug"],
            access_log=True,
            workers=config["workers"] if not config["debug"] else 1,
        )

    except Exception as e:
        logger.error(f"Failed to start Agent Orchestration service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
