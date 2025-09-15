#!/bin/bash
set -e

echo "Removing duplicated files from TTA.prototype root directory..."

# Documentation files
rm -f TTA.prototype/FEATURES.md
rm -f TTA.prototype/GPU_INFERENCE_OPTIMIZATION.md
rm -f TTA.prototype/MODEL_SETUP.md
rm -f TTA.prototype/PERSISTENCE.md
rm -f TTA.prototype/QUEST_SYSTEM.md
rm -f TTA.prototype/tta_project_documentation.md

# Utility files
rm -f TTA.prototype/check_env.py
rm -f TTA.prototype/cleanup.sh
rm -f TTA.prototype/create_project_md.py
rm -f TTA.prototype/populate_neo4j.py
rm -f TTA.prototype/sync-to-gdrive.sh

# Setup files
rm -f TTA.prototype/setup_huggingface.py
rm -f TTA.prototype/setup_ollama.py
rm -f TTA.prototype/update_venv.sh

echo "Duplicated files removed successfully!"
