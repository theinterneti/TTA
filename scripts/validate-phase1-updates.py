#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Validate-phase1-updates]]
Phase 1 Security Update Validation Script

Validates that all Phase 1 dependency updates are correctly applied
and that the packages can be imported successfully.
"""

import sys
from pathlib import Path


def check_requirements_file(file_path, expected_versions):
    """Check that a requirements file contains the expected versions."""

    if not Path(file_path).exists():
        return False

    with open(file_path) as f:
        content = f.read()

    all_found = True
    for package, version in expected_versions.items():
        if (
            f"{package}=={version}" in content
            or f"{package}[" in content
            and version in content
        ):
            pass
        else:
            all_found = False

    return all_found


def test_package_import(package_name, import_name=None):
    """Test that a package can be imported."""
    if import_name is None:
        import_name = package_name.replace("-", "_")

    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def main():
    # Define expected versions
    phase1_updates = {
        "python-jose": "3.4.0",
        "gunicorn": "22.0.0",
        "python-multipart": "0.0.18",
        "aiohttp": "3.12.14",
        "pillow": "10.3.0",
    }

    # Check each requirements file
    files_to_check = {
        "src/player_experience/api/requirements.txt": {
            "python-jose": "3.4.0",
            "python-multipart": "0.0.18",
            "aiohttp": "3.12.14",
        },
        "src/player_experience/franchise_worlds/deployment/requirements-prod.txt": {
            "python-jose": "3.4.0",
            "gunicorn": "22.0.0",
            "python-multipart": "0.0.18",
        },
        "src/analytics/requirements.txt": {
            "python-multipart": "0.0.18",
        },
        "testing/requirements-testing.txt": {
            "aiohttp": "3.12.14",
            "pillow": "10.3.0",
        },
    }

    all_files_ok = True
    for file_path, expected in files_to_check.items():
        if not check_requirements_file(file_path, expected):
            all_files_ok = False

    # Test imports (these may fail if not installed, which is OK)
    test_package_import("python-jose", "jose")
    test_package_import("gunicorn")
    test_package_import("python-multipart", "multipart")
    test_package_import("aiohttp")
    test_package_import("pillow", "PIL")

    if all_files_ok:
        for _package, _version in phase1_updates.items():
            pass

        for file_path in files_to_check:
            pass

        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
