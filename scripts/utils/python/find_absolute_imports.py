#!/usr/bin/env python3
"""
Script to find absolute imports from src in the TTA.prototype repository.
"""

import os
import re
import sys


def find_absolute_imports(directory):
    """Find all Python files with absolute imports from src."""
    absolute_imports = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path) as f:
                    try:
                        content = f.read()
                        # Find all imports from src
                        matches = re.findall(
                            r"^from src\..*|^import src\..*", content, re.MULTILINE
                        )
                        if matches:
                            relative_path = os.path.relpath(file_path, directory)
                            absolute_imports.append((relative_path, matches))
                    except UnicodeDecodeError:
                        pass

    return absolute_imports


def main():
    """Main function."""
    if len(sys.argv) != 2:
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        sys.exit(1)

    absolute_imports = find_absolute_imports(directory)

    if not absolute_imports:
        return

    for _file_path, imports in absolute_imports:
        for _imp in imports:
            pass


if __name__ == "__main__":
    main()
