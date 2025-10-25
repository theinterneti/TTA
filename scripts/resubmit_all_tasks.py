#!/usr/bin/env python3
"""
Re-submit all tasks from batch result files to the execution queue.
"""

import json
import subprocess
from pathlib import Path


def submit_task(item):
    """Submit a single task using the CLI."""
    # Determine task type and description based on item content
    if "coverage" in item:
        task_type = "unit_test"
        description = f"Generate unit tests for {item['file']} (coverage: {item['coverage']} → {item['target']})"
    elif "refactoring" in item.get("type", "").lower():
        task_type = "refactor"
        description = f"Refactor {item['file']}: {item.get('description', 'Improve code quality')}"
    elif "documentation" in item.get("type", "").lower():
        task_type = "documentation"
        description = f"Create documentation for {item['file']}"
    else:
        task_type = "code_generation"
        description = f"Generate code for {item['file']}"

    cmd = [
        "python",
        "-m",
        "src.agent_orchestration.openhands_integration.cli",
        "submit-task",
        "--task-type",
        task_type,
        "--description",
        description,
        "--target-file",
        item["file"],
        "--complexity",
        item.get("complexity", "moderate"),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/thein/recovered-tta-storytelling"
        )

        if result.returncode == 0:
            output = result.stdout
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
    """Re-submit all tasks from batch results."""
    print("=" * 80)
    print("🔄 RE-SUBMITTING ALL TASKS FROM BATCH RESULTS")
    print("=" * 80)
    print()

    batch_files = sorted(Path(".").glob("batch[1-5]_results.json"))
    total_submitted = 0

    for batch_file in batch_files:
        print(f"📂 Processing: {batch_file}")

        with open(batch_file) as f:
            batch_data = json.load(f)

        for result in batch_data.get("results", []):
            item = result.get("item", {})
            if not item:
                continue

            print(f"  Submitting: {item.get('module')} - {Path(item.get('file', '')).name}")
            task_id = submit_task(item)
            if task_id:
                print(f"    ✅ Task ID: {task_id}")
                total_submitted += 1
            else:
                print(f"    ❌ Failed to submit")

        print()

    print("=" * 80)
    print(f"✅ RE-SUBMISSION COMPLETE: {total_submitted} tasks submitted")
    print("=" * 80)


if __name__ == "__main__":
    main()

