# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Comprehensive test suite for OpenHands integration with real OpenRouter API credentials.

Tests:
1. Configuration loading from environment
2. Docker client initialization
3. Real task execution via Docker
4. File creation in workspace
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "src")


def test_env_file():
    """Test 1: Verify .env file exists and contains API key."""
    print("\n" + "=" * 70)
    print("TEST 1: Environment File Verification")
    print("=" * 70)

    env_file = Path(".env")
    if not env_file.exists():
        print("❌ FAIL: .env file not found")
        return False

    content = env_file.read_text()
    if "OPENROUTER_API_KEY" not in content:
        print("❌ FAIL: OPENROUTER_API_KEY not found in .env")
        return False

    print("✅ PASS: .env file exists with OPENROUTER_API_KEY")
    return True


def test_config_loading():
    """Test 2: Verify configuration loads from environment."""
    print("\n" + "=" * 70)
    print("TEST 2: Configuration Loading")
    print("=" * 70)

    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )

        config = OpenHandsIntegrationConfig.from_env()
        api_key = config.api_key.get_secret_value()

        if not api_key.startswith("sk-or-v1-"):
            print(f"❌ FAIL: Invalid API key format: {api_key[:20]}...")
            return False

        print("✅ PASS: Config loaded successfully")
        print(f"   - Model preset: {config.model_preset}")
        print(f"   - Workspace: {config.workspace_root}")
        print(f"   - API key: {api_key[:30]}...")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_docker_client_init():
    """Test 3: Verify Docker client initializes."""
    print("\n" + "=" * 70)
    print("TEST 3: Docker Client Initialization")
    print("=" * 70)

    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )
        from agent_orchestration.openhands_integration.docker_client import (
            DockerOpenHandsClient,
        )

        config = OpenHandsIntegrationConfig.from_env()
        client_config = config.to_client_config()
        client = DockerOpenHandsClient(client_config)

        print("✅ PASS: Docker client initialized")
        print(f"   - OpenHands image: {client.openhands_image}")
        print(f"   - Runtime image: {client.runtime_image}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


async def test_real_task_execution():
    """Test 4: Execute real task via Docker with OpenRouter API."""
    print("\n" + "=" * 70)
    print("TEST 4: Real Task Execution (Docker + OpenRouter API)")
    print("=" * 70)

    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )
        from agent_orchestration.openhands_integration.docker_client import (
            DockerOpenHandsClient,
        )

        config = OpenHandsIntegrationConfig.from_env()
        client_config = config.to_client_config()
        client = DockerOpenHandsClient(client_config)

        workspace = config.workspace_root
        workspace.mkdir(parents=True, exist_ok=True)

        task_description = "Create a file named 'openhands_test.txt' in the workspace with content 'Hello from OpenHands'"

        print(f"Executing task: {task_description}")
        print(f"Workspace: {workspace}")

        result = await client.execute_task(
            task_description=task_description,
            workspace_path=workspace,
            timeout=config.default_timeout_seconds,
        )

        if not result.success:
            print(
                f"❌ FAIL: Task failed with exit code {result.metadata.get('exit_code')}"
            )
            print(f"Error: {result.error}")
            return False

        # Check if file was created
        test_file = workspace / "openhands_test.txt"
        if not test_file.exists():
            print("❌ FAIL: File not created in workspace")
            return False

        content = test_file.read_text()
        if content != "Hello from OpenHands":
            print(f"❌ FAIL: File content incorrect: {content}")
            return False

        print("✅ PASS: Task executed successfully")
        print(f"   - Execution time: {result.execution_time:.2f}s")
        print(f"   - File created: {test_file}")
        print(f"   - File content: {content}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("OPENHANDS INTEGRATION TEST SUITE")
    print("=" * 70)

    results = []

    # Run synchronous tests
    results.append(("Environment File", test_env_file()))
    results.append(("Config Loading", test_config_loading()))
    results.append(("Docker Client Init", test_docker_client_init()))

    # Run async test
    results.append(("Real Task Execution", await test_real_task_execution()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! OpenHands integration is ready for production.")
        return 0
    print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
