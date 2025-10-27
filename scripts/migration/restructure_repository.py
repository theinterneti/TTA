#!/usr/bin/env python3
"""
Repository Restructuring Script for TTA Monorepo Migration

This script automates the migration from the current structure to Option A
(Monorepo with Clear Namespace Separation).

Usage:
    python scripts/migration/restructure_repository.py --dry-run  # Preview changes
    python scripts/migration/restructure_repository.py --execute  # Execute migration
    python scripts/migration/restructure_repository.py --rollback # Rollback changes
"""

import argparse
import json
import shutil
from pathlib import Path

# Migration mapping: source -> destination
MIGRATION_MAP = {
    # AI Framework components
    "src/agent_orchestration": "packages/tta-ai-framework/src/tta_ai/orchestration",
    "src/components/model_management": "packages/tta-ai-framework/src/tta_ai/models",
    "src/ai_components/prompts": "packages/tta-ai-framework/src/tta_ai/prompts",

    # Narrative Engine components
    "src/components/gameplay_loop/narrative": "packages/tta-narrative-engine/src/tta_narrative/generation",
    "src/components/narrative_arc_orchestrator": "packages/tta-narrative-engine/src/tta_narrative/orchestration",
    "src/components/narrative_coherence": "packages/tta-narrative-engine/src/tta_narrative/coherence",
}

# Import path replacements
IMPORT_REPLACEMENTS = {
    # AI Framework imports
    "from tta_ai.orchestration": "from tta_ai.orchestration",
    "from tta_ai.models": "from tta_ai.models",
    "from tta_ai.prompts": "from tta_ai.prompts",
    "import tta_ai.orchestration": "import tta_ai.orchestration",
    "import tta_ai.models": "import tta_ai.models",
    "import tta_ai.prompts": "import tta_ai.prompts",

    # Narrative Engine imports
    "from tta_narrative.generation": "from tta_narrative.generation",
    "from tta_narrative.orchestration": "from tta_narrative.orchestration",
    "from tta_narrative.coherence": "from tta_narrative.coherence",
    "import tta_narrative.generation": "import tta_narrative.generation",
    "import tta_narrative.orchestration": "import tta_narrative.orchestration",
    "import tta_narrative.coherence": "import tta_narrative.coherence",
}

# Directories to delete
OBSOLETE_DIRS = [
    "tta/prod",
    "tta/prototype",
    "ai-components/tta.dev",
    "narrative-engine/tta.prototype",
]

# Files to delete
OBSOLETE_FILES = [
    ".gitmodules",
    "scripts/fix_submodules.sh",
    "scripts/setup_submodules.sh",
]


class RepositoryRestructurer:
    """Handles the repository restructuring process."""

    def __init__(self, repo_root: Path, dry_run: bool = True):
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.migration_log: list[dict] = []
        self.import_updates: list[dict] = []

    def log_action(self, action: str, source: str, destination: str = "", status: str = "pending"):
        """Log a migration action."""
        entry = {
            "action": action,
            "source": source,
            "destination": destination,
            "status": status,
        }
        self.migration_log.append(entry)

        if not self.dry_run:
            print(f"  [{status.upper()}] {action}: {source} -> {destination}")
        else:
            print(f"  [DRY-RUN] {action}: {source} -> {destination}")

    def create_directory_structure(self):
        """Create the new directory structure."""
        print("\n=== Creating New Directory Structure ===")

        new_dirs = [
            "packages/tta-ai-framework/src/tta_ai",
            "packages/tta-ai-framework/tests",
            "packages/tta-narrative-engine/src/tta_narrative",
            "packages/tta-narrative-engine/tests",
            "config/development",
            "config/staging",
            "config/production",
            "deployment/docker/development",
            "deployment/docker/staging",
            "deployment/docker/production",
        ]

        for dir_path in new_dirs:
            full_path = self.repo_root / dir_path
            self.log_action("CREATE_DIR", dir_path)

            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
                # Create __init__.py for Python packages
                if "src/" in dir_path and not dir_path.endswith("tests"):
                    init_file = full_path / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text('"""Package initialization."""\n')

    def migrate_code(self):
        """Migrate code to new locations."""
        print("\n=== Migrating Code ===")

        for source, destination in MIGRATION_MAP.items():
            source_path = self.repo_root / source
            dest_path = self.repo_root / destination

            if not source_path.exists():
                self.log_action("SKIP", source, destination, "source_not_found")
                continue

            self.log_action("MOVE", source, destination, "in_progress")

            if not self.dry_run:
                # Ensure destination parent exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Move the directory
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    self.log_action("MOVE", source, destination, "completed")
                else:
                    shutil.copy2(source_path, dest_path)
                    self.log_action("MOVE", source, destination, "completed")

    def update_imports(self):
        """Update import statements across all Python files."""
        print("\n=== Updating Import Statements ===")

        # Find all Python files
        python_files = list(self.repo_root.glob("**/*.py"))

        # Exclude certain directories
        exclude_patterns = [".venv", "venv", "__pycache__", ".git", "node_modules"]
        python_files = [
            f for f in python_files
            if not any(pattern in str(f) for pattern in exclude_patterns)
        ]

        print(f"Found {len(python_files)} Python files to process")

        for py_file in python_files:
            try:
                content = py_file.read_text()
                original_content = content

                # Apply import replacements
                for old_import, new_import in IMPORT_REPLACEMENTS.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)

                # If content changed, update the file
                if content != original_content:
                    relative_path = py_file.relative_to(self.repo_root)
                    self.import_updates.append({
                        "file": str(relative_path),
                        "changes": sum(1 for old in IMPORT_REPLACEMENTS if old in original_content)
                    })

                    if not self.dry_run:
                        py_file.write_text(content)
                        print(f"  Updated imports in: {relative_path}")
                    else:
                        print(f"  [DRY-RUN] Would update imports in: {relative_path}")

            except Exception as e:
                print(f"  Error processing {py_file}: {e}")

        print(f"\nTotal files with import updates: {len(self.import_updates)}")

    def cleanup_obsolete(self):
        """Remove obsolete directories and files."""
        print("\n=== Cleaning Up Obsolete Files ===")

        # Remove directories
        for dir_path in OBSOLETE_DIRS:
            full_path = self.repo_root / dir_path
            if full_path.exists():
                self.log_action("DELETE_DIR", dir_path, "", "pending")
                if not self.dry_run:
                    shutil.rmtree(full_path)
                    self.log_action("DELETE_DIR", dir_path, "", "completed")

        # Remove files
        for file_path in OBSOLETE_FILES:
            full_path = self.repo_root / file_path
            if full_path.exists():
                self.log_action("DELETE_FILE", file_path, "", "pending")
                if not self.dry_run:
                    full_path.unlink()
                    self.log_action("DELETE_FILE", file_path, "", "completed")

    def generate_report(self) -> str:
        """Generate migration report."""
        report = {
            "dry_run": self.dry_run,
            "migration_actions": self.migration_log,
            "import_updates": self.import_updates,
            "summary": {
                "total_actions": len(self.migration_log),
                "files_with_import_updates": len(self.import_updates),
                "total_import_changes": sum(u["changes"] for u in self.import_updates),
            }
        }

        return json.dumps(report, indent=2)

    def execute(self):
        """Execute the full migration."""
        print(f"\n{'='*60}")
        print(f"TTA Repository Restructuring - {'DRY RUN' if self.dry_run else 'EXECUTION'}")
        print(f"{'='*60}")

        self.create_directory_structure()
        self.migrate_code()
        self.update_imports()
        self.cleanup_obsolete()

        # Save report
        report_path = self.repo_root / "migration_report.json"
        report_content = self.generate_report()

        if not self.dry_run:
            report_path.write_text(report_content)
            print(f"\n✓ Migration report saved to: {report_path}")
        else:
            print(f"\n[DRY-RUN] Would save migration report to: {report_path}")

        print(f"\n{'='*60}")
        print(f"Migration {'Preview' if self.dry_run else 'Execution'} Complete")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="TTA Repository Restructuring Tool")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    parser.add_argument("--execute", action="store_true", help="Execute the migration")
    parser.add_argument("--rollback", action="store_true", help="Rollback to pre-restructure-backup branch")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]

    if args.rollback:
        print("Rollback functionality: Use 'git checkout pre-restructure-backup' to rollback")
        return

    if args.execute:
        response = input("This will modify the repository structure. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Migration cancelled.")
            return
        dry_run = False
    else:
        dry_run = True

    restructurer = RepositoryRestructurer(repo_root, dry_run=dry_run)
    restructurer.execute()


if __name__ == "__main__":
    main()
