#!/usr/bin/env python3
"""
Phase 7 Batch 2 - Tier 2 Unit Tests (Items 7-12)

Submits high-priority unit test tasks for:
- websocket_manager.py, docker_client.py (5% → 70%)
- worlds.py, production_readiness.py (3% → 70%)
- neo4j manager/query_builder (27% → 70%)
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Batch 2 Work Items
BATCH2_ITEMS = [
    {
        "id": 7,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/realtime/websocket_manager.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "complex",
    },
    {
        "id": 8,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/openhands_integration/docker_client.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "complex",
    },
    {
        "id": 9,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/worlds.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "moderate",
    },
    {
        "id": 10,
        "module": "Player Experience",
        "file": "src/player_experience/production_readiness.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "complex",
    },
    {
        "id": 11,
        "module": "Neo4j Component",
        "file": "src/components/neo4j_integration/manager.py",
        "coverage": "27%",
        "target": "70%",
        "complexity": "moderate",
    },
    {
        "id": 12,
        "module": "Neo4j Component",
        "file": "src/components/neo4j_integration/query_builder.py",
        "coverage": "27%",
        "target": "70%",
        "complexity": "simple",
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
        "high",
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
    """Execute Batch 2 task submission."""
    print("=" * 80)
    print("🚀 PHASE 7 BATCH 2 EXECUTION - TIER 2 UNIT TESTS")
    print("=" * 80)
    print()

    task_ids = []
    results = []

    for i, item in enumerate(BATCH2_ITEMS, 1):
        print(f"[{i}/6] Submitting: {item['module']} - {Path(item['file']).name}")
        print(f"      Coverage: {item['coverage']} → {item['target']}")
        print(f"      Complexity: {item['complexity']}")

        task_id = submit_task(item)
        if task_id:
            print(f"      ✅ Task ID: {task_id}")
            task_ids.append(task_id)
            results.append({"item": item, "task_id": task_id, "status": "submitted"})
        else:
            print(f"      ❌ Failed to submit")
            results.append({"item": item, "task_id": None, "status": "failed"})

        print()

    # Save results
    output = {
        "batch": 2,
        "timestamp": datetime.now().isoformat(),
        "total_submitted": len(task_ids),
        "total_items": len(BATCH2_ITEMS),
        "task_ids": task_ids,
        "results": results,
    }

    output_file = Path("/home/thein/recovered-tta-storytelling/batch2_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 80)
    print(f"✅ BATCH 2 SUBMISSION COMPLETE")
    print(f"   Submitted: {len(task_ids)}/{len(BATCH2_ITEMS)} tasks")
    print(f"   Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()

