#!/usr/bin/env python3
"""
TTA System Cleanup Script

This script removes obsolete demo, test, and debug files that are no longer needed
for the integrated TTA system. It creates a backup list before deletion.

Usage:
    python cleanup_obsolete_files.py [--dry-run] [--backup]
"""

import argparse
import os
import shutil
from datetime import datetime


def get_obsolete_files() -> list[str]:
    """Get list of obsolete files to be removed."""
    obsolete_files = [
        # Root level demo and test files
        "./test-ai-narrative-generation.py",
        "./demo_authentication_fix.py",
        "./demo-preference-integration.py",
        "./test_narrative_scale_management.py",
        "./test-comprehensive-preference-system.py",
        "./test_websocket_simple.py",
        "./test_tta_data_flow_verification.py",
        "./demo-complete-preference-system.py",
        "./test_conflict_resolution_mechanisms.py",
        "./test-websocket-ai-integration.py",
        "./test-openrouter-model-performance.py",
        "./test_dependencies.py",
        "./demo_docker_integration.py",
        "./test_engine_simple.py",
        "./test_server.py",
        "./demo_comprehensive_test_integration.py",
        "./test-player-preference-ai-pipeline.py",
        # JavaScript test and debug files
        "./debug-frontend.js",
        "./test-all-browsers.js",
        "./test-modal-debug-console.js",
        "./test-dev-server-character-creation.js",
        "./test-character-creation-complete.js",
        "./test-character-creation-final.js",
        "./test-browser-fix.js",
        "./test-tta-chat-focused.js",
        "./test-modal-form-submission.js",
        "./debug-react-error.js",
        "./test-character-creation-modal-debug.js",
        "./test-auth-simple.js",
        "./test-character-simple-complete.js",
        "./test-modal-dom-debug.js",
        "./test_model_management_components.js",
        "./test-create-character-button.js",
        "./test-character-api-direct.js",
        "./test-tta-chat-conversation-e2e.js",
        "./test-character-loading-debug.js",
        "./test-all-character-buttons.js",
        # Log and output files
        "./.augment_full_test_output.txt",
        "./.pytest-firstfail.txt",
        "./.pytest-full.txt",
        "./.pytest-junit.xml",
        "./.pytest-last.txt",
        "./.pytest-quiet.txt",
        "./api-test-final.png",
        # Temporary image files
        "./screenshot-*.png",
        "./test-*.png",
        "./debug-*.png",
    ]

    return obsolete_files


def get_obsolete_directories() -> list[str]:
    """Get list of obsolete directories to be removed."""
    obsolete_dirs = [
        "./testing-env",
        "./tta-env",
        "./venv",  # Duplicate venv directory
        "./.pytest_cache",
    ]

    return obsolete_dirs


def create_backup_list(
    files: list[str], directories: list[str], backup_file: str
) -> None:
    """Create a backup list of files being removed."""
    with open(backup_file, "w") as f:
        f.write(f"# TTA Cleanup Backup List - {datetime.now().isoformat()}\n")
        f.write("# Files and directories removed during system cleanup\n\n")

        f.write("## Files:\n")
        for file_path in files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                f.write(
                    f"{file_path} (size: {stat.st_size} bytes, modified: {datetime.fromtimestamp(stat.st_mtime)})\n"
                )

        f.write("\n## Directories:\n")
        for dir_path in directories:
            if os.path.exists(dir_path):
                f.write(f"{dir_path}/\n")


def remove_files(files: list[str], dry_run: bool = False) -> int:
    """Remove obsolete files."""
    removed_count = 0

    for file_path in files:
        if os.path.exists(file_path):
            if dry_run:
                print(f"[DRY RUN] Would remove file: {file_path}")
            else:
                try:
                    os.remove(file_path)
                    print(f"✅ Removed file: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")

    return removed_count


def remove_directories(directories: list[str], dry_run: bool = False) -> int:
    """Remove obsolete directories."""
    removed_count = 0

    for dir_path in directories:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            if dry_run:
                print(f"[DRY RUN] Would remove directory: {dir_path}")
            else:
                try:
                    shutil.rmtree(dir_path)
                    print(f"✅ Removed directory: {dir_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {dir_path}: {e}")
        else:
            print(f"⚠️  Directory not found: {dir_path}")

    return removed_count


def main():
    parser = argparse.ArgumentParser(description="Clean up obsolete TTA files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup list of removed files"
    )

    args = parser.parse_args()

    print("🧹 TTA System Cleanup")
    print("=" * 50)

    obsolete_files = get_obsolete_files()
    obsolete_dirs = get_obsolete_directories()

    # Expand glob patterns
    expanded_files = []
    for pattern in obsolete_files:
        if "*" in pattern:
            import glob

            matches = glob.glob(pattern)
            expanded_files.extend(matches)
        else:
            expanded_files.append(pattern)

    print(
        f"Found {len(expanded_files)} files and {len(obsolete_dirs)} directories to clean up"
    )

    if args.backup and not args.dry_run:
        backup_file = f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        create_backup_list(expanded_files, obsolete_dirs, backup_file)
        print(f"📝 Created backup list: {backup_file}")

    # Remove files
    print("\n🗂️  Cleaning up files...")
    files_removed = remove_files(expanded_files, args.dry_run)

    # Remove directories
    print("\n📁 Cleaning up directories...")
    dirs_removed = remove_directories(obsolete_dirs, args.dry_run)

    print("\n" + "=" * 50)
    if args.dry_run:
        print(
            f"[DRY RUN] Would remove {files_removed} files and {dirs_removed} directories"
        )
    else:
        print(
            f"✅ Cleanup complete! Removed {files_removed} files and {dirs_removed} directories"
        )
        print("🎯 System is now optimized for integration testing")


if __name__ == "__main__":
    main()
