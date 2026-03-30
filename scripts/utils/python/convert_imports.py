#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Utils/Python/Convert_imports]]
Script to convert absolute imports from src to relative imports in the TTA.prototype repository.
"""

import os
import re
import sys


def get_relative_import(file_path, import_path):
    """
    Convert an absolute import to a relative import.

    Args:
        file_path: Path to the file containing the import
        import_path: The absolute import path (e.g., 'src.models.llm_client')

    Returns:
        The relative import path
    """
    # Remove 'src.' from the import path
    import_path = import_path.replace("src.", "")

    # Get the directory of the file relative to src
    file_dir = os.path.dirname(os.path.relpath(file_path, "TTA.prototype/src"))

    # Split the import path into components
    import_components = import_path.split(".")

    # Calculate the number of parent directories to go up
    file_dirs = file_dir.split(os.sep) if file_dir != "." else []
    import_dirs = import_components[:-1]

    # Find common prefix
    common_prefix_len = 0
    for i in range(min(len(file_dirs), len(import_dirs))):
        if file_dirs[i] == import_dirs[i]:
            common_prefix_len += 1
        else:
            break

    # Calculate relative path
    up_levels = len(file_dirs) - common_prefix_len
    down_path = import_dirs[common_prefix_len:]

    # Construct the relative import
    if up_levels == 0 and not down_path:
        # Same directory
        return f".{import_components[-1]}"
    if up_levels > 0:
        # Need to go up
        rel_import = "." * (up_levels + 1)
        if down_path:
            rel_import += ".".join(down_path) + "."
        rel_import += import_components[-1]
        return rel_import
    # Need to go down
    rel_import = "."
    if down_path:
        rel_import += ".".join(down_path) + "."
    rel_import += import_components[-1]
    return rel_import


def convert_imports(file_path, dry_run=False):
    """
    Convert absolute imports to relative imports in a file.

    Args:
        file_path: Path to the file to convert
        dry_run: If True, don't actually modify the file

    Returns:
        True if the file was modified, False otherwise
    """
    with open(file_path) as f:
        content = f.read()

    # Find all imports from src
    matches = re.findall(r"^from src\.([^\s]+) import ([^\n]+)", content, re.MULTILINE)

    if not matches:
        return False

    modified_content = content

    for import_path, imported_items in matches:
        # Construct the absolute import
        abs_import = f"from src.{import_path} import {imported_items}"

        # Get the relative import
        rel_import_path = get_relative_import(file_path, f"src.{import_path}")
        rel_import = f"from {rel_import_path} import {imported_items}"

        # Replace the absolute import with the relative import
        modified_content = modified_content.replace(abs_import, rel_import)

    if modified_content != content and not dry_run:
        with open(file_path, "w") as f:
            f.write(modified_content)
        return True
    if modified_content != content:
        return True
    return None


def main():
    """Main function."""
    if len(sys.argv) < 2:
        sys.exit(1)

    directory = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.isdir(directory):
        sys.exit(1)

    modified_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    if convert_imports(file_path, dry_run):
                        modified_files.append(os.path.relpath(file_path, directory))
                except Exception:
                    pass

    if not modified_files:
        return

    for file_path in modified_files:
        pass


if __name__ == "__main__":
    main()
