#!/usr/bin/env python3
"""
Phase 7 Batch 3 - Code Refactoring (Items 19-30)

Submits code refactoring tasks:
- Error handling standardization (items 19-21)
- SOLID principle violations (items 22-24)
- Code duplication removal (items 25-27)
- Type hints completion (items 28-30)
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

# Batch 3 Work Items
BATCH3_ITEMS = [
    {
        "id": 19,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/therapeutic_safety.py",
        "task": "Standardize exception handling (50+ linting issues)",
        "complexity": "moderate",
    },
    {
        "id": 20,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/realtime/websocket_manager.py",
        "task": "Add error recovery patterns (30+ linting issues)",
        "complexity": "moderate",
    },
    {
        "id": 21,
        "module": "Player Experience",
        "file": "src/player_experience/production_readiness.py",
        "task": "Standardize error handling (40+ linting issues)",
        "complexity": "moderate",
    },
    {
        "id": 22,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/adapters.py",
        "task": "Fix import resolution errors + type mismatches",
        "complexity": "complex",
    },
    {
        "id": 23,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/agents.py",
        "task": "Fix type mismatches (dict vs AgentConfig)",
        "complexity": "moderate",
    },
    {
        "id": 24,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/auth.py",
        "task": "Reduce cyclomatic complexity (35+ linting issues)",
        "complexity": "moderate",
    },
    {
        "id": 25,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/openhands_integration/",
        "task": "Extract common retry logic",
        "complexity": "simple",
    },
    {
        "id": 26,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/",
        "task": "Extract common validation logic",
        "complexity": "simple",
    },
    {
        "id": 27,
        "module": "Components",
        "file": "src/components/",
        "task": "Extract common error handling patterns",
        "complexity": "moderate",
    },
    {
        "id": 28,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/service.py",
        "task": "Add missing type hints",
        "complexity": "simple",
    },
    {
        "id": 29,
        "module": "Player Experience",
        "file": "src/player_experience/managers/",
        "task": "Add missing type hints (all files)",
        "complexity": "simple",
    },
    {
        "id": 30,
        "module": "Components",
        "file": "src/components/gameplay_loop/",
        "task": "Add missing type hints",
        "complexity": "simple",
    },
]


def submit_task(item: dict) -> str | None:
    """Submit a single task using CLI."""
    description = f"Refactor {Path(item['file']).name}: {item['task']}"

    cmd = [
        "python",
        "-m",
        "src.agent_orchestration.openhands_integration.cli",
        "submit-task",
        "--task-type",
        "refactor",
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
    """Execute Batch 3 task submission."""
    print("=" * 80)
    print("🚀 PHASE 7 BATCH 3 EXECUTION - CODE REFACTORING")
    print("=" * 80)
    print()

    task_ids = []
    results = []

    for i, item in enumerate(BATCH3_ITEMS, 1):
        print(f"[{i:2d}/12] Submitting: {item['module']}")
        print(f"        Task: {item['task']}")
        print(f"        Complexity: {item['complexity']}")

        task_id = submit_task(item)
        if task_id:
            print(f"        ✅ Task ID: {task_id}")
            task_ids.append(task_id)
            results.append({"item": item, "task_id": task_id, "status": "submitted"})
        else:
            print("        ❌ Failed to submit")
            results.append({"item": item, "task_id": None, "status": "failed"})

        print()

    # Save results
    output = {
        "batch": 3,
        "timestamp": datetime.now().isoformat(),
        "total_submitted": len(task_ids),
        "total_items": len(BATCH3_ITEMS),
        "task_ids": task_ids,
        "results": results,
    }

    output_file = Path("/home/thein/recovered-tta-storytelling/batch3_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 80)
    print("✅ BATCH 3 SUBMISSION COMPLETE")
    print(f"   Submitted: {len(task_ids)}/{len(BATCH3_ITEMS)} tasks")
    print(f"   Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
