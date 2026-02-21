#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Setup_mutants_env]]
Setup script for mutation testing environment.

This script ensures that all necessary __init__.py files are present in the
mutants directory so that imports work correctly during mutation testing.

The issue: mutmut only copies files from the specified paths_to_mutate directory,
but doesn't copy parent __init__.py files, causing import errors.

Solution: Copy all parent __init__.py files to the mutants directory.
"""

import shutil
from pathlib import Path


def setup_mutants_environment():
    """Copy necessary __init__.py files to mutants directory."""
    project_root = Path("/home/thein/recovered-tta-storytelling")
    mutants_dir = project_root / "mutants"

    # Check if mutants directory exists
    if not mutants_dir.exists():
        return

    # List of __init__.py files that need to be copied
    init_files_to_copy = [
        "src/__init__.py",
        "src/components/__init__.py",
        "src/components/model_management/__init__.py",
    ]

    for init_file in init_files_to_copy:
        source = project_root / init_file
        dest = mutants_dir / init_file

        # Create parent directories if they don't exist
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file if it exists
        if source.exists():
            shutil.copy2(source, dest)
        else:
            # Create empty __init__.py if source doesn't exist
            dest.touch()


if __name__ == "__main__":
    setup_mutants_environment()