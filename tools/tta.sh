#!/bin/bash

# TTA Orchestrator Script
# This script provides a convenient way to run the TTA Orchestrator

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the main.py script with the provided arguments using UV
uv run python "${SCRIPT_DIR}/src/main.py" "$@"
