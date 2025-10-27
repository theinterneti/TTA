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
from datetime import datetime, timedelta


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

    for _task_id, task in tasks.items():
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
    print("\n" + "=" * 80)
    print("📊 PHASE 7 OPTIMIZATION PROGRESS REPORT")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print("\n📈 TASK STATUS:")
    print(f"   ✅ Completed:  {completed:3d}/{total_tasks} ({completion_rate:5.1f}%)")
    print(f"   ⏳ Running:    {running:3d}")
    print(f"   📋 Queued:    {queued:3d}")
    print(f"   ❌ Failed:    {failed:3d}")

    print("\n⏱️  PERFORMANCE METRICS:")
    print(f"   Average Task Time: {avg_time:.2f}s")
    if task_times:
        print(f"   Min Task Time:     {min(task_times):.2f}s")
        print(f"   Max Task Time:     {max(task_times):.2f}s")
    if estimated_time:
        print(f"   Est. Time to Completion: {estimated_time}")

    print("\n🔄 THROUGHPUT:")
    if state.get("queue_stats"):
        stats = state["queue_stats"]
        print(f"   Total Processed: {stats.get('completed', 0)}")
        print(f"   Success Rate:    {stats.get('success_rate', 0):.1f}%")

    if errors_by_type:
        print("\n⚠️  ERROR SUMMARY (Top 5):")
        sorted_errors = sorted(errors_by_type.items(), key=lambda x: x[1], reverse=True)
        for error, count in sorted_errors[:5]:
            print(f"   • {error}: {count}")

    print("\n" + "=" * 80)

    # Show sample of completed tasks
    completed_tasks = [t for t in tasks.values() if t.get("status") == "COMPLETED"]
    if completed_tasks:
        print("\n✅ SAMPLE COMPLETED TASKS (Last 3):")
        for task in completed_tasks[-3:]:
            print(
                f"   • {task['task_id'][:8]}... ({task['task_type']}) - "
                f"{task.get('execution_time', 0):.2f}s"
            )

    # Show sample of failed tasks
    failed_tasks = [t for t in tasks.values() if t.get("status") == "FAILED"]
    if failed_tasks:
        print("\n❌ SAMPLE FAILED TASKS (Last 3):")
        for task in failed_tasks[-3:]:
            error = task.get("error", "Unknown")[:60]
            print(f"   • {task['task_id'][:8]}... ({task['task_type']}) - {error}")

    print("\n" + "=" * 80 + "\n")

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
        print("📡 Starting continuous monitoring (Ctrl+C to stop)...")
        try:
            while True:
                analyze_progress()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    else:
        # Single report
        analyze_progress()
