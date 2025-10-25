#!/usr/bin/env python3
"""
Phase 7 Batch 1 - Simple Sequential Task Submission

Submits Batch 1 unit test tasks one by one using the CLI.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

# Batch 1 Work Items
BATCH1_ITEMS = [
    {
        "id": 1,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/adapters.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "simple",
    },
    {
        "id": 2,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/agents.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "moderate",
    },
    {
        "id": 3,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/service.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "moderate",
    },
    {
        "id": 4,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/auth.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "moderate",
    },
    {
        "id": 5,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/characters.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "moderate",
    },
    {
        "id": 6,
        "module": "Player Experience",
        "file": "src/player_experience/managers/player_experience_manager.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "complex",
    },
]


def submit_task(item: dict) -> str | None:
    """Submit a single task using CLI."""
    description = f"Generate unit tests for {Path(item['file']).name} ({item['coverage']} → {item['target']})"

    cmd = [
        "python",
        "-m",
        "src.agent_orchestration.openhands_integration.cli",
        "submit-task",
        "--task-type",
        "unit_test",
        "--description",
        description,
        "--target-file",
        item["file"],
        "--priority",
        "critical",
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
            # Extract task ID from output
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
    """Execute Batch 1 task submission."""
    print("=" * 80)
    print("🚀 PHASE 7 BATCH 1 EXECUTION - TIER 1 UNIT TESTS")
    print("=" * 80)
    print()

    task_ids = []
    results = []

    for i, item in enumerate(BATCH1_ITEMS, 1):
        print(f"[{i}/6] Submitting: {item['module']} - {Path(item['file']).name}")
        print(f"      Coverage: {item['coverage']} → {item['target']}")
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
        "batch": 1,
        "timestamp": datetime.now().isoformat(),
        "total_submitted": len(task_ids),
        "total_items": len(BATCH1_ITEMS),
        "task_ids": task_ids,
        "results": results,
    }

    output_file = Path("/home/thein/recovered-tta-storytelling/batch1_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 80)
    print("✅ BATCH 1 SUBMISSION COMPLETE")
    print(f"   Submitted: {len(task_ids)}/{len(BATCH1_ITEMS)} tasks")
    print(f"   Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
