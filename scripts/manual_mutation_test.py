# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Manual Mutation Testing Script for ModelSelector

This script performs manual mutation testing by:
1. Creating backup of original file
2. Applying specific mutations
3. Running tests
4. Restoring original file
5. Reporting results

Usage:
    python scripts/manual_mutation_test.py
"""

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Mutation:
    """Represents a single mutation to test."""

    name: str
    description: str
    line_number: int
    original_line: str
    mutated_line: str
    expected_result: str  # "KILLED" or "SURVIVED"


# Define mutations to test
MUTATIONS = [
    Mutation(
        name="MUT-1: Zero therapeutic safety weight",
        description="Change therapeutic safety scoring to always use weight of 0",
        line_number=219,
        original_line="                    * self.selection_criteria.therapeutic_safety_weight",
        mutated_line="                    * 0  # MUTATION: Zero out therapeutic safety weight",
        expected_result="KILLED",
    ),
    Mutation(
        name="MUT-2: Change comparison operator in ranking",
        description="Change > to >= in score comparison",
        line_number=165,
        original_line="            if score > best_score:",
        mutated_line="            if score >= best_score:  # MUTATION: Changed > to >=",
        expected_result="KILLED",
    ),
    Mutation(
        name="MUT-3: Remove performance score contribution",
        description="Set performance score contribution to 0",
        line_number=209,
        original_line="                    model.performance_score * self.selection_criteria.performance_weight",
        mutated_line="                    0  # MUTATION: Remove performance score contribution",
        expected_result="KILLED",
    ),
    Mutation(
        name="MUT-4: Change default performance score",
        description="Change default performance score from 5.0 to 10.0",
        line_number=213,
        original_line="                score += 5.0 * self.selection_criteria.performance_weight",
        mutated_line="                score += 10.0 * self.selection_criteria.performance_weight  # MUTATION: Changed default",
        expected_result="KILLED",
    ),
    Mutation(
        name="MUT-5: Remove context length check",
        description="Always return True for context length compatibility",
        line_number=275,
        original_line="        if requirements.min_context_length:",
        mutated_line="        if False:  # MUTATION: Skip context length check",
        expected_result="KILLED",
    ),
]


def run_tests() -> bool:
    """Run the test suite and return True if all tests pass."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "pytest",
            "tests/unit/model_management/services/test_model_selector_properties.py",
            "tests/unit/model_management/services/test_model_selector_concrete.py",
            "-x",
            "-q",
            "--tb=no",
            "-p",
            "no:warnings",
        ],
        check=False,
        cwd="/home/thein/recovered-tta-storytelling",
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def apply_mutation(file_path: Path, mutation: Mutation) -> bool:
    """Apply a mutation to the file. Returns True if successful."""
    try:
        with open(file_path) as f:
            lines = f.readlines()

        # Check if the line matches (accounting for line numbers being 1-indexed)
        if mutation.line_number > len(lines):
            print(f"  ❌ Line number {mutation.line_number} out of range")
            return False

        actual_line = lines[mutation.line_number - 1]
        if mutation.original_line.strip() not in actual_line:
            print(f"  ❌ Line content mismatch at line {mutation.line_number}")
            print(f"     Expected substring: {mutation.original_line.strip()}")
            print(f"     Actual line: {actual_line.strip()}")
            return False

        # Apply mutation
        lines[mutation.line_number - 1] = mutation.mutated_line + "\n"

        with open(file_path, "w") as f:
            f.writelines(lines)

        return True
    except Exception as e:
        print(f"  ❌ Error applying mutation: {e}")
        return False


def main():
    """Run manual mutation testing."""
    project_root = Path("/home/thein/recovered-tta-storytelling")
    target_file = (
        project_root / "src/components/model_management/services/model_selector.py"
    )
    backup_file = target_file.with_suffix(".py.backup")

    print("=" * 80)
    print("MANUAL MUTATION TESTING - ModelSelector")
    print("=" * 80)
    print()

    # Create backup
    print("📋 Creating backup...")
    shutil.copy2(target_file, backup_file)
    print(f"   Backup created: {backup_file}")
    print()

    # Run baseline tests
    print("🧪 Running baseline tests (no mutations)...")
    baseline_pass = run_tests()
    if not baseline_pass:
        print("   ❌ BASELINE TESTS FAILED - Cannot proceed with mutation testing")
        print("   Please fix failing tests before running mutation testing.")
        shutil.copy2(backup_file, target_file)
        backup_file.unlink()
        return
    print("   ✅ Baseline tests PASSED")
    print()

    # Test each mutation
    results = []
    for i, mutation in enumerate(MUTATIONS, 1):
        print(f"🧬 Mutation {i}/{len(MUTATIONS)}: {mutation.name}")
        print(f"   Description: {mutation.description}")
        print(f"   Line {mutation.line_number}: {mutation.original_line.strip()}")
        print(f"   Mutated to: {mutation.mutated_line.strip()}")

        # Apply mutation
        if not apply_mutation(target_file, mutation):
            results.append((mutation, "ERROR", "Failed to apply mutation"))
            shutil.copy2(backup_file, target_file)
            continue

        # Run tests
        print("   Running tests...")
        tests_pass = run_tests()

        # Determine result
        if tests_pass:
            status = "SURVIVED"
            symbol = "⚠️"
            message = "Tests still pass - mutation not detected!"
        else:
            status = "KILLED"
            symbol = "✅"
            message = "Tests failed - mutation detected!"

        print(f"   {symbol} {status}: {message}")

        # Check if result matches expectation
        if status == mutation.expected_result:
            print(f"   ✓ Result matches expectation ({mutation.expected_result})")
        else:
            print(
                f"   ⚠️  Unexpected result! Expected {mutation.expected_result}, got {status}"
            )

        results.append((mutation, status, message))

        # Restore original file
        shutil.copy2(backup_file, target_file)
        print()

    # Print summary
    print("=" * 80)
    print("MUTATION TESTING SUMMARY")
    print("=" * 80)
    print()

    killed = sum(1 for _, status, _ in results if status == "KILLED")
    survived = sum(1 for _, status, _ in results if status == "SURVIVED")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    total = len(results)

    print(f"Total Mutations: {total}")
    print(f"Killed: {killed} ({killed / total * 100:.1f}%)")
    print(f"Survived: {survived} ({survived / total * 100:.1f}%)")
    print(f"Errors: {errors}")
    print()

    if survived > 0:
        print("⚠️  SURVIVING MUTANTS (Test Gaps):")
        for mutation, status, message in results:
            if status == "SURVIVED":
                print(f"   - {mutation.name}")
                print(f"     {mutation.description}")
        print()

    mutation_score = (killed / total * 100) if total > 0 else 0
    print(f"Mutation Score: {mutation_score:.1f}%")

    if mutation_score >= 80:
        print("✅ EXCELLENT - Test suite has strong mutation coverage!")
    elif mutation_score >= 60:
        print("⚠️  GOOD - Test suite has decent coverage, but could be improved")
    else:
        print("❌ POOR - Test suite needs significant improvement")

    print()

    # Cleanup
    backup_file.unlink()
    print("🧹 Cleanup complete - original file restored")


if __name__ == "__main__":
    main()
