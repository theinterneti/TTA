#!/usr/bin/env python3
"""
Phase 7 Progress Monitoring Script

Monitors the execution progress of all 41 submitted tasks and collects metrics.
Uses execution log analysis and task queue inspection.
"""

import json
import re
from datetime import datetime
from pathlib import Path


def load_task_ids_from_batch_results() -> list[str]:
    """Load all task IDs from batch result files."""
    task_ids = []
    batch_files = [
        "batch1_results.json",
        "batch2_results.json",
        "batch3_results.json",
        "batch4_results.json",
        "batch5_results.json",
    ]

    for batch_file in batch_files:
        path = Path(batch_file)
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    for result in data.get("results", []):
                        task_id = result.get("task_id")
                        if task_id:
                            task_ids.append(task_id)
            except Exception:
                pass

    return task_ids


def get_queue_stats_from_file() -> dict | None:
    """Get queue statistics from engine state file."""
    state_file = Path("engine_state.json")

    if not state_file.exists():
        return None

    try:
        with open(state_file) as f:
            state = json.load(f)
            return state.get("queue_stats")
    except Exception:
        return None


def analyze_execution_log() -> dict:
    """Analyze execution log for task progress."""
    log_file = Path("phase7_execution.log")
    stats = {
        "completed": 0,
        "failed": 0,
        "running": 0,
        "queued": 0,
        "total_processed": 0,
    }

    if not log_file.exists():
        return stats

    try:
        with open(log_file) as f:
            content = f.read()

            # Count task completions
            completed_matches = re.findall(r"Task ([a-f0-9\-]+) completed", content)
            failed_matches = re.findall(r"Task ([a-f0-9\-]+) failed", content)

            stats["completed"] = len(completed_matches)
            stats["failed"] = len(failed_matches)
            stats["running"] = len(re.findall(r"Worker \d+ started", content))
            stats["total_processed"] = stats["completed"] + stats["failed"]

    except Exception as e:
        print(f"Error analyzing log: {e}")

    return stats


def main():
    """Monitor Phase 7 execution progress."""
    print("=" * 80)
    print("📊 PHASE 7 PROGRESS MONITORING")
    print("=" * 80)
    print()

    # Load task IDs from batch results
    all_task_ids = load_task_ids_from_batch_results()
    print(f"📋 Loaded {len(all_task_ids)} tasks from batch results")
    print()

    # Get queue stats from engine state file
    print("📈 Queue Statistics (from running engine):")
    queue_stats = get_queue_stats_from_file()
    if queue_stats:
        print(json.dumps(queue_stats, indent=2))
    else:
        print("❌ Engine state file not found (engine may not be running)")

    print()

    # Analyze execution log
    print("📊 Execution Log Analysis:")
    log_stats = analyze_execution_log()
    print(json.dumps(log_stats, indent=2))

    print()
    print("=" * 80)
    print("📋 Task Status Summary")
    print("=" * 80)
    print()

    # Calculate completion rate
    total_tasks = len(all_task_ids)
    completed = log_stats.get("completed", 0)
    failed = log_stats.get("failed", 0)
    queued = queue_stats.get("queued", 0) if queue_stats else 0
    running = queue_stats.get("running", 0) if queue_stats else 0

    print("📊 Status Distribution:")
    print(f"  Queued:    {queued:2d}")
    print(f"  Running:   {running:2d}")
    print(f"  Completed: {completed:2d}")
    print(f"  Failed:    {failed:2d}")

    print()
    completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
    print(f"✅ Completion Rate: {completed}/{total_tasks} ({completion_rate:.1f}%)")

    if failed > 0:
        print(f"❌ Failed Tasks: {failed}")

    # Save progress report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tasks": total_tasks,
        "completed": completed,
        "failed": failed,
        "queued": queued,
        "running": running,
        "completion_rate": completion_rate / 100,
    }

    output_file = Path("phase7_progress_report.json")
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print()
    print(f"💾 Progress report saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
