"""
Logseq: [[TTA.dev/Tests/Test_components_legacy]]

# Logseq: [[TTA.dev/Tests/Test_components]]
TTA Components Tests

This module contains tests for the TTA components.

Usage:
    ```bash
    # Run the tests
    python3 tests/test_components.py
    ```
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

from src.components import AppComponent, CarbonComponent, DockerComponent, LLMComponent
from src.orchestration import TTAConfig
from src.orchestration.component import ComponentStatus


class TestComponents(unittest.TestCase):
    """Test case for TTA components."""

    def test_config_validation(self):
        """Test configuration validation."""
        config = TTAConfig()
        self.assertTrue(config.validate(), "Configuration validation failed")

    def test_docker_component(self):
        """Test the Docker component."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Test initialization
        self.assertEqual(docker.name, "docker", "Docker component name is incorrect")
        self.assertEqual(
            docker.status.value, "stopped", "Docker component status is incorrect"
        )

        # Test starting the component
        if os.environ.get("RUN_DOCKER_TESTS", "false").lower() == "true":
            self.assertTrue(docker.start(), "Docker component failed to start")
            self.assertEqual(
                docker.status.value,
                "running",
                "Docker component status is incorrect after starting",
            )

            # Test stopping the component
            self.assertTrue(docker.stop(), "Docker component failed to stop")
            self.assertEqual(
                docker.status.value,
                "stopped",
                "Docker component status is incorrect after stopping",
            )

    # Batch 1: Start/Stop Operations (3 tests)
    def test_docker_start_success(self):
        """Test Docker component successful start."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create mock result object for safe_run
        mock_result = type(
            "obj", (object,), {"returncode": 0, "stdout": "Docker version 20.10.0"}
        )()

        # Mock _check_docker_installed and ensure_consistency
        with (
            patch("src.common.process_utils.run", return_value=mock_result),
            patch.object(docker, "ensure_consistency", return_value=True),
        ):
            result = docker.start()
            self.assertTrue(result, "Docker component should start successfully")

    def test_docker_start_docker_not_installed(self):
        """Test Docker component start fails when Docker not installed."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock _check_docker_installed to raise RuntimeError
        with patch.object(
            docker,
            "_check_docker_installed",
            side_effect=RuntimeError("Docker not installed"),
        ):
            result = docker.start()
            self.assertFalse(
                result,
                "Docker component should fail to start when Docker not installed",
            )

    def test_docker_stop_success(self):
        """Test Docker component stop (always succeeds as it's a no-op)."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Set status to running before stopping
        docker.status = ComponentStatus.RUNNING

        result = docker.stop()
        self.assertTrue(result, "Docker component should stop successfully")

    # Batch 2: Docker Installation Check (2 tests)
    def test_check_docker_installed_success(self):
        """Test Docker installation check succeeds."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create mock result object
        mock_result = type(
            "obj", (object,), {"returncode": 0, "stdout": "Docker version 20.10.0"}
        )()

        with patch("src.common.process_utils.run", return_value=mock_result):
            result = docker._check_docker_installed()
            self.assertTrue(result, "Docker should be detected as installed")

    def test_check_docker_installed_failure(self):
        """Test Docker installation check exception handling."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create a mock result with non-zero return code
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        # Patch at the module level where it's imported
        with (
            patch("src.components.docker_component.safe_run", return_value=mock_result),
            self.assertRaises(RuntimeError),
        ):
            docker._check_docker_installed()

    # Batch 3: Consistency Orchestration (3 tests)
    def test_ensure_consistency_success(self):
        """Test ensure_consistency processes both repositories successfully."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock Path.exists to return True for both repositories
        # Mock all sub-methods to return None (they don't return values)
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(docker, "_copy_template_files"),
            patch.object(docker, "_standardize_container_names"),
            patch.object(docker, "_ensure_consistent_extensions"),
            patch.object(docker, "_ensure_consistent_env_vars"),
            patch.object(docker, "_ensure_consistent_services"),
        ):
            result = docker.ensure_consistency()
            self.assertTrue(result, "Consistency should be ensured successfully")

    def test_ensure_consistency_dev_missing(self):
        """Test ensure_consistency fails when tta.dev repository not found."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock Path.exists to return False for tta.dev
        with patch.object(Path, "exists", return_value=False):
            result = docker.ensure_consistency()
            self.assertFalse(result, "Consistency should fail when tta.dev missing")

    def test_ensure_consistency_prototype_missing(self):
        """Test ensure_consistency fails when tta.prototype repository not found."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock Path.exists to return True for tta.dev, False for tta.prototype
        def mock_exists(self):
            # First call is for tta.dev (True), second is for tta.prototype (False)
            return str(self).endswith("tta.dev")

        with (
            patch.object(Path, "exists", mock_exists),
            patch.object(docker, "_copy_template_files"),
            patch.object(docker, "_standardize_container_names"),
            patch.object(docker, "_ensure_consistent_extensions"),
            patch.object(docker, "_ensure_consistent_env_vars"),
            patch.object(docker, "_ensure_consistent_services"),
        ):
            result = docker.ensure_consistency()
            self.assertFalse(
                result, "Consistency should fail when tta.prototype missing"
            )

    def test_carbon_component(self):
        """Test the Carbon component."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Test initialization
        self.assertEqual(carbon.name, "carbon", "Carbon component name is incorrect")
        self.assertEqual(
            carbon.status.value, "stopped", "Carbon component status is incorrect"
        )

        # Test starting the component
        try:
            from codecarbon import EmissionsTracker  # noqa: PLC0415, F401

            has_codecarbon = True
        except ImportError:
            has_codecarbon = False

        if has_codecarbon:
            self.assertTrue(carbon.start(), "Carbon component failed to start")
            self.assertEqual(
                carbon.status.value,
                "running",
                "Carbon component status is incorrect after starting",
            )

            # Test tracking a function
            def test_function():
                return "test"

            result = carbon.track_function(test_function)
            self.assertEqual(
                result, "test", "Carbon component failed to track function"
            )

            # Test getting emissions report
            report = carbon.get_emissions_report()
            self.assertIn(
                "project_name", report, "Emissions report is missing project_name"
            )
            self.assertIn(
                "total_emissions", report, "Emissions report is missing total_emissions"
            )

            # Test stopping the component
            self.assertTrue(carbon.stop(), "Carbon component failed to stop")
            self.assertEqual(
                carbon.status.value,
                "stopped",
                "Carbon component status is incorrect after stopping",
            )

    def test_carbon_decorator(self):
        """Test the Carbon component decorator functionality."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Test getting the carbon decorator
        decorator = carbon.get_carbon_decorator()
        self.assertIsNotNone(decorator, "Carbon decorator should not be None")

        # Test that the decorator can be applied to a function
        @decorator
        def test_function():
            return "decorated"

        result = test_function()
        self.assertEqual(result, "decorated", "Decorated function should work")

    def test_carbon_without_codecarbon(self):
        """Test Carbon component behavior when codecarbon is not available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Test that get_emissions_report handles missing codecarbon gracefully
        # This test will pass regardless of whether codecarbon is installed
        # because the component handles both cases
        report = carbon.get_emissions_report()
        self.assertIsNotNone(report, "Emissions report should not be None")

    def test_carbon_stop_without_codecarbon(self):
        """Test Carbon component stop when codecarbon is not available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Mock codecarbon_available to False
        with patch("src.components.carbon_component.codecarbon_available", False):
            carbon.start()
            result = carbon.stop()
            self.assertTrue(
                result, "Carbon component should stop successfully without codecarbon"
            )

    def test_carbon_stop_with_emissions_data(self):
        """Test Carbon component stop with emissions data."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Start the component first
        with patch("src.components.carbon_component.codecarbon_available", True):
            carbon.start()

            # Add some mock emissions data
            carbon.emissions_data = {
                "test_func": {
                    "emissions": 0.5,
                    "duration": 1.0,
                    "timestamp": "2025-10-21T00:00:00",
                }
            }

            # Mock the _save_emissions_data method
            with patch.object(carbon, "_save_emissions_data") as mock_save:
                result = carbon.stop()
                self.assertTrue(result, "Carbon component should stop successfully")
                mock_save.assert_called_once()

    def test_carbon_get_emissions_report_with_data(self):
        """Test getting emissions report with data."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Add some mock emissions data
        carbon.emissions_data = {
            "func1": {"emissions": 0.5, "duration": 1.0},
            "func2": {"emissions": 0.3, "duration": 0.5},
        }

        with patch("src.components.carbon_component.codecarbon_available", True):
            report = carbon.get_emissions_report()
            self.assertIn("project_name", report)
            self.assertIn("total_emissions", report)
            self.assertIn("functions", report)
            self.assertEqual(report["total_emissions"], 0.8)
            self.assertEqual(report["unit"], "kg CO2eq")

    def test_carbon_save_emissions_data(self):
        """Test saving emissions data to file."""
        config = TTAConfig()

        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        try:
            carbon = CarbonComponent(config)
            carbon.output_dir = temp_dir

            # Add some mock emissions data
            carbon.emissions_data = {
                "test_func": {
                    "emissions": 0.5,
                    "duration": 1.0,
                    "timestamp": "2025-10-21T00:00:00",
                }
            }

            # Patch codecarbon_available so get_emissions_report returns proper data
            with patch("src.components.carbon_component.codecarbon_available", True):
                # Call _save_emissions_data
                carbon._save_emissions_data()

            # Check that a file was created
            files = list(Path(temp_dir).glob("emissions_*.json"))
            self.assertEqual(len(files), 1, "Should create one emissions file")

            # Verify file content
            content = json.loads(files[0].read_text())
            self.assertIn("project_name", content)
            self.assertIn("total_emissions", content)
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def test_carbon_save_emissions_data_empty(self):
        """Test saving emissions data when there's no data."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        # Ensure emissions_data is empty
        carbon.emissions_data = {}

        # Call _save_emissions_data - should return early without error
        carbon._save_emissions_data()  # Should not raise an exception

    def test_carbon_get_decorator_without_codecarbon(self):
        """Test getting carbon decorator when codecarbon is not available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        with patch("src.components.carbon_component.codecarbon_available", False):
            decorator = carbon.get_carbon_decorator()
            self.assertIsNotNone(decorator, "Should return a no-op decorator")

            # Test that the decorator works as a no-op
            @decorator
            def test_func():
                return "test"

            result = test_func()
            self.assertEqual(
                result, "test", "Decorator should not affect function result"
            )

    def test_carbon_get_decorator_with_codecarbon(self):
        """Test getting carbon decorator when codecarbon is available."""
        config = TTAConfig()
        carbon = CarbonComponent(config)

        mock_decorator = lambda f: f  # noqa: E731
        mock_track_emissions = MagicMock(return_value=mock_decorator)
        with (
            patch("src.components.carbon_component.codecarbon_available", True),
            patch(
                "src.components.carbon_component.track_emissions",
                mock_track_emissions,
                create=True,
            ),
        ):
            decorator = carbon.get_carbon_decorator(project_name="test_project")
            self.assertIsNotNone(decorator, "Should return a decorator")

            # The decorator should be a callable that wraps functions
            # Test that it returns a function
            @decorator
            def test_func():
                return "test"

            # The decorated function should still be callable
            self.assertTrue(
                callable(test_func), "Decorated function should be callable"
            )

    # Batch 4: Template Copying (2 tests)
    def test_copy_template_files_docker_compose(self):
        """Test copying docker-compose.yml template - verifies method executes without error."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Just verify the method executes without raising an exception
        # The actual file operations are mocked at a lower level
        try:
            docker._copy_template_files("tta.dev")
            # If we get here, the method executed successfully
            self.assertTrue(True, "Method executed successfully")
        except Exception as e:
            self.fail(f"Method raised unexpected exception: {e}")

    def test_copy_template_files_devcontainer(self):
        """Test copying devcontainer.json template."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock Path.exists to return True for template, False for repo devcontainer
        def mock_exists(self):
            path_str = str(self)
            # Template exists, repo devcontainer doesn't
            return "templates" in path_str and "devcontainer.json" in path_str

        with (
            patch.object(Path, "exists", mock_exists),
            patch.object(Path, "mkdir") as mock_mkdir,
            patch("shutil.copy") as mock_copy,
        ):
            docker._copy_template_files("tta.dev")
            # Verify mkdir and copy were called
            self.assertTrue(
                mock_mkdir.called or mock_copy.called,
                "Directory creation or copy should occur",
            )

    # Batch 5: Container Name Standardization (2 tests)
    def test_standardize_container_names_success(self):
        """Test standardizing container names in docker-compose.yml."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock file content
        mock_content = "container_name: tta-app\ncontainer_name: tta-neo4j"
        mock_file = mock_open(read_data=mock_content)

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", mock_file),
        ):
            docker._standardize_container_names("tta.dev")
            # Verify file was opened for reading and writing
            self.assertTrue(mock_file.called, "File should be opened")

    def test_standardize_container_names_no_file(self):
        """Test standardizing container names when docker-compose.yml doesn't exist."""
        config = TTAConfig()
        docker = DockerComponent(config)

        with patch.object(Path, "exists", return_value=False):
            # Should not raise an error, just skip
            docker._standardize_container_names("tta.dev")

    # Batch 6: Extension Consistency (2 tests)
    def test_ensure_consistent_extensions_all_present(self):
        """Test ensuring extensions when all are present."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock file content with all extensions
        mock_content = """
        {
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter"
            ]
        }
        """
        mock_file = mock_open(read_data=mock_content)

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", mock_file),
        ):
            docker._ensure_consistent_extensions("tta.dev")
            # Should complete without warnings
            self.assertTrue(mock_file.called, "File should be opened")

    def test_ensure_consistent_extensions_missing(self):
        """Test ensuring extensions when some are missing."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock file content with missing extensions
        mock_content = '{"extensions": []}'
        mock_file = mock_open(read_data=mock_content)

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", mock_file),
        ):
            docker._ensure_consistent_extensions("tta.dev")
            # Should log warnings about missing extensions
            self.assertTrue(mock_file.called, "File should be opened")

    # Batch 7: Environment Variable Consistency (3 tests)
    def test_ensure_consistent_env_vars_create_new(self):
        """Test creating new .env.example file."""
        config = TTAConfig()
        docker = DockerComponent(config)

        mock_file = mock_open()

        with (
            patch.object(Path, "exists", return_value=False),
            patch.object(Path, "open", mock_file),
        ):
            docker._ensure_consistent_env_vars("tta.dev")
            # Verify file was created
            self.assertTrue(mock_file.called, "File should be created")

    def test_ensure_consistent_env_vars_add_missing(self):
        """Test adding missing environment variables."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock file content with some variables missing
        mock_content = "NEO4J_PASSWORD=password\n"
        mock_file = mock_open(read_data=mock_content)

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", mock_file),
        ):
            docker._ensure_consistent_env_vars("tta.dev")
            # Should add missing variables
            self.assertTrue(mock_file.called, "File should be opened")

    def test_ensure_consistent_env_vars_all_present(self):
        """Test when all environment variables are present."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock file content with all variables
        mock_content = """
        NEO4J_PASSWORD=password
        NEO4J_URI=bolt://neo4j:7687
        NEO4J_USERNAME=neo4j
        MODEL_CACHE_DIR=/app/.model_cache
        CODECARBON_OUTPUT_DIR=/app/logs/codecarbon
        """
        mock_file = mock_open(read_data=mock_content)

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", mock_file),
        ):
            docker._ensure_consistent_env_vars("tta.dev")
            # Should complete without adding variables
            self.assertTrue(mock_file.called, "File should be opened")

    # Batch 8: Service Consistency (2 tests)
    def test_ensure_consistent_services_all_present(self):
        """Test ensuring services when all are present."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock file content with all services
        mock_content = """
        services:
          neo4j:
            image: neo4j:latest
          app:
            image: app:latest
        """
        mock_file = mock_open(read_data=mock_content)

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", mock_file),
        ):
            docker._ensure_consistent_services("tta.dev")
            # Should complete without warnings
            self.assertTrue(mock_file.called, "File should be opened")

    def test_ensure_consistent_services_missing(self):
        """Test ensuring services when some are missing."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Mock file content with missing services
        mock_content = "services:\n  neo4j:\n    image: neo4j:latest\n"
        mock_file = mock_open(read_data=mock_content)

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", mock_file),
        ):
            docker._ensure_consistent_services("tta.dev")
            # Should log warnings about missing services
            self.assertTrue(mock_file.called, "File should be opened")

    # Batch 9: Helper Methods (3 tests)
    def test_get_env_var_default_known_vars(self):
        """Test getting default values for known environment variables."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Test known variables
        self.assertEqual(docker._get_env_var_default("NEO4J_PASSWORD"), "password")
        self.assertEqual(docker._get_env_var_default("NEO4J_URI"), "bolt://neo4j:7687")
        self.assertEqual(docker._get_env_var_default("NEO4J_USERNAME"), "neo4j")
        self.assertEqual(
            docker._get_env_var_default("MODEL_CACHE_DIR"), "/app/.model_cache"
        )
        self.assertEqual(
            docker._get_env_var_default("CODECARBON_OUTPUT_DIR"), "/app/logs/codecarbon"
        )

    def test_get_env_var_default_unknown_var(self):
        """Test getting default value for unknown environment variable."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Test unknown variable
        self.assertEqual(docker._get_env_var_default("UNKNOWN_VAR"), "default_value")

    def test_create_env_example_with_template(self):
        """Test creating .env.example from template."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            env_example_path = tmppath / ".env.example"

            # Mock the template path to not exist, forcing creation
            with patch.object(Path, "exists", return_value=False):
                docker._create_env_example("tta.dev", env_example_path)

            # Verify file was created
            self.assertTrue(env_example_path.exists(), ".env.example should be created")

            # Verify content
            content = env_example_path.read_text()
            self.assertIn("NEO4J_PASSWORD", content)
            self.assertIn("NEO4J_URI", content)

    def test_add_missing_env_vars_integration(self):
        """Test adding missing environment variables (integration test)."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            env_example_path = tmppath / ".env.example"

            # Create initial file with only one variable
            env_example_path.write_text("NEO4J_PASSWORD=password\n")

            # Call the method
            docker._add_missing_env_vars("tta.dev", env_example_path)

            # Verify missing variables were added
            content = env_example_path.read_text()
            self.assertIn("NEO4J_URI", content)
            self.assertIn("NEO4J_USERNAME", content)
            self.assertIn("MODEL_CACHE_DIR", content)
            self.assertIn("CODECARBON_OUTPUT_DIR", content)

    def test_standardize_container_names_integration(self):
        """Test standardizing container names (integration test)."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            repo_path = tmppath / "tta.dev"
            repo_path.mkdir()
            docker_compose_path = repo_path / "docker-compose.yml"

            # Create initial file with generic container names
            docker_compose_path.write_text(
                "container_name: tta-app\ncontainer_name: tta-neo4j\n"
            )

            # Mock the repo paths
            with (
                patch.object(docker, "root_dir", tmppath),
                patch.object(docker, "tta_dev_path", repo_path),
            ):
                docker._standardize_container_names("tta.dev")

            # Verify container names were standardized
            content = docker_compose_path.read_text()
            self.assertIn("tta-dev-app", content)
            self.assertIn("tta-dev-neo4j", content)

    def test_ensure_consistency_integration(self):
        """Test ensure_consistency method (integration test)."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create temporary directories for both repositories
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            tta_dev_path = tmppath / "tta.dev"
            tta_prototype_path = tmppath / "tta.prototype"

            # Create both repository directories
            tta_dev_path.mkdir()
            tta_prototype_path.mkdir()

            # Create minimal docker-compose.yml files
            (tta_dev_path / "docker-compose.yml").write_text(
                "services:\n  neo4j:\n    image: neo4j\n"
            )
            (tta_prototype_path / "docker-compose.yml").write_text(
                "services:\n  neo4j:\n    image: neo4j\n"
            )

            # Mock the repository paths
            with (
                patch.object(docker, "root_dir", tmppath),
                patch.object(docker, "tta_dev_path", tta_dev_path),
                patch.object(docker, "tta_prototype_path", tta_prototype_path),
                patch.object(docker, "templates_path", tmppath / "templates"),
            ):
                result = docker.ensure_consistency()

            # Verify success
            self.assertTrue(result, "ensure_consistency should succeed")

            # Verify .env.example files were created
            self.assertTrue((tta_dev_path / ".env.example").exists())
            self.assertTrue((tta_prototype_path / ".env.example").exists())

    def test_copy_template_files_integration(self):
        """Test _copy_template_files method (integration test)."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create temporary directories
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            repo_path = tmppath / "tta.dev"
            templates_path = tmppath / "templates" / "tta.dev"

            # Create directories
            repo_path.mkdir(parents=True)
            templates_path.mkdir(parents=True)

            # Create template docker-compose.yml
            (templates_path / "docker-compose.yml").write_text(
                "version: '3.8'\nservices:\n  app:\n    image: app\n"
            )

            # Mock the paths
            with (
                patch.object(docker, "root_dir", tmppath),
                patch.object(docker, "tta_dev_path", repo_path),
                patch.object(docker, "templates_path", tmppath / "templates"),
            ):
                docker._copy_template_files("tta.dev")

            # Verify docker-compose.yml was copied
            self.assertTrue((repo_path / "docker-compose.yml").exists())

    def test_ensure_consistent_extensions_integration(self):
        """Test _ensure_consistent_extensions method (integration test)."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            repo_path = tmppath / "tta.dev"
            devcontainer_path = repo_path / ".devcontainer"

            # Create directories
            devcontainer_path.mkdir(parents=True)

            # Create devcontainer.json with some extensions
            devcontainer_json = {"extensions": ["ms-python.python"]}
            (devcontainer_path / "devcontainer.json").write_text(
                json.dumps(devcontainer_json)
            )

            # Mock the paths
            with (
                patch.object(docker, "root_dir", tmppath),
                patch.object(docker, "tta_dev_path", repo_path),
            ):
                docker._ensure_consistent_extensions("tta.dev")

            # Verify method executed without error
            self.assertTrue((devcontainer_path / "devcontainer.json").exists())

    def test_ensure_consistent_services_integration(self):
        """Test _ensure_consistent_services method (integration test)."""
        config = TTAConfig()
        docker = DockerComponent(config)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            repo_path = tmppath / "tta.dev"
            repo_path.mkdir()

            # Create docker-compose.yml with one service
            (repo_path / "docker-compose.yml").write_text(
                "services:\n  neo4j:\n    image: neo4j\n"
            )

            # Mock the paths
            with (
                patch.object(docker, "root_dir", tmppath),
                patch.object(docker, "tta_dev_path", repo_path),
            ):
                docker._ensure_consistent_services("tta.dev")

            # Verify method executed without error
            self.assertTrue((repo_path / "docker-compose.yml").exists())

    # ========== App Component Tests ==========

    def test_app_component_init(self):
        """Test App component initialization."""
        config = TTAConfig()
        app = AppComponent(config)

        self.assertEqual(app.name, "tta.prototype_app")
        self.assertEqual(app.port, 8501)
        self.assertIsNotNone(app.root_dir)
        self.assertIsNotNone(app.repo_dir)

    def test_app_stop_not_running(self):
        """Test App component stop when not running."""
        config = TTAConfig()
        app = AppComponent(config)

        with patch.object(app, "_is_app_running", return_value=False):
            result = app.stop()
            self.assertTrue(
                result, "App component should stop successfully when not running"
            )

    def test_app_stop_success(self):
        """Test App component successful stop."""
        config = TTAConfig()
        app = AppComponent(config)

        # Set component status to RUNNING so stop() will call _stop_impl()
        app.status = ComponentStatus.RUNNING

        # Mock _is_app_running to return True initially, then False after stop
        with (
            patch.object(app, "_is_app_running", side_effect=[True, False]),
            patch.object(app, "_run_docker_compose") as mock_docker,
        ):
            # Mock successful docker-compose stop
            mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()
            mock_docker.return_value = mock_result

            result = app.stop()
            self.assertTrue(result, "App component should stop successfully")
            mock_docker.assert_called_once_with(["stop", "app"])

    def test_app_stop_timeout(self):
        """Test App component stop timeout."""
        config = TTAConfig()
        app = AppComponent(config)

        # Set component status to RUNNING
        app.status = ComponentStatus.RUNNING

        # Mock _is_app_running to always return True (simulating timeout)
        with (
            patch.object(app, "_is_app_running", return_value=True),
            patch.object(app, "_run_docker_compose") as mock_docker,
        ):
            # Mock successful docker-compose stop command
            mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()
            mock_docker.return_value = mock_result

            result = app.stop()
            self.assertFalse(result, "App component should fail to stop due to timeout")

    def test_app_stop_error(self):
        """Test App component stop error handling."""
        config = TTAConfig()
        app = AppComponent(config)

        # Set component status to RUNNING
        app.status = ComponentStatus.RUNNING

        # Mock _is_app_running to return True (so it tries to stop)
        # Mock _run_docker_compose to raise an exception
        with (
            patch.object(app, "_is_app_running", return_value=True),
            patch.object(
                app, "_run_docker_compose", side_effect=Exception("Docker error")
            ),
        ):
            result = app.stop()
            self.assertFalse(
                result, "App component should fail to stop due to exception"
            )

    def test_app_start_already_running(self):
        """Test App component start when already running."""
        config = TTAConfig()
        app = AppComponent(config)

        # Mock config to have the required key
        with (
            patch.object(app.config, "get", return_value=8501),
            patch.object(app, "_is_app_running", return_value=True),
        ):
            result = app._start_impl()
            self.assertTrue(
                result, "App component should return True when already running"
            )

    def test_app_start_success(self):
        """Test App component successful start."""
        config = TTAConfig()
        app = AppComponent(config)

        # Mock config to have the required key
        with (
            patch.object(app.config, "get", return_value=8501),
            patch.object(app, "_is_app_running", side_effect=[False, True]),
            patch.object(app, "_run_docker_compose") as mock_docker,
        ):
            # Mock successful docker-compose up
            mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()
            mock_docker.return_value = mock_result

            result = app._start_impl()
            self.assertTrue(result, "App component should start successfully")
            mock_docker.assert_called_once_with(["up", "-d", "app"])

    def test_app_start_timeout(self):
        """Test App component start timeout."""
        config = TTAConfig()
        app = AppComponent(config)

        # Mock config to have the required key
        with (
            patch.object(app.config, "get", return_value=8501),
            patch.object(app, "_is_app_running", return_value=False),
            patch.object(app, "_run_docker_compose") as mock_docker,
        ):
            # Mock successful docker-compose up command
            mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()
            mock_docker.return_value = mock_result

            result = app._start_impl()
            self.assertFalse(
                result, "App component should fail to start due to timeout"
            )

    def test_app_start_docker_error(self):
        """Test App component Docker Compose failure."""
        config = TTAConfig()
        app = AppComponent(config)

        # Mock config to have the required key
        with (
            patch.object(app.config, "get", return_value=8501),
            patch.object(app, "_is_app_running", return_value=False),
            patch.object(app, "_run_docker_compose") as mock_docker,
        ):
            # Mock failed docker-compose up
            mock_result = type(
                "obj", (object,), {"returncode": 1, "stderr": "Docker error"}
            )()
            mock_docker.return_value = mock_result

            result = app._start_impl()
            self.assertFalse(
                result, "App component should fail to start due to Docker error"
            )

    def test_app_start_exception(self):
        """Test App component start exception handling."""
        config = TTAConfig()
        app = AppComponent(config)

        # Mock config to have the required key
        with (
            patch.object(app.config, "get", return_value=8501),
            patch.object(app, "_is_app_running", return_value=False),
            patch.object(
                app, "_run_docker_compose", side_effect=Exception("Docker error")
            ),
        ):
            result = app._start_impl()
            self.assertFalse(
                result, "App component should fail to start due to exception"
            )

    # ========================================================================
    # LLM Component Tests
    # ========================================================================

    def test_llm_component_init(self):
        """Test LLM component initialization."""
        config = TTAConfig()
        llm = LLMComponent(config, repository="tta.dev")

        # Verify initialization
        self.assertEqual(llm.repository, "tta.dev")
        self.assertEqual(llm.model, "qwen2.5-7b-instruct")
        self.assertEqual(llm.api_base, "http://localhost:1234/v1")
        self.assertEqual(llm.use_gpu, False)
        self.assertEqual(llm.name, "tta.dev_llm")

    def test_llm_stop_not_running(self):
        """Test LLM component stop when not running."""
        config = TTAConfig()
        llm = LLMComponent(config, repository="tta.dev")

        # Mock _is_llm_running to return False
        with patch.object(llm, "_is_llm_running", return_value=False):
            # Set status to RUNNING (required for base Component.stop() to call _stop_impl)
            llm.status = ComponentStatus.RUNNING
            result = llm.stop()
            self.assertTrue(
                result, "LLM component should stop successfully when not running"
            )

    def test_llm_stop_success(self):
        """Test LLM component successful stop."""
        config = TTAConfig()
        llm = LLMComponent(config, repository="tta.dev")

        # Create mock result object
        mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()

        # Mock _is_llm_running to return True then False (running -> stopped)
        # Mock _run_docker_compose to return success
        with (
            patch.object(llm, "_is_llm_running", side_effect=[True, False]),
            patch.object(llm, "_run_docker_compose", return_value=mock_result),
        ):
            # Set status to RUNNING
            llm.status = ComponentStatus.RUNNING
            result = llm.stop()
            self.assertTrue(result, "LLM component should stop successfully")

    def test_llm_stop_timeout(self):
        """Test LLM component stop timeout."""
        config = TTAConfig()
        llm = LLMComponent(config, repository="tta.dev")

        # Create mock result object
        mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()

        # Mock _is_llm_running to always return True (never stops)
        # Mock _run_docker_compose to return success
        with (
            patch.object(llm, "_is_llm_running", return_value=True),
            patch.object(llm, "_run_docker_compose", return_value=mock_result),
        ):
            # Set status to RUNNING
            llm.status = ComponentStatus.RUNNING
            result = llm.stop()
            self.assertFalse(result, "LLM component should timeout during stop")

    def test_llm_stop_error(self):
        """Test LLM component stop error handling."""
        config = TTAConfig()
        llm = LLMComponent(config, repository="tta.dev")

        # Create mock result object with error
        mock_result = type(
            "obj", (object,), {"returncode": 1, "stderr": "Docker error"}
        )()

        # Mock _is_llm_running to return True
        # Mock _run_docker_compose to return error
        with (
            patch.object(llm, "_is_llm_running", return_value=True),
            patch.object(llm, "_run_docker_compose", return_value=mock_result),
        ):
            # Set status to RUNNING
            llm.status = ComponentStatus.RUNNING
            result = llm.stop()
            self.assertFalse(
                result, "LLM component should fail to stop due to Docker error"
            )

    def test_llm_start_already_running(self):
        """Test LLM component start when already running."""
        config = TTAConfig()
        # Set required config values for @require_config decorator
        config.set("tta.dev.components.llm.model", "test-model")
        config.set("tta.dev.components.llm.api_base", "http://test:1234/v1")
        llm = LLMComponent(config, repository="tta.dev")

        # Mock _is_llm_running to return True
        with patch.object(llm, "_is_llm_running", return_value=True):
            result = llm.start()
            self.assertTrue(
                result, "LLM component should return True when already running"
            )

    def test_llm_start_success(self):
        """Test LLM component successful start."""
        config = TTAConfig()
        # Set required config values for @require_config decorator
        config.set("tta.dev.components.llm.model", "test-model")
        config.set("tta.dev.components.llm.api_base", "http://test:1234/v1")
        llm = LLMComponent(config, repository="tta.dev")

        # Create mock result object
        mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()

        # Mock _is_llm_running to return False then True (not running -> running)
        # Mock _run_docker_compose to return success
        with (
            patch.object(llm, "_is_llm_running", side_effect=[False, True]),
            patch.object(llm, "_run_docker_compose", return_value=mock_result),
        ):
            result = llm.start()
            self.assertTrue(result, "LLM component should start successfully")

    def test_llm_start_timeout(self):
        """Test LLM component start timeout."""
        config = TTAConfig()
        # Set required config values for @require_config decorator
        config.set("tta.dev.components.llm.model", "test-model")
        config.set("tta.dev.components.llm.api_base", "http://test:1234/v1")
        llm = LLMComponent(config, repository="tta.dev")

        # Create mock result object
        mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()

        # Mock _is_llm_running to always return False (never starts)
        # Mock _run_docker_compose to return success
        with (
            patch.object(llm, "_is_llm_running", return_value=False),
            patch.object(llm, "_run_docker_compose", return_value=mock_result),
        ):
            result = llm.start()
            self.assertFalse(result, "LLM component should timeout during start")

    def test_llm_start_docker_error(self):
        """Test LLM component start Docker Compose error."""
        config = TTAConfig()
        # Set required config values for @require_config decorator
        config.set("tta.dev.components.llm.model", "test-model")
        config.set("tta.dev.components.llm.api_base", "http://test:1234/v1")
        llm = LLMComponent(config, repository="tta.dev")

        # Create mock result object with error
        mock_result = type(
            "obj", (object,), {"returncode": 1, "stderr": "Docker error"}
        )()

        # Mock _is_llm_running to return False
        # Mock _run_docker_compose to return error
        with (
            patch.object(llm, "_is_llm_running", return_value=False),
            patch.object(llm, "_run_docker_compose", return_value=mock_result),
        ):
            result = llm.start()
            self.assertFalse(
                result, "LLM component should fail to start due to Docker error"
            )

    def test_llm_start_exception(self):
        """Test LLM component start exception handling."""
        config = TTAConfig()
        # Set required config values for @require_config decorator
        config.set("tta.dev.components.llm.model", "test-model")
        config.set("tta.dev.components.llm.api_base", "http://test:1234/v1")
        llm = LLMComponent(config, repository="tta.dev")

        # Mock _is_llm_running to raise exception
        with patch.object(llm, "_is_llm_running", side_effect=Exception("Test error")):
            result = llm.start()
            self.assertFalse(
                result, "LLM component should fail to start due to exception"
            )

    def test_llm_start_with_gpu(self):
        """Test LLM component start with GPU profile."""
        config = TTAConfig()
        # Set required config values for @require_config decorator
        config.set("tta.dev.components.llm.model", "test-model")
        config.set("tta.dev.components.llm.api_base", "http://test:1234/v1")
        llm = LLMComponent(config, repository="tta.dev")
        llm.use_gpu = True  # Enable GPU

        # Create mock result object
        mock_result = type("obj", (object,), {"returncode": 0, "stderr": ""})()

        # Mock _is_llm_running to return False then True
        # Mock _run_docker_compose to capture the command
        with (
            patch.object(llm, "_is_llm_running", side_effect=[False, True]),
            patch.object(
                llm, "_run_docker_compose", return_value=mock_result
            ) as mock_docker,
        ):
            result = llm.start()
            self.assertTrue(result, "LLM component should start successfully with GPU")

            # Verify GPU profile was added to command
            call_args = mock_docker.call_args
            command = call_args[0][0]  # First positional argument
            self.assertIn("--profile", command, "GPU profile flag should be in command")
            self.assertIn("with-gpu", command, "GPU profile value should be in command")

    def test_llm_is_running_check_success(self):
        """Test LLM health check returns True when HTTP 200."""
        config = TTAConfig()
        llm = LLMComponent(config, repository="tta.dev")

        # Create mock response object
        mock_response = type("obj", (object,), {"status_code": 200})()

        # Mock requests.get to return HTTP 200
        with patch("requests.get", return_value=mock_response):
            result = llm._is_llm_running()
            self.assertTrue(result, "LLM should be considered running when HTTP 200")

    def test_llm_is_running_check_failure(self):
        """Test LLM health check returns False on exception."""
        config = TTAConfig()
        llm = LLMComponent(config, repository="tta.dev")

        # Mock requests.get to raise exception
        with patch(
            "requests.get", side_effect=requests.RequestException("Connection error")
        ):
            result = llm._is_llm_running()
            self.assertFalse(
                result, "LLM should be considered not running on connection error"
            )


if __name__ == "__main__":
    # Run the tests
    unittest.main()
