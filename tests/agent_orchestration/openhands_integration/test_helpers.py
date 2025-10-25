"""
Tests for OpenHands integration helper utilities.

Tests the convenience functions for test generation.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent_orchestration.openhands_integration.helpers import (
    generate_tests_for_file,
    generate_tests_for_package,
    validate_test_result,
)
from src.agent_orchestration.openhands_integration.test_generation_models import (
    TestValidationResult,
)


class TestGenerateTestsForFile:
    """Tests for generate_tests_for_file helper."""

    @pytest.mark.asyncio
    async def test_generate_tests_for_file_success(
        self, tmp_path, openhands_config, mock_openhands_sdk
    ):
        """Test successful test generation for single file."""
        # Create test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text("def sample_function():\n    return 42\n")

        # Mock service
        with patch(
            "src.agent_orchestration.openhands_integration.helpers.UnitTestGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            # Mock successful result
            mock_result = TestValidationResult(
                syntax_valid=True,
                conventions_followed=True,
                tests_pass=True,
                coverage_percentage=85.0,
                issues=[],
                quality_score=90.0,
                test_file_path=Path("tests/test_module.py"),
            )
            mock_service.generate_tests.return_value = mock_result

            # Execute
            result = await generate_tests_for_file(
                test_file,
                coverage_threshold=70.0,
                max_iterations=5,
                config=openhands_config,
            )

            # Verify
            assert result.syntax_valid
            assert result.tests_pass
            assert result.coverage_percentage == 85.0
            mock_service.generate_tests.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_tests_for_file_not_found(self, openhands_config):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            await generate_tests_for_file(
                "nonexistent_file.py",
                config=openhands_config,
            )

    @pytest.mark.asyncio
    async def test_generate_tests_for_file_not_python(self, tmp_path, openhands_config):
        """Test error when file is not Python."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("not python")

        with pytest.raises(ValueError, match="not a Python file"):
            await generate_tests_for_file(
                test_file,
                config=openhands_config,
            )

    @pytest.mark.asyncio
    async def test_generate_tests_for_file_is_directory(
        self, tmp_path, openhands_config
    ):
        """Test error when path is directory."""
        with pytest.raises(ValueError, match="not a file"):
            await generate_tests_for_file(
                tmp_path,
                config=openhands_config,
            )

    @pytest.mark.asyncio
    async def test_generate_tests_for_file_loads_config_from_env(
        self, tmp_path, mock_openhands_sdk
    ):
        """Test that config is loaded from environment if not provided."""
        # Create test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text("def sample_function():\n    return 42\n")

        # Mock config loading
        with patch(
            "src.agent_orchestration.openhands_integration.helpers.OpenHandsIntegrationConfig.from_env"
        ) as mock_from_env:
            mock_config = MagicMock()
            mock_config.to_client_config.return_value = MagicMock()
            mock_from_env.return_value = mock_config

            # Mock service
            with patch(
                "src.agent_orchestration.openhands_integration.helpers.UnitTestGenerationService"
            ) as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                mock_service.generate_tests.return_value = TestValidationResult(
                    syntax_valid=True,
                    conventions_followed=True,
                    tests_pass=True,
                    coverage_percentage=85.0,
                    issues=[],
                    quality_score=90.0,
                    test_file_path=Path("tests/test_module.py"),
                )

                # Execute without config
                await generate_tests_for_file(test_file)

                # Verify config was loaded from env
                mock_from_env.assert_called_once()


class TestGenerateTestsForPackage:
    """Tests for generate_tests_for_package helper."""

    @pytest.mark.asyncio
    async def test_generate_tests_for_package_success(
        self, tmp_path, openhands_config, mock_openhands_sdk
    ):
        """Test successful test generation for package."""
        # Create package with multiple files
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("")
        (package_dir / "module1.py").write_text("def func1():\n    return 1\n")
        (package_dir / "module2.py").write_text("def func2():\n    return 2\n")

        # Mock service
        with patch(
            "src.agent_orchestration.openhands_integration.helpers.UnitTestGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            # Mock successful results
            mock_result = TestValidationResult(
                syntax_valid=True,
                conventions_followed=True,
                tests_pass=True,
                coverage_percentage=85.0,
                issues=[],
                quality_score=90.0,
                test_file_path=Path("tests/test_module.py"),
            )
            mock_service.generate_tests.return_value = mock_result

            # Execute
            results = await generate_tests_for_package(
                package_dir,
                coverage_threshold=70.0,
                config=openhands_config,
            )

            # Verify
            assert len(results) == 2  # module1.py and module2.py (__init__.py excluded)
            assert all(r.syntax_valid for r in results.values())
            assert all(r.tests_pass for r in results.values())

    @pytest.mark.asyncio
    async def test_generate_tests_for_package_not_found(self, openhands_config):
        """Test error when package doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Package not found"):
            await generate_tests_for_package(
                "nonexistent_package",
                config=openhands_config,
            )

    @pytest.mark.asyncio
    async def test_generate_tests_for_package_not_directory(
        self, tmp_path, openhands_config
    ):
        """Test error when path is not directory."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def func():\n    pass\n")

        with pytest.raises(ValueError, match="not a directory"):
            await generate_tests_for_package(
                test_file,
                config=openhands_config,
            )

    @pytest.mark.asyncio
    async def test_generate_tests_for_package_empty(self, tmp_path, openhands_config):
        """Test handling of empty package."""
        package_dir = tmp_path / "empty_package"
        package_dir.mkdir()

        results = await generate_tests_for_package(
            package_dir,
            config=openhands_config,
        )

        assert results == {}

    @pytest.mark.asyncio
    async def test_generate_tests_for_package_partial_failure(
        self, tmp_path, openhands_config, mock_openhands_sdk
    ):
        """Test that package generation continues even if one file fails."""
        # Create package with multiple files
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "module1.py").write_text("def func1():\n    return 1\n")
        (package_dir / "module2.py").write_text("def func2():\n    return 2\n")

        # Mock service to fail on first file, succeed on second
        with patch(
            "src.agent_orchestration.openhands_integration.helpers.UnitTestGenerationService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            # First call fails, second succeeds
            mock_service.generate_tests.side_effect = [
                Exception("Test generation failed"),
                TestValidationResult(
                    syntax_valid=True,
                    conventions_followed=True,
                    tests_pass=True,
                    coverage_percentage=85.0,
                    issues=[],
                    quality_score=90.0,
                    test_file_path=Path("tests/test_module2.py"),
                ),
            ]

            # Execute
            results = await generate_tests_for_package(
                package_dir,
                config=openhands_config,
            )

            # Verify - should have result for second file only
            assert len(results) == 1


class TestValidateTestResult:
    """Tests for validate_test_result helper."""

    def test_validate_test_result_success(self):
        """Test validation of successful result."""
        result = TestValidationResult(
            syntax_valid=True,
            conventions_followed=True,
            tests_pass=True,
            coverage_percentage=85.0,
            issues=[],
            quality_score=90.0,
            test_file_path=Path("tests/test_module.py"),
        )

        success, issues = validate_test_result(result, coverage_threshold=70.0)

        assert success
        assert issues == []

    def test_validate_test_result_syntax_invalid(self):
        """Test validation with syntax errors."""
        result = TestValidationResult(
            syntax_valid=False,
            conventions_followed=True,
            tests_pass=True,
            coverage_percentage=85.0,
            issues=[],
            quality_score=90.0,
            test_file_path=Path("tests/test_module.py"),
        )

        success, issues = validate_test_result(result)

        assert not success
        assert "Syntax errors" in issues[0]

    def test_validate_test_result_conventions_not_followed(self):
        """Test validation with convention violations."""
        result = TestValidationResult(
            syntax_valid=True,
            conventions_followed=False,
            tests_pass=True,
            coverage_percentage=85.0,
            issues=[],
            quality_score=90.0,
            test_file_path=Path("tests/test_module.py"),
        )

        success, issues = validate_test_result(result)

        assert not success
        assert "conventions" in issues[0].lower()

    def test_validate_test_result_tests_dont_pass(self):
        """Test validation with failing tests."""
        result = TestValidationResult(
            syntax_valid=True,
            conventions_followed=True,
            tests_pass=False,
            coverage_percentage=85.0,
            issues=[],
            quality_score=90.0,
            test_file_path=Path("tests/test_module.py"),
        )

        success, issues = validate_test_result(result)

        assert not success
        assert "don't pass" in issues[0]

    def test_validate_test_result_low_coverage(self):
        """Test validation with coverage below threshold."""
        result = TestValidationResult(
            syntax_valid=True,
            conventions_followed=True,
            tests_pass=True,
            coverage_percentage=65.0,
            issues=[],
            quality_score=90.0,
            test_file_path=Path("tests/test_module.py"),
        )

        success, issues = validate_test_result(result, coverage_threshold=70.0)

        assert not success
        assert "Coverage 65.0% below threshold 70.0%" in issues[0]

    def test_validate_test_result_with_result_issues(self):
        """Test validation includes issues from result."""
        result = TestValidationResult(
            syntax_valid=True,
            conventions_followed=True,
            tests_pass=True,
            coverage_percentage=85.0,
            issues=["Missing edge case tests", "Incomplete error handling"],
            quality_score=90.0,
            test_file_path=Path("tests/test_module.py"),
        )

        success, issues = validate_test_result(result)

        assert not success
        assert "Missing edge case tests" in issues
        assert "Incomplete error handling" in issues
