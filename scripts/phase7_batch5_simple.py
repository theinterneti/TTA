#!/usr/bin/env python3
"""
Phase 7 Batch 5 - Code Generation (Items 41-47)

Submits code generation tasks:
- Utility functions (items 41-42)
- Validators (items 43-44)
- Configuration helpers (items 45-47)
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

# Batch 5 Work Items
BATCH5_ITEMS = [
    {
        "id": 41,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/utils/",
        "task": "Generate validation helpers",
        "complexity": "simple",
    },
    {
        "id": 42,
        "module": "Player Experience",
        "file": "src/player_experience/utils/",
        "task": "Generate response formatters",
        "complexity": "simple",
    },
    {
        "id": 43,
        "module": "Player Experience",
        "file": "src/player_experience/validators/",
        "task": "Generate Pydantic validators",
        "complexity": "simple",
    },
    {
        "id": 44,
        "module": "Components",
        "file": "src/components/gameplay_loop/validators/",
        "task": "Generate game state validators",
        "complexity": "moderate",
    },
    {
        "id": 45,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/config/",
        "task": "Generate config loaders",
        "complexity": "simple",
    },
    {
        "id": 46,
        "module": "Player Experience",
        "file": "src/player_experience/config/",
        "task": "Generate environment validators",
        "complexity": "simple",
    },
    {
        "id": 47,
        "module": "Components",
        "file": "src/components/",
        "task": "Generate component factory functions",
        "complexity": "moderate",
    },
]


def submit_task(item: dict) -> str | None:
    """Submit a single task using CLI."""
    description = f"Code generation: {item['task']}"

    cmd = [
        "python",
        "-m",
        "src.agent_orchestration.openhands_integration.cli",
        "submit-task",
        "--task-type",
        "generate",
        "--description",
        description,
        "--target-file",
        item["file"],
        "--priority",
        "low",
        "--complexity",
        item["complexity"],
    ]

    try:
        result = subprocess.run(
            cmd,
            check=False,
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
        print("❌ Timeout submitting task")
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def main():
    """Execute Batch 5 task submission."""
    print("=" * 80)
    print("🚀 PHASE 7 BATCH 5 EXECUTION - CODE GENERATION")
    print("=" * 80)
    print()

    task_ids = []
    results = []

    for i, item in enumerate(BATCH5_ITEMS, 1):
        print(f"[{i}/7] Submitting: {item['module']}")
        print(f"      Task: {item['task']}")
        print(f"      Complexity: {item['complexity']}")

        task_id = submit_task(item)
        if task_id:
            print(f"      ✅ Task ID: {task_id}")
            task_ids.append(task_id)
            results.append({"item": item, "task_id": task_id, "status": "submitted"})
        else:
            print("      ❌ Failed to submit")
            results.append({"item": item, "task_id": None, "status": "failed"})

        print()

    # Save results
    output = {
        "batch": 5,
        "timestamp": datetime.now().isoformat(),
        "total_submitted": len(task_ids),
        "total_items": len(BATCH5_ITEMS),
        "task_ids": task_ids,
        "results": results,
    }

    output_file = Path("/home/thein/recovered-tta-storytelling/batch5_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 80)
    print("✅ BATCH 5 SUBMISSION COMPLETE")
    print(f"   Submitted: {len(task_ids)}/{len(BATCH5_ITEMS)} tasks")
    print(f"   Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
