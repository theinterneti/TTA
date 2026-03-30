#!/bin/bash
# Wrapper script for running mutation tests with correct PYTHONPATH
# This script ensures tests run from the project root, not the mutants directory

# Set PYTHONPATH to include project root (not mutants directory)
export PYTHONPATH=/home/thein/repos/recovered-tta-storytelling:$PYTHONPATH

# CRITICAL: Change to project root, not mutants directory
# This ensures imports work correctly
cd /home/thein/repos/recovered-tta-storytelling

# Run pytest with the provided arguments
# The tests will import from the project root, not the mutants directory
uv run pytest "$@"
