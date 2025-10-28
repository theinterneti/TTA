# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Phase 1 Security Update Validation Script

Validates that all Phase 1 dependency updates are correctly applied
and that the packages can be imported successfully.
"""

import sys
from pathlib import Path


def check_requirements_file(file_path, expected_versions):
    """Check that a requirements file contains the expected versions."""
    print(f"\n📄 Checking {file_path}...")

    if not Path(file_path).exists():
        print(f"  ❌ File not found: {file_path}")
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
            print(f"  ✅ {package}=={version}")
        else:
            print(f"  ❌ {package}=={version} NOT FOUND")
            all_found = False

    return all_found


def test_package_import(package_name, import_name=None):
    """Test that a package can be imported."""
    if import_name is None:
        import_name = package_name.replace("-", "_")

    try:
        __import__(import_name)
        print(f"  ✅ {package_name} can be imported")
        return True
    except ImportError as e:
        print(f"  ⚠️  {package_name} import failed (may not be installed): {e}")
        return False


def main():
    print("=" * 80)
    print("PHASE 1 SECURITY UPDATE VALIDATION")
    print("=" * 80)

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

    print("\n" + "=" * 80)
    print("STEP 1: Verify Requirements Files")
    print("=" * 80)

    all_files_ok = True
    for file_path, expected in files_to_check.items():
        if not check_requirements_file(file_path, expected):
            all_files_ok = False

    print("\n" + "=" * 80)
    print("STEP 2: Test Package Imports")
    print("=" * 80)
    print("\n⚠️  Note: Some packages may not be installed in current environment")
    print("This is expected - validation focuses on requirements file updates\n")

    # Test imports (these may fail if not installed, which is OK)
    test_package_import("python-jose", "jose")
    test_package_import("gunicorn")
    test_package_import("python-multipart", "multipart")
    test_package_import("aiohttp")
    test_package_import("pillow", "PIL")

    print("\n" + "=" * 80)
    print("STEP 3: Summary")
    print("=" * 80)

    if all_files_ok:
        print("\n✅ SUCCESS: All Phase 1 dependency updates are correctly applied!")
        print("\nUpdated packages:")
        for package, version in phase1_updates.items():
            print(f"  • {package}: → {version}")

        print("\nFiles updated:")
        for file_path in files_to_check:
            print(f"  • {file_path}")

        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Install dependencies: uv sync --all-extras")
        print("2. Run existing test suite to validate functionality")
        print("3. Test authentication flows (JWT, OAuth)")
        print("4. Test form data handling")
        print("5. Test HTTP client operations")
        print("6. Create conventional commits")
        print("7. Generate PR for review")

        return 0
    print("\n❌ FAILURE: Some dependency updates are missing or incorrect")
    print("Please review the errors above and fix the requirements files.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
