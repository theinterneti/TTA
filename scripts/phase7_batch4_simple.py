#!/usr/bin/env python3
"""
Phase 7 Batch 4 - Documentation (Items 31-40)

Submits documentation tasks:
- Missing READMEs (items 31-33)
- API documentation (items 34-35)
- Architecture documentation (items 36-37)
- Docstring completion (items 38-40)
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Batch 4 Work Items
BATCH4_ITEMS = [
    {
        "id": 31,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/openhands_integration/",
        "task": "Create comprehensive README",
        "complexity": "simple",
    },
    {
        "id": 32,
        "module": "Player Experience",
        "file": "src/player_experience/managers/",
        "task": "Create README for managers",
        "complexity": "simple",
    },
    {
        "id": 33,
        "module": "Components",
        "file": "src/components/redis_integration/",
        "task": "Create Redis integration README",
        "complexity": "simple",
    },
    {
        "id": 34,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/",
        "task": "Generate OpenAPI schema docs",
        "complexity": "simple",
    },
    {
        "id": 35,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/service.py",
        "task": "Document orchestration API",
        "complexity": "moderate",
    },
    {
        "id": 36,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/",
        "task": "Create architecture diagram + docs",
        "complexity": "moderate",
    },
    {
        "id": 37,
        "module": "Player Experience",
        "file": "src/player_experience/",
        "task": "Create component interaction docs",
        "complexity": "moderate",
    },
    {
        "id": 38,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/adapters.py",
        "task": "Add comprehensive docstrings",
        "complexity": "simple",
    },
    {
        "id": 39,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/auth.py",
        "task": "Add comprehensive docstrings",
        "complexity": "simple",
    },
    {
        "id": 40,
        "module": "Components",
        "file": "src/components/gameplay_loop/",
        "task": "Add comprehensive docstrings",
        "complexity": "simple",
    },
]


def submit_task(item: dict) -> str | None:
    """Submit a single task using CLI."""
    description = f"Documentation: {item['task']}"

    cmd = [
        "python",
        "-m",
        "src.agent_orchestration.openhands_integration.cli",
        "submit-task",
        "--task-type",
        "document",
        "--description",
        description,
        "--target-file",
        item["file"],
        "--priority",
        "normal",
        "--complexity",
        item["complexity"],
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/home/thein/recovered-tta-storytelling",
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if "Task submitted:" in output:
                task_id = output.split("Task submitted:")[-1].strip()
                return task_id
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout submitting task")
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def main():
    """Execute Batch 4 task submission."""
    print("=" * 80)
    print("🚀 PHASE 7 BATCH 4 EXECUTION - DOCUMENTATION")
    print("=" * 80)
    print()

    task_ids = []
    results = []

    for i, item in enumerate(BATCH4_ITEMS, 1):
        print(f"[{i:2d}/10] Submitting: {item['module']}")
        print(f"        Task: {item['task']}")
        print(f"        Complexity: {item['complexity']}")

        task_id = submit_task(item)
        if task_id:
            print(f"        ✅ Task ID: {task_id}")
            task_ids.append(task_id)
            results.append({"item": item, "task_id": task_id, "status": "submitted"})
        else:
            print(f"        ❌ Failed to submit")
            results.append({"item": item, "task_id": None, "status": "failed"})

        print()

    # Save results
    output = {
        "batch": 4,
        "timestamp": datetime.now().isoformat(),
        "total_submitted": len(task_ids),
        "total_items": len(BATCH4_ITEMS),
        "task_ids": task_ids,
        "results": results,
    }

    output_file = Path("/home/thein/recovered-tta-storytelling/batch4_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 80)
    print(f"✅ BATCH 4 SUBMISSION COMPLETE")
    print(f"   Submitted: {len(task_ids)}/{len(BATCH4_ITEMS)} tasks")
    print(f"   Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()

