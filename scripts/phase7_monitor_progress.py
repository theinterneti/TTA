#!/usr/bin/env python3
"""
Phase 7 Progress Monitoring Script

Monitors the execution progress of all 47 submitted tasks and collects metrics.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# All task IDs from all batches
ALL_TASK_IDS = [
    # Batch 1
    "efa2bfa5-e2b3-4643-bde3-1fe4843ce7f2",
    "a9b72383-54f9-4618-9dd6-fe564cded13a",
    "9380e8a5-3dd4-47bc-80e7-dfa75177c6e1",
    "3cc3483d-e6dc-40dc-9cb9-0447764d95ca",
    "a95da901-7aac-428e-bc6c-68abf1d3becc",
    "1ce1730e-d449-4cae-8d42-58673cddcabb",
    # Batch 2
    "63a7f25a-3089-4150-8dc3-501d2a678b6a",
    "abd78cb1-b271-4808-84b0-4358ff26868e",
    "ea60b3e8-ec50-4544-a5e9-ff3bfef9ceab",
    "3734b119-fabc-45d6-849f-bd73943e1028",
    "39c08520-23a4-47f9-b227-1ad351405ca2",
    "afd25c7c-7985-44c4-abc8-590e6aac40e7",
    # Batch 3
    "3503341f-d6cc-4c3a-bf58-c6103b88a01d",
    "cd1bc430-09ad-4b5d-a4c0-16d00b6cd55e",
    "23bb3063-67d4-4b07-bc00-ef34ff4bf77d",
    "eacdc228-a30e-4e6d-9c67-32054eedcc0b",
    "4ff0b512-12c6-4857-8182-57c87b207a67",
    "28dc6b30-82da-42a8-9199-ba6121eb6f31",
    "4f93968b-9bad-42a0-bf01-64efbc3a7e93",
    "aeb5f855-83e0-485a-9168-05f4a59e8a10",
    "5a7c9d43-5850-4086-b602-ede11ef2ede2",
    "3cfe4b2b-ae43-4327-9cc5-ec6674c18d9e",
    "264cbd71-25b0-4ecc-a626-2d9fe1234335",
    "38be8ffa-162e-46ae-9fd5-11c889f03d2d",
    # Batch 4
    "00c608db-6998-44e4-97dc-3ffae48ff0ba",
    "5edb8510-15ed-4db6-971d-2c93a9eae292",
    "d0eb4335-1092-4237-88e9-bf7bec894948",
    "5c9347af-09ae-4599-b981-aab0aa02b3b2",
    "b7796d7f-4591-4400-9d47-d4c8f91ed045",
    "6b49d428-7fad-4d29-beb5-12e1f461d9f5",
    "21de6cc5-0cfc-4820-8357-2bc664b0bfbc",
    "ab1b0488-76ae-4aca-952f-39083cef506e",
    "95b7ff01-59bf-4788-96d3-12798b58d00f",
    "ce95d681-df4e-41a0-9245-54afa8795d24",
    # Batch 5
    "a421e993-7105-4efe-9e8f-d5e4ccbe1252",
    "461556c3-3231-49f2-9382-b6d8736852aa",
    "e576de23-6165-4fd3-898f-c64f00e5a513",
    "2e10bbe9-3568-4249-a362-b7d028d89f55",
    "c9ba8439-3de9-4c86-bb5f-2220483afa39",
    "c1c5dee6-7743-4097-8662-d13807fd0c09",
    "345deb95-b73b-4bd4-b5ab-8b9a6e839c56",
]


def get_task_status(task_id: str) -> dict | None:
    """Get status of a single task."""
    cmd = [
        "python",
        "-m",
        "src.agent_orchestration.openhands_integration.cli",
        "get-status",
        "--task-id",
        task_id,
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
            return json.loads(result.stdout)
        else:
            return None
    except Exception:
        return None


def get_queue_stats() -> dict | None:
    """Get queue statistics."""
    cmd = [
        "python",
        "-m",
        "src.agent_orchestration.openhands_integration.cli",
        "queue-stats",
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
            return json.loads(result.stdout)
        else:
            return None
    except Exception:
        return None


def main():
    """Monitor Phase 7 execution progress."""
    print("=" * 80)
    print("📊 PHASE 7 PROGRESS MONITORING")
    print("=" * 80)
    print()

    # Get queue stats
    print("📈 Queue Statistics:")
    stats = get_queue_stats()
    if stats:
        print(json.dumps(stats, indent=2))
    else:
        print("❌ Could not retrieve queue statistics")

    print()
    print("=" * 80)
    print("📋 Task Status Summary")
    print("=" * 80)
    print()

    # Collect task statuses
    statuses = {"pending": 0, "queued": 0, "running": 0, "completed": 0, "failed": 0}
    completed_tasks = []
    failed_tasks = []

    for i, task_id in enumerate(ALL_TASK_IDS, 1):
        status = get_task_status(task_id)
        if status:
            task_status = status.get("status", "unknown")
            statuses[task_status] = statuses.get(task_status, 0) + 1

            if task_status == "completed":
                completed_tasks.append(task_id)
            elif task_status == "failed":
                failed_tasks.append(task_id)

            if i % 10 == 0:
                print(f"  [{i:2d}/47] Checked {i} tasks...")

    print()
    print("📊 Status Distribution:")
    print(f"  Pending:   {statuses['pending']:2d}")
    print(f"  Queued:    {statuses['queued']:2d}")
    print(f"  Running:   {statuses['running']:2d}")
    print(f"  Completed: {statuses['completed']:2d}")
    print(f"  Failed:    {statuses['failed']:2d}")

    print()
    print(f"✅ Completion Rate: {statuses['completed']}/{len(ALL_TASK_IDS)} ({100*statuses['completed']/len(ALL_TASK_IDS):.1f}%)")

    if failed_tasks:
        print(f"❌ Failed Tasks: {len(failed_tasks)}")
        for task_id in failed_tasks[:5]:
            print(f"   - {task_id}")

    # Save progress report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tasks": len(ALL_TASK_IDS),
        "statuses": statuses,
        "completed_count": statuses["completed"],
        "failed_count": statuses["failed"],
        "completion_rate": statuses["completed"] / len(ALL_TASK_IDS),
    }

    output_file = Path("/home/thein/recovered-tta-storytelling/phase7_progress_report.json")
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print()
    print(f"💾 Progress report saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()

