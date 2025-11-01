"""Google ADK configuration for TTA Agent Orchestration.

This module provides centralized configuration for Google's Agent Development Kit (ADK)
used in TTA's multi-agent orchestration system.

Configuration includes:
- Gemini 2.0 Flash model settings
- API authentication (via environment variables)
- Agent configuration
- Workflow configuration
- Session state management
- Error handling
- Observability settings

Note: Google ADK uses environment variables for authentication (GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS).
      No explicit Config class is needed - agents accept model names directly.
"""

import os
from typing import Any


def get_gemini_api_key() -> str:
    """Get Gemini API key from environment variables.

    Returns:
        str: Gemini API key

    Raises:
        ValueError: If GEMINI_API_KEY environment variable is not set
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    return api_key


def get_google_cloud_project() -> str:
    """Get Google Cloud project ID from environment variables.

    Returns:
        str: Google Cloud project ID (defaults to 'tta-project')
    """
    return os.getenv("GOOGLE_CLOUD_PROJECT", "tta-project")


# Default Model Name for TTA
DEFAULT_MODEL = "gemini-2.0-flash"  # Optimized for speed, unlimited usage


# Model Configuration (for GenerateContentConfig)
MODEL_CONFIG: dict[str, Any] = {
    "temperature": 0.7,  # Balanced creativity and consistency
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048,
}


# Agent Configuration
AGENT_CONFIG: dict[str, Any] = {
    "input_processor": {
        "name": "InputProcessorAgent",
        "description": "Processes user input and extracts therapeutic intent",
        "timeout": 10,  # seconds
        "max_retries": 3,
    },
    "world_builder": {
        "name": "WorldBuilderAgent",
        "description": "Builds and updates therapeutic world state",
        "timeout": 15,  # seconds
        "max_retries": 3,
    },
    "narrative_generator": {
        "name": "NarrativeGeneratorAgent",
        "description": "Generates therapeutic narrative content",
        "timeout": 20,  # seconds
        "max_retries": 3,
    },
}


# Workflow Configuration
WORKFLOW_CONFIG: dict[str, Any] = {
    "sequential": {
        "name": "SequentialWorkflow",
        "description": "Sequential agent execution (IPA → WBA → NGA)",
        "timeout": 45,  # seconds (sum of agent timeouts)
    },
    "parallel": {
        "name": "ParallelWorkflow",
        "description": "Parallel agent execution for concurrent operations",
        "timeout": 20,  # seconds (max of agent timeouts)
    },
    "loop": {
        "name": "LoopWorkflow",
        "description": "Iterative refinement workflow",
        "max_iterations": 3,
        "timeout": 60,  # seconds
    },
}


# Session State Keys
SESSION_STATE_KEYS = {
    "processed_input": "processed_input",  # Output from InputProcessorAgent
    "world_state": "world_state",  # Output from WorldBuilderAgent
    "narrative_response": "narrative_response",  # Output from NarrativeGeneratorAgent
    "user_input": "user_input",  # Original user input
    "session_id": "session_id",  # Session identifier
    "iteration_count": "iteration_count",  # For loop workflows
}


# Error Handling Configuration
ERROR_CONFIG: dict[str, Any] = {
    "max_retries": 3,
    "retry_delay": 1.0,  # seconds
    "exponential_backoff": True,
    "backoff_multiplier": 2.0,
    "max_retry_delay": 10.0,  # seconds
}


# Observability Configuration
OBSERVABILITY_CONFIG: dict[str, Any] = {
    "enable_logging": True,
    "log_level": "INFO",
    "enable_metrics": True,
    "enable_tracing": True,
    "trace_sample_rate": 1.0,  # 100% sampling for development
}


__all__ = [
    "DEFAULT_MODEL",
    "MODEL_CONFIG",
    "AGENT_CONFIG",
    "WORKFLOW_CONFIG",
    "SESSION_STATE_KEYS",
    "ERROR_CONFIG",
    "OBSERVABILITY_CONFIG",
    "get_gemini_api_key",
    "get_google_cloud_project",
]
