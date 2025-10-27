#!/usr/bin/env python3
"""Monitor Phase 7 batch execution progress."""

import re
import time
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("phase7_batch_execution_final.log")
TOTAL_TASKS = 41


def get_progress():
    """Get current batch progress."""
    if not LOG_FILE.exists():
        return None

    with open(LOG_FILE) as f:
        content = f.read()

    completed = len(re.findall(r"\[TASK COMPLETE\]", content))
    failed = len(re.findall(r"\[TASK FAILED\]", content))
    started = len(re.findall(r"\[TASK START\]", content))

    return {
        "completed": completed,
        "failed": failed,
        "started": started,
        "queued": TOTAL_TASKS - started,
        "total": TOTAL_TASKS,
    }


def print_progress(progress):
    """Print progress in a nice format."""
    if not progress:
        print("❌ Log file not found")
        return

    completed = progress["completed"]
    failed = progress["failed"]
    started = progress["started"]
    queued = progress["queued"]
    total = progress["total"]

    pct = (completed / total) * 100 if total > 0 else 0

    print(f"\n{'=' * 60}")
    print("📊 PHASE 7 BATCH EXECUTION PROGRESS")
    print(f"{'=' * 60}")
    print(f"⏱️  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ Completed: {completed}/{total} ({pct:.1f}%)")
    print(f"❌ Failed: {failed}")
    print(f"🔄 Started: {started}")
    print(f"⏳ Queued: {queued}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    print("🚀 Starting batch progress monitor...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            progress = get_progress()
            print_progress(progress)

            if progress and progress["completed"] >= TOTAL_TASKS:
                print("✅ BATCH EXECUTION COMPLETE!")
                break

            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\n⏹️  Monitor stopped")
