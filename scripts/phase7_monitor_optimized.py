# Logseq: [[TTA.dev/Scripts/Phase7_monitor_optimized]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Enhanced monitoring script for Phase 7 OpenHands integration with optimizations.

Tracks:
- Task completion rate and throughput
- Average task execution time
- Estimated time to completion
- Error rates and types
- Model usage and performance
"""

import json
import time
from datetime import timedelta


def load_task_queue():
    """Load task queue from file."""
    try:
        with open("task_queue.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_engine_state():
    """Load engine state from file."""
    try:
        with open("engine_state.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def analyze_progress():
    """Analyze and display progress."""
    tasks = load_task_queue()
    state = load_engine_state()

    # Count task statuses
    status_counts = {}
    task_times = []
    errors_by_type = {}

    for task in tasks.values():
        status = task.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1

        # Track execution times
        if task.get("execution_time"):
            task_times.append(task["execution_time"])

        # Track errors
        if task.get("error"):
            error_type = task.get("error", "Unknown")[:50]
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

    total_tasks = len(tasks)
    completed = status_counts.get("COMPLETED", 0)
    failed = status_counts.get("FAILED", 0)
    running = status_counts.get("RUNNING", 0)
    queued = status_counts.get("QUEUED", 0)

    # Calculate metrics
    completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
    avg_time = sum(task_times) / len(task_times) if task_times else 0
    remaining_tasks = total_tasks - completed - failed

    # Estimate time to completion
    if avg_time > 0 and remaining_tasks > 0:
        # Assume 5 concurrent workers
        estimated_seconds = (remaining_tasks / 5) * avg_time
        estimated_time = timedelta(seconds=estimated_seconds)
    else:
        estimated_time = None

    # Display progress

    if task_times:
        pass
    if estimated_time:
        pass

    if state.get("queue_stats"):
        state["queue_stats"]

    if errors_by_type:
        sorted_errors = sorted(errors_by_type.items(), key=lambda x: x[1], reverse=True)
        for _error, _count in sorted_errors[:5]:
            pass

    # Show sample of completed tasks
    completed_tasks = [t for t in tasks.values() if t.get("status") == "COMPLETED"]
    if completed_tasks:
        for task in completed_tasks[-3:]:
            pass

    # Show sample of failed tasks
    failed_tasks = [t for t in tasks.values() if t.get("status") == "FAILED"]
    if failed_tasks:
        for task in failed_tasks[-3:]:
            task.get("error", "Unknown")[:60]

    return {
        "total": total_tasks,
        "completed": completed,
        "failed": failed,
        "running": running,
        "queued": queued,
        "completion_rate": completion_rate,
        "avg_time": avg_time,
        "estimated_time": str(estimated_time) if estimated_time else None,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Watch mode - update every 30 seconds
        try:
            while True:
                analyze_progress()
                time.sleep(30)
        except KeyboardInterrupt:
            pass
    else:
        # Single report
        analyze_progress()
