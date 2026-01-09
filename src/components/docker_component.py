"""

# Logseq: [[TTA.dev/Components/Docker_component]]
Docker Component.

This module provides a component for managing Docker configurations across repositories.

Classes:
    DockerComponent: Component for managing Docker configurations

Example:
    ```python
    from src.orchestration import TTAConfig
    from src.components.docker_component import DockerComponent

    # Create a configuration object
    config = TTAConfig()

    # Create a Docker component
    docker = DockerComponent(config)

    # Start the Docker component (standardize configurations)
    docker.start()

    # Ensure Docker consistency across repositories
    docker.ensure_consistency()
    ```
"""

import logging
import shutil
from pathlib import Path
from typing import Any

from src.common.process_utils import run as safe_run

# Try to import codecarbon for carbon tracking
try:
    from codecarbon import track_emissions

    _codecarbon_available = True
except ImportError:
    _codecarbon_available = False

    # Define a no-op decorator
    def track_emissions(*args, **_kwargs):
        def decorator(func):
            return func

        return decorator if args and callable(args[0]) else decorator


from src.orchestration.component import Component
from src.orchestration.decorators import log_entry_exit, timing_decorator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DockerComponent(Component):
    """
    Component for managing Docker configurations across repositories.

    This component ensures Docker configurations are consistent across
    both tta.dev and tta.prototype repositories. It provides methods for
    standardizing container names, environment variables, and services.

    Attributes:
        root_dir: Root directory of the project
        tta_dev_path: Path to the tta.dev repository
        tta_prototype_path: Path to the tta.prototype repository
        templates_path: Path to the templates directory
    """

    def __init__(self, config: Any):
        """
        Initialize the Docker component.

        Args:
            config: Configuration object
        """
        super().__init__(config, name="docker", dependencies=[])

        self.root_dir = Path(__file__).parent.parent.parent
        self.tta_dev_path = self.root_dir / "tta.dev"
        self.tta_prototype_path = self.root_dir / "tta.prototype"
        self.templates_path = self.root_dir / "templates"

        logger.info("Initialized Docker component")

    @log_entry_exit
    @timing_decorator
    @track_emissions(project_name="TTA")
    def _start_impl(self) -> bool:
        """
        Start the Docker component.

        This method ensures Docker configurations are consistent across repositories.

        Returns:
            bool: True if the component was started successfully, False otherwise
        """
        try:
            # Check if Docker is installed
            self._check_docker_installed()

            # Ensure Docker consistency across repositories
            self.ensure_consistency()

            return True
        except Exception as e:
            logger.error(f"Error starting Docker component: {e}")
            return False

    @log_entry_exit
    @timing_decorator
    def _stop_impl(self) -> bool:
        """
        Stop the Docker component.

        This method doesn't actually stop anything since the Docker component
        is just a utility for ensuring consistency.

        Returns:
            bool: True if the component was stopped successfully, False otherwise
        """
        return True

    def _check_docker_installed(self) -> bool:
        """
        Check if Docker is installed.

        Returns:
            bool: True if Docker is installed, False otherwise

        Raises:
            RuntimeError: If Docker is not installed
        """
        try:
            result = safe_run(
                ["docker", "--version"],
                text=True,
                timeout=60,
                capture_output=True,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError("Docker is not installed or not in PATH")

            logger.info(f"Docker is installed: {result.stdout.strip()}")
            return True
        except Exception as e:
            logger.error(f"Error checking Docker installation: {e}")
            raise RuntimeError(f"Docker is not installed or not accessible: {e}") from e

    @log_entry_exit
    @timing_decorator
    def ensure_consistency(self) -> bool:
        """
        Ensure Docker configurations are consistent across repositories.

        This method checks and standardizes Docker configurations across
        both tta.dev and tta.prototype repositories.

        Returns:
            bool: True if consistency was ensured, False otherwise
        """
        try:
            # Process tta.dev repository
            if self.tta_dev_path.exists():
                logger.info("Processing tta.dev repository...")
                self._copy_template_files("tta.dev")
                self._standardize_container_names("tta.dev")
                self._ensure_consistent_extensions("tta.dev")
                self._ensure_consistent_env_vars("tta.dev")
                self._ensure_consistent_services("tta.dev")
                logger.info("tta.dev repository processed successfully")
            else:
                logger.error(f"tta.dev repository not found at {self.tta_dev_path}")
                return False

            # Process tta.prototype repository
            if self.tta_prototype_path.exists():
                logger.info("Processing tta.prototype repository...")
                self._copy_template_files("tta.prototype")
                self._standardize_container_names("tta.prototype")
                self._ensure_consistent_extensions("tta.prototype")
                self._ensure_consistent_env_vars("tta.prototype")
                self._ensure_consistent_services("tta.prototype")
                logger.info("tta.prototype repository processed successfully")
            else:
                logger.error(
                    f"tta.prototype repository not found at {self.tta_prototype_path}"
                )
                return False

            logger.info("Docker consistency ensured across repositories")
            return True
        except Exception as e:
            logger.error(f"Error ensuring Docker consistency: {e}")
            return False

    def _copy_template_files(self, repo_name: str) -> None:
        """
        Copy template files to a repository if they don't exist.

        Args:
            repo_name: Name of the repository
        """
        repo_path = self.root_dir / repo_name
        template_path = self.templates_path / repo_name

        logger.info(f"Checking Docker files for {repo_name}...")

        # Check Dockerfile
        if (
            not (repo_path / "Dockerfile").exists()
            and (template_path / "Dockerfile").exists()
        ):
            logger.info(f"Copying Dockerfile template to {repo_name}...")
            shutil.copy(template_path / "Dockerfile", repo_path / "Dockerfile")
            logger.info(f"Copied Dockerfile template to {repo_name}")

        # Check docker-compose.yml
        if (
            not (repo_path / "docker-compose.yml").exists()
            and (template_path / "docker-compose.yml").exists()
        ):
            logger.info(f"Copying docker-compose.yml template to {repo_name}...")
            shutil.copy(
                template_path / "docker-compose.yml", repo_path / "docker-compose.yml"
            )
            logger.info(f"Copied docker-compose.yml template to {repo_name}")

        # Check devcontainer.json
        if (
            not (repo_path / ".devcontainer" / "devcontainer.json").exists()
            and (template_path / ".devcontainer" / "devcontainer.json").exists()
        ):
            logger.info(f"Copying devcontainer.json template to {repo_name}...")
            (repo_path / ".devcontainer").mkdir(parents=True, exist_ok=True)
            shutil.copy(
                template_path / ".devcontainer" / "devcontainer.json",
                repo_path / ".devcontainer" / "devcontainer.json",
            )
            logger.info(f"Copied devcontainer.json template to {repo_name}")

        logger.info(f"Docker files for {repo_name} are in place")

    def _standardize_container_names(self, repo_name: str) -> None:
        """
        Standardize container names in a repository.

        Args:
            repo_name: Name of the repository
        """
        repo_path = self.root_dir / repo_name
        docker_compose_path = repo_path / "docker-compose.yml"

        logger.info(f"Standardizing container names in {repo_name}...")

        if docker_compose_path.exists():
            # Read the docker-compose.yml file
            with docker_compose_path.open() as f:
                content = f.read()

            # Replace container names
            repo_prefix = repo_name.replace("tta.", "")
            updated_content = content.replace(
                "container_name: tta-", f"container_name: tta-{repo_prefix}-"
            )

            # Write the updated content back to the file
            with docker_compose_path.open("w") as f:
                f.write(updated_content)

            logger.info(f"Standardized container names in {repo_name}")

    def _ensure_consistent_extensions(self, repo_name: str) -> None:
        """
        Ensure consistent VS Code extensions in a repository.

        Args:
            repo_name: Name of the repository
        """
        repo_path = self.root_dir / repo_name
        devcontainer_path = repo_path / ".devcontainer" / "devcontainer.json"

        logger.info(f"Ensuring consistent VS Code extensions in {repo_name}...")

        if devcontainer_path.exists():
            # Read the devcontainer.json file
            with devcontainer_path.open() as f:
                content = f.read()

            # Check for essential extensions
            essential_extensions = [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-python.flake8",
                "ms-azuretools.vscode-docker",
                "ms-vscode-remote.remote-containers",
                "neo4j-extensions.neo4j-for-vscode",
            ]

            missing_extensions = [
                ext for ext in essential_extensions if ext not in content
            ]

            if missing_extensions:
                logger.warning(
                    f"Missing extensions in {repo_name}: {', '.join(missing_extensions)}"
                )
                logger.warning(f"Please add these extensions to {devcontainer_path}")
            else:
                logger.info(f"All essential extensions are present in {repo_name}")

    def _get_env_var_default(self, var_name: str) -> str:
        """
        Get the default value for an environment variable.

        Args:
            var_name: Name of the environment variable

        Returns:
            str: Default value for the variable
        """
        defaults = {
            "NEO4J_PASSWORD": "password",  # pragma: allowlist secret
            "NEO4J_URI": "bolt://neo4j:7687",
            "NEO4J_USERNAME": "neo4j",
            "MODEL_CACHE_DIR": "/app/.model_cache",
            "CODECARBON_OUTPUT_DIR": "/app/logs/codecarbon",
        }
        return defaults.get(var_name, "default_value")

    def _ensure_consistent_env_vars(self, repo_name: str) -> None:
        """
        Ensure consistent environment variables in a repository.

        Args:
            repo_name: Name of the repository
        """
        repo_path = self.root_dir / repo_name
        env_example_path = repo_path / ".env.example"

        logger.info(f"Ensuring consistent environment variables in {repo_name}...")

        # Create .env.example if it doesn't exist
        if not env_example_path.exists():
            self._create_env_example(repo_name, env_example_path)
        else:
            self._add_missing_env_vars(repo_name, env_example_path)

    def _create_env_example(self, repo_name: str, env_example_path: Path) -> None:
        """
        Create .env.example file for a repository.

        Args:
            repo_name: Name of the repository
            env_example_path: Path to the .env.example file
        """
        logger.info(f"Creating .env.example in {repo_name}...")

        template_env_path = self.templates_path / repo_name / ".env.example"
        if template_env_path.exists():
            shutil.copy(template_env_path, env_example_path)
        else:
            with env_example_path.open("w") as f:
                f.write("# TTA Environment Variables\n")
                f.write("NEO4J_PASSWORD=password\n")
                f.write("NEO4J_URI=bolt://neo4j:7687\n")
                f.write("NEO4J_USERNAME=neo4j\n")
                f.write("MODEL_CACHE_DIR=/app/.model_cache\n")
                f.write("CODECARBON_OUTPUT_DIR=/app/logs/codecarbon\n")

        logger.info(f"Created .env.example in {repo_name}")

    def _add_missing_env_vars(self, repo_name: str, env_example_path: Path) -> None:
        """
        Add missing environment variables to .env.example file.

        Args:
            repo_name: Name of the repository
            env_example_path: Path to the .env.example file
        """
        with env_example_path.open() as f:
            content = f.read()

        essential_vars = [
            "NEO4J_PASSWORD",
            "NEO4J_URI",
            "NEO4J_USERNAME",
            "MODEL_CACHE_DIR",
            "CODECARBON_OUTPUT_DIR",
        ]

        missing_vars = [var for var in essential_vars if var not in content]

        if missing_vars:
            logger.info(f"Adding missing environment variables to {repo_name}...")

            with env_example_path.open("a") as f:
                for var in missing_vars:
                    default_value = self._get_env_var_default(var)
                    f.write(f"{var}={default_value}\n")

            logger.info(f"Added missing environment variables to {repo_name}")
        else:
            logger.info(
                f"All essential environment variables are present in {repo_name}"
            )

    def _ensure_consistent_services(self, repo_name: str) -> None:
        """
        Ensure consistent Docker Compose services in a repository.

        Args:
            repo_name: Name of the repository
        """
        repo_path = self.root_dir / repo_name
        docker_compose_path = repo_path / "docker-compose.yml"

        logger.info(f"Ensuring consistent Docker Compose services in {repo_name}...")

        if docker_compose_path.exists():
            # Read the docker-compose.yml file
            with docker_compose_path.open() as f:
                content = f.read()

            # Check for essential services
            essential_services = ["neo4j:", "app:"]

            missing_services = [
                service.replace(":", "")
                for service in essential_services
                if service not in content
            ]

            if missing_services:
                logger.warning(
                    f"Missing services in {repo_name}: {', '.join(missing_services)}"
                )
                logger.warning(f"Please add these services to {docker_compose_path}")
            else:
                logger.info(f"All essential services are present in {repo_name}")
