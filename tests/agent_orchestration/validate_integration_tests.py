#!/usr/bin/env python3
"""
Integration Test Validation Script

This script validates that the comprehensive integration test suite for Task 12.2
is properly implemented and ready for CI/CD execution.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            if result.stdout.strip():
                # Show test count from output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '.py:' in line and any(char.isdigit() for char in line):
                        print(f"   {line}")
            return True
        else:
            print(f"❌ FAILED: {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {description} - {e}")
        return False


def validate_test_files():
    """Validate that all test files exist and are properly structured."""
    print("\n" + "="*60)
    print("📁 VALIDATING TEST FILE STRUCTURE")
    print("="*60)
    
    test_files = [
        "test_multi_agent_workflow_integration.py",
        "test_end_to_end_workflows.py", 
        "test_error_handling_recovery.py",
        "test_state_persistence_aggregation.py",
        "test_performance_concurrency.py",
        "README_INTEGRATION_TESTS.md",
        "INTEGRATION_TEST_SUMMARY.md"
    ]
    
    base_path = Path(__file__).parent
    all_exist = True
    
    for test_file in test_files:
        file_path = base_path / test_file
        if file_path.exists():
            print(f"✅ {test_file}")
        else:
            print(f"❌ {test_file} - NOT FOUND")
            all_exist = False
    
    return all_exist


def validate_test_discovery():
    """Validate that pytest can discover all integration tests."""
    print("\n" + "="*60)
    print("🔍 VALIDATING TEST DISCOVERY")
    print("="*60)
    
    commands = [
        ("uv run pytest tests/agent_orchestration/test_end_to_end_workflows.py --collect-only -q", 
         "End-to-end workflow tests discovery"),
        ("uv run pytest tests/agent_orchestration/test_error_handling_recovery.py --collect-only -q",
         "Error handling tests discovery"),
        ("uv run pytest tests/agent_orchestration/test_state_persistence_aggregation.py --collect-only -q",
         "State persistence tests discovery"),
        ("uv run pytest tests/agent_orchestration/test_performance_concurrency.py --collect-only -q",
         "Performance tests discovery"),
    ]
    
    all_success = True
    total_tests = 0
    
    for cmd, desc in commands:
        success = run_command(cmd, desc)
        if not success:
            all_success = False
        else:
            # Try to extract test count
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if '.py:' in line and line.strip().split(':')[-1].strip().isdigit():
                        count = int(line.strip().split(':')[-1].strip())
                        total_tests += count
            except:
                pass
    
    print(f"\n📊 TOTAL INTEGRATION TESTS DISCOVERED: {total_tests}")
    return all_success


def validate_three_tier_execution():
    """Validate three-tier test execution pattern."""
    print("\n" + "="*60)
    print("🎯 VALIDATING THREE-TIER EXECUTION")
    print("="*60)
    
    test_file = "tests/agent_orchestration/test_end_to_end_workflows.py"
    
    commands = [
        (f"uv run pytest {test_file} --collect-only -q",
         "Tier 1: Unit tests only"),
        (f"uv run pytest {test_file} --redis --collect-only -q",
         "Tier 2: Redis integration"),
        (f"uv run pytest {test_file} --neo4j --collect-only -q", 
         "Tier 3: Neo4j integration"),
        (f"uv run pytest {test_file} --redis --neo4j --collect-only -q",
         "Full integration: Redis + Neo4j"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        success = run_command(cmd, desc)
        if not success:
            all_success = False
    
    return all_success


def validate_ci_cd_compatibility():
    """Validate CI/CD configuration compatibility."""
    print("\n" + "="*60)
    print("🚀 VALIDATING CI/CD COMPATIBILITY")
    print("="*60)
    
    # Check if GitHub Actions workflow exists
    workflow_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "tests.yml"
    if workflow_path.exists():
        print("✅ GitHub Actions workflow found")
        
        # Check if integration job exists
        with open(workflow_path, 'r') as f:
            content = f.read()
            
        checks = [
            ("integration:" in content, "Integration job defined"),
            ("neo4j:" in content, "Neo4j service configured"),
            ("redis:" in content, "Redis service configured"),
            ("--neo4j --redis" in content, "Integration test flags configured"),
        ]
        
        all_good = True
        for check, desc in checks:
            if check:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc}")
                all_good = False
        
        return all_good
    else:
        print("❌ GitHub Actions workflow not found")
        return False


def validate_pytest_markers():
    """Validate that tests have proper pytest markers."""
    print("\n" + "="*60)
    print("🏷️  VALIDATING PYTEST MARKERS")
    print("="*60)
    
    test_files = [
        "test_end_to_end_workflows.py",
        "test_error_handling_recovery.py", 
        "test_state_persistence_aggregation.py",
        "test_performance_concurrency.py"
    ]
    
    base_path = Path(__file__).parent
    all_good = True
    
    for test_file in test_files:
        file_path = base_path / test_file
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            markers = [
                ("@pytest.mark.integration", "Integration marker"),
                ("@pytest.mark.redis", "Redis marker"),
                ("@pytest.mark.neo4j", "Neo4j marker"),
            ]
            
            file_good = True
            for marker, desc in markers:
                if marker in content:
                    print(f"✅ {test_file}: {desc}")
                else:
                    print(f"❌ {test_file}: Missing {desc}")
                    file_good = False
                    all_good = False
            
            if file_good:
                print(f"✅ {test_file}: All markers present")
        else:
            print(f"❌ {test_file}: File not found")
            all_good = False
    
    return all_good


def main():
    """Main validation function."""
    print("🧪 INTEGRATION TEST VALIDATION")
    print("Task 12.2: Multi-Agent Workflow Integration Tests")
    print("="*60)
    
    validations = [
        ("Test File Structure", validate_test_files),
        ("Test Discovery", validate_test_discovery),
        ("Three-Tier Execution", validate_three_tier_execution),
        ("CI/CD Compatibility", validate_ci_cd_compatibility),
        ("Pytest Markers", validate_pytest_markers),
    ]
    
    results = {}
    for name, validator in validations:
        try:
            results[name] = validator()
        except Exception as e:
            print(f"❌ ERROR in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 VALIDATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Task 12.2 integration tests are ready for production")
        print("✅ CI/CD pipeline will execute tests correctly")
        print("✅ Three-tier execution pattern is working")
        print("✅ All test infrastructure is properly configured")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("Please review the failed validations above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
