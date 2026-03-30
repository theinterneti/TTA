# Logseq: [[TTA.dev/Scripts/Monitor_batch_progress]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""Monitor Phase 7 batch execution progress."""

import re
import time
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
        return

    completed = progress["completed"]
    progress["failed"]
    progress["started"]
    progress["queued"]
    total = progress["total"]

    (completed / total) * 100 if total > 0 else 0


if __name__ == "__main__":
    try:
        while True:
            progress = get_progress()
            print_progress(progress)

            if progress and progress["completed"] >= TOTAL_TASKS:
                break

            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        pass
