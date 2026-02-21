# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Diagnose_openhands]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Diagnostic script to understand OpenHands test generation behavior.

Checks:
1. Workspace directory structure
2. Whether test files are being created
3. Docker execution output
4. File extraction patterns
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.client import create_openhands_client
from agent_orchestration.openhands_integration.config import OpenHandsIntegrationConfig


async def main():
    """Run diagnostic checks."""

    # Load config
    config = OpenHandsIntegrationConfig.from_env()

    # Check workspace
    workspace = Path(config.workspace_root)

    if workspace.exists():
        files = list(workspace.glob("**/*.py"))
        if files:
            for f in files[:5]:
                pass

    # Create client (will use Docker if configured)
    client = create_openhands_client(config)

    # Simple test task
    task = "List the files in the current directory and create a simple test file named test_hello.py with a single test function"

    try:
        result = await client.execute_task(task, timeout=120)

        # Check output
        output_lines = result.output.split("\n")
        for line in output_lines[:20]:
            if line.strip():
                pass

        # Check for test files
        test_files = list(workspace.glob("**/test_*.py"))
        for f in test_files:
            with open(f) as fp:
                fp.read()

        # Parse JSON events
        events = []
        for line in result.output.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    pass

        for event in events[:5]:
            pass

    except Exception as e:
        logger.error(f"Task failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
