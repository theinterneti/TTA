#!/usr/bin/env python3
"""
NotebookLM Query Helper

Quick utility to query the TTA research notebook for architectural guidance,
best practices, and implementation patterns.

Usage:
    # Command line
    uv run python scripts/query_notebook_helper.py "How should I implement agent primitives?"

    # From Python
    from scripts.query_notebook_helper import query_notebook
    response = await query_notebook("What are MCP security best practices?")
"""

import asyncio
import sys
from pathlib import Path


async def query_notebook(
    question: str, notebook_id: str | None = None, timeout: int = 15
) -> str:
    """
    Query the TTA research notebook.

    Args:
        question: The question to ask the notebook
        notebook_id: Optional specific notebook ID (uses default from config if not provided)
        timeout: Maximum seconds to wait for response (default: 15)

    Returns:
        The notebook's response as a string

    Raises:
        Exception: If connection fails or query times out
    """
    try:
        from notebooklm_mcp.client import NotebookLMClient  # noqa: PLC0415
        from notebooklm_mcp.config import load_config  # noqa: PLC0415
    except ImportError:
        return "❌ NotebookLM MCP not available. Install with: uv add notebooklm-mcp"

    # Load configuration
    config_path = Path(__file__).parent.parent / "notebooklm-config.json"
    if not config_path.exists():
        return f"❌ Configuration not found at {config_path}"

    try:
        config = load_config(str(config_path))
        target_notebook = notebook_id or config.default_notebook_id

        client = NotebookLMClient(config)

        try:
            # Connect to notebook
            await client.start()
            await client.authenticate()
            await client.navigate_to_notebook(target_notebook)

            # Send query
            await client.send_message(question)

            # Wait for response with timeout
            await asyncio.sleep(min(timeout, 10))
            return await client.get_response()

        finally:
            await client.close()

    except Exception as e:
        return f"❌ Query failed: {str(e)}"


async def quick_query(question: str) -> None:
    """Quick command-line query with formatted output."""
    print("📓 Querying TTA Research Notebook...")  # noqa: T201
    print(f"💬 Question: {question}")  # noqa: T201
    print()  # noqa: T201

    response = await query_notebook(question)

    print("📥 Response:")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print(response)  # noqa: T201
    print("=" * 70)  # noqa: T201


def main():
    """Command-line entry point."""
    if len(sys.argv) < 2:
        print()  # noqa: T201
        print("Examples:")  # noqa: T201
        print("  'What are the three layers of the AI-Native framework?'")  # noqa: T201
        print("  'How should I implement agent primitives in Python?'")  # noqa: T201
        print("  'What are MCP security best practices?'")  # noqa: T201
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    asyncio.run(quick_query(question))


if __name__ == "__main__":
    main()
