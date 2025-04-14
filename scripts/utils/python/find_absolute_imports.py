#!/usr/bin/env python3
"""
Script to find absolute imports from src in the TTA.prototype repository.
"""

import os
import re
import sys
from pathlib import Path

def find_absolute_imports(directory):
    """Find all Python files with absolute imports from src."""
    absolute_imports = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    try:
                        content = f.read()
                        # Find all imports from src
                        matches = re.findall(r'^from src\..*|^import src\..*', content, re.MULTILINE)
                        if matches:
                            relative_path = os.path.relpath(file_path, directory)
                            absolute_imports.append((relative_path, matches))
                    except UnicodeDecodeError:
                        print(f"Error reading {file_path}")
    
    return absolute_imports

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    absolute_imports = find_absolute_imports(directory)
    
    if not absolute_imports:
        print("No absolute imports found.")
        return
    
    print(f"Found {len(absolute_imports)} files with absolute imports:")
    for file_path, imports in absolute_imports:
        print(f"\n{file_path}:")
        for imp in imports:
            print(f"  {imp}")

if __name__ == "__main__":
    main()
