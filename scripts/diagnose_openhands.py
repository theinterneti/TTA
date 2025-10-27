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

    print("\n" + "=" * 80)
    print("OPENHANDS DIAGNOSTIC")
    print("=" * 80)

    # Load config
    config = OpenHandsIntegrationConfig.from_env()
    print("\n✓ Config loaded")
    print(f"  - Workspace: {config.workspace_root}")
    print(f"  - Model preset: {config.model_preset}")
    print(f"  - Custom model: {config.custom_model_id}")

    # Check workspace
    workspace = Path(config.workspace_root)
    print("\n✓ Workspace check:")
    print(f"  - Exists: {workspace.exists()}")
    print(f"  - Is dir: {workspace.is_dir()}")

    if workspace.exists():
        files = list(workspace.glob("**/*.py"))
        print(f"  - Python files: {len(files)}")
        if files:
            for f in files[:5]:
                print(f"    - {f.relative_to(workspace)}")

    # Create client (will use Docker if configured)
    client = create_openhands_client(config)
    print("\n✓ Client created")

    # Simple test task
    task = "List the files in the current directory and create a simple test file named test_hello.py with a single test function"

    print("\n[*] Executing simple test task...")
    print(f"    Task: {task}")

    try:
        result = await client.execute_task(task, timeout=120)

        print("\n✓ Task completed")
        print(f"  - Success: {result.success}")
        print(f"  - Execution time: {result.execution_time:.2f}s")
        print(f"  - Error: {result.error}")

        # Check output
        print("\n✓ Output analysis:")
        output_lines = result.output.split("\n")
        print(f"  - Output lines: {len(output_lines)}")
        print("  - First 20 lines:")
        for line in output_lines[:20]:
            if line.strip():
                print(f"    {line[:100]}")

        # Check for test files
        print("\n✓ Checking for generated files...")
        test_files = list(workspace.glob("**/test_*.py"))
        print(f"  - Test files found: {len(test_files)}")
        for f in test_files:
            print(f"    - {f.relative_to(workspace)}")
            with open(f) as fp:
                content = fp.read()
                print(f"      Size: {len(content)} bytes")
                print(f"      First 200 chars: {content[:200]}")

        # Parse JSON events
        print("\n✓ JSON events in output:")
        events = []
        for line in result.output.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    pass

        print(f"  - Events found: {len(events)}")
        for event in events[:5]:
            print(f"    - {event.get('event_type', 'unknown')}: {str(event)[:100]}")

    except Exception as e:
        logger.error(f"Task failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
