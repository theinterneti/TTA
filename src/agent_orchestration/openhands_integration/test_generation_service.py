"""Unit test generation service using OpenHands.

This module provides a high-level service for generating unit tests with
iterative feedback and quality validation.
"""

import logging
from datetime import UTC, datetime
from pathlib import Path

from ..openhands_integration.client import create_openhands_client
from ..openhands_integration.config import OpenHandsConfig, OpenHandsIntegrationConfig
from .error_recovery import OpenHandsErrorRecovery
from .test_error_handler import classify_error, create_retry_feedback
from .test_file_extractor import extract_test_files_from_output
from .test_generation_models import (
    TestTaskSpecification,
    TestValidationResult,
)
from .test_result_validator import validate_generated_tests
from .test_task_builder import (
    create_test_generation_task,
)

# Import AI context management
try:
    import sys
    from pathlib import Path as PathLib

    # Add .augment to path if not already there
    augment_path = PathLib(__file__).resolve().parents[3] / ".augment"
    if str(augment_path) not in sys.path:
        sys.path.insert(0, str(augment_path))

    from context.conversation_manager import (
        AIConversationContextManager,
        create_tta_session,
    )

    AI_CONTEXT_AVAILABLE = True
except ImportError:
    AI_CONTEXT_AVAILABLE = False
    logging.warning("AI context management not available, session tracking disabled")

logger = logging.getLogger(__name__)


class UnitTestGenerationService:
    """Service for generating unit tests using OpenHands.

    This service orchestrates the entire test generation process:
    1. Create task description from specification
    2. Execute task with OpenHands
    3. Extract test files from output
    4. Validate tests (syntax, coverage, execution, conventions)
    5. If validation fails, provide feedback and retry
    6. Repeat until validation passes or max iterations reached

    Example:
        >>> config = OpenHandsConfig.from_env()
        >>> service = UnitTestGenerationService(config)
        >>> spec = TestTaskSpecification(
        ...     target_file=Path("src/agent_orchestration/tools/client.py"),
        ...     coverage_threshold=80.0,
        ... )
        >>> result = await service.generate_tests(spec)
        >>> print(result.coverage_percentage)
        85.5
    """

    def __init__(self, config: OpenHandsConfig | OpenHandsIntegrationConfig):
        """Initialize service with OpenHands configuration.

        Args:
            config: OpenHands configuration (OpenHandsConfig or OpenHandsIntegrationConfig)
        """
        self.config = config
        # Use factory function to create appropriate client (SDK or Docker)
        self.client = create_openhands_client(config)
        # Extract workspace path from config
        if isinstance(config, OpenHandsIntegrationConfig):
            self.workspace_path = config.workspace_root
            # Initialize error recovery for OpenHandsIntegrationConfig
            # (OpenHandsConfig doesn't have max_retries and retry_base_delay attributes)
            self.error_recovery = OpenHandsErrorRecovery(config=config)
        else:
            self.workspace_path = config.workspace_path
            # No error recovery for OpenHandsConfig
            self.error_recovery = None

    async def generate_tests(
        self,
        spec: TestTaskSpecification,
        max_iterations: int = 5,
    ) -> TestValidationResult:
        """Generate unit tests with iterative feedback.

        Args:
            spec: Test task specification
            max_iterations: Maximum number of iterations (default: 5)

        Returns:
            TestValidationResult with final validation results

        Example:
            >>> spec = TestTaskSpecification(
            ...     target_file=Path("src/agent_orchestration/tools/client.py"),
            ...     coverage_threshold=80.0,
            ... )
            >>> result = await service.generate_tests(spec)
            >>> print(result.syntax_valid, result.tests_pass)
            True True
        """
        logger.info(
            f"Generating tests for {spec.target_file} (max_iterations={max_iterations})"
        )

        # Create AI context session for tracking
        context_manager = None
        session_id = None
        if AI_CONTEXT_AVAILABLE:
            try:
                # Create session with format: openhands-test-gen-{target_file_stem}-{timestamp}
                timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
                target_file_stem = spec.target_file.stem
                session_id = f"openhands-test-gen-{target_file_stem}-{timestamp}"

                context_manager = AIConversationContextManager()
                context_manager.create_session(session_id)

                # Track task start (importance=0.9)
                context_manager.add_message(
                    session_id=session_id,
                    role="user",
                    content=f"Starting test generation for {spec.target_file} (coverage threshold: {spec.coverage_threshold}%, max iterations: {max_iterations})",
                    importance=0.9,
                    metadata={
                        "event": "task_start",
                        "target_file": str(spec.target_file),
                        "coverage_threshold": spec.coverage_threshold,
                        "max_iterations": max_iterations,
                    },
                )

                logger.info(f"Created AI context session: {session_id}")
            except Exception as e:
                logger.warning(f"Failed to create AI context session: {e}")
                context_manager = None
                session_id = None

        # Create initial task description
        task_description = create_test_generation_task(spec)

        # Initialize validation_result to None (will be set if any iteration succeeds)
        validation_result = None

        for iteration in range(max_iterations):
            logger.info(f"Iteration {iteration + 1}/{max_iterations}")

            # Track iteration start (importance=0.7)
            if context_manager and session_id:
                try:
                    context_manager.add_message(
                        session_id=session_id,
                        role="user",
                        content=f"Starting iteration {iteration + 1}/{max_iterations}",
                        importance=0.7,
                        metadata={
                            "event": "iteration_start",
                            "iteration": iteration + 1,
                            "max_iterations": max_iterations,
                        },
                    )
                except Exception as e:
                    logger.warning(f"Failed to track iteration start: {e}")

            # Execute task with OpenHands (with error recovery if available)
            if self.error_recovery:
                result = await self.error_recovery.execute_with_recovery(
                    self.client.execute_task,
                    task_description=task_description,
                    workspace_path=self.workspace_path,
                    timeout=spec.timeout_seconds,
                )
            else:
                result = await self.client.execute_task(
                    task_description=task_description,
                    workspace_path=self.workspace_path,
                    timeout=spec.timeout_seconds,
                )

            if not result.success:
                logger.warning(f"Task execution failed: {result.error}")

                # Classify error and create feedback
                error_type = classify_error(result)
                logger.info(f"Error classified as: {error_type}")

                # Create feedback for retry
                feedback = create_retry_feedback(
                    error_type, spec, result, self.workspace_path
                )
                task_description = f"{task_description}\n\n**Feedback from previous attempt:**\n{feedback}"

                # Continue to next iteration
                continue

            # Extract test files from output
            test_files = extract_test_files_from_output(
                result.output, self.workspace_path
            )

            if not test_files:
                logger.warning("No test files found in output")
                task_description = f"{task_description}\n\n**Feedback:** No test files were generated. Please ensure you create the test file and report its path."
                continue

            # Validate first test file (should only be one for single file generation)
            test_file = test_files[0]
            logger.info(f"Validating test file: {test_file}")

            validation_result = await validate_generated_tests(
                test_file=test_file,
                target_file=spec.target_file,
                coverage_threshold=spec.coverage_threshold,
                workspace_path=self.workspace_path,
            )

            # Track validation results (importance=0.9)
            if context_manager and session_id:
                try:
                    validation_status = (
                        "passed"
                        if (
                            validation_result.syntax_valid
                            and validation_result.tests_pass
                            and validation_result.coverage_percentage
                            >= spec.coverage_threshold
                            and validation_result.conventions_followed
                        )
                        else "failed"
                    )

                    context_manager.add_message(
                        session_id=session_id,
                        role="assistant",
                        content=f"Validation {validation_status} (iteration {iteration + 1}): syntax_valid={validation_result.syntax_valid}, tests_pass={validation_result.tests_pass}, coverage={validation_result.coverage_percentage}%, conventions={validation_result.conventions_followed}",
                        importance=0.9,
                        metadata={
                            "event": "validation_result",
                            "iteration": iteration + 1,
                            "status": validation_status,
                            "syntax_valid": validation_result.syntax_valid,
                            "tests_pass": validation_result.tests_pass,
                            "coverage_percentage": validation_result.coverage_percentage,
                            "conventions_followed": validation_result.conventions_followed,
                            "issues": validation_result.issues,
                        },
                    )
                except Exception as e:
                    logger.warning(f"Failed to track validation result: {e}")

            # Check if validation passed
            if (
                validation_result.syntax_valid
                and validation_result.tests_pass
                and validation_result.coverage_percentage >= spec.coverage_threshold
                and validation_result.conventions_followed
            ):
                logger.info(
                    f"✓ Test generation successful (coverage: {validation_result.coverage_percentage}%)"
                )

                # Track task completion (importance=1.0)
                if context_manager and session_id:
                    try:
                        context_manager.add_message(
                            session_id=session_id,
                            role="assistant",
                            content=f"Test generation completed successfully after {iteration + 1} iteration(s). Final coverage: {validation_result.coverage_percentage}%",
                            importance=1.0,
                            metadata={
                                "event": "task_complete",
                                "status": "success",
                                "iterations": iteration + 1,
                                "final_coverage": validation_result.coverage_percentage,
                            },
                        )

                        # Save session
                        context_manager.save_session(session_id)
                        logger.info(f"Saved AI context session: {session_id}")
                    except Exception as e:
                        logger.warning(f"Failed to save AI context session: {e}")

                return validation_result

            # Validation failed - create feedback for retry
            logger.warning(f"Validation failed: {validation_result.issues}")
            feedback = self._create_feedback_task(validation_result)
            task_description = (
                f"{task_description}\n\n**Feedback from previous attempt:**\n{feedback}"
            )

        # Max iterations reached - return last validation result or create failure result
        logger.warning(f"Max iterations ({max_iterations}) reached without success")

        # If no validation result (all iterations failed), create a failure result
        if validation_result is None:
            from .test_generation_models import TestValidationResult

            validation_result = TestValidationResult(
                syntax_valid=False,
                tests_pass=False,
                coverage_percentage=0.0,
                conventions_followed=False,
                quality_score=0.0,
                issues=["All iterations failed - no tests generated"],
            )

        # Track task completion with failure (importance=1.0)
        if context_manager and session_id:
            try:
                context_manager.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=f"Test generation failed after {max_iterations} iterations. Last coverage: {validation_result.coverage_percentage}%",
                    importance=1.0,
                    metadata={
                        "event": "task_complete",
                        "status": "failure",
                        "iterations": max_iterations,
                        "final_coverage": validation_result.coverage_percentage,
                        "issues": validation_result.issues,
                    },
                )

                # Save session
                context_manager.save_session(session_id)
                logger.info(f"Saved AI context session: {session_id}")
            except Exception as e:
                logger.warning(f"Failed to save AI context session: {e}")

        return validation_result

    async def generate_package_tests(
        self,
        package_path: Path,
        coverage_threshold: float = 70.0,
    ) -> dict[Path, TestValidationResult]:
        """Generate tests for all files in a package.

        Args:
            package_path: Path to package directory
            coverage_threshold: Minimum coverage percentage required (default: 70.0)

        Returns:
            Dictionary mapping file paths to validation results

        Example:
            >>> results = await service.generate_package_tests(
            ...     Path("src/agent_orchestration/tools"),
            ...     coverage_threshold=75.0,
            ... )
            >>> for file, result in results.items():
            ...     print(f"{file}: {result.coverage_percentage}%")
        """
        logger.info(f"Generating tests for package {package_path}")

        # Find all Python files in package
        full_package_path = self.workspace_path / package_path
        python_files = [
            f.relative_to(self.workspace_path)
            for f in full_package_path.rglob("*.py")
            if f.name != "__init__.py" and "__pycache__" not in str(f)
        ]

        logger.info(f"Found {len(python_files)} Python files in package")

        # Generate tests for each file
        results = {}
        for python_file in python_files:
            logger.info(f"Generating tests for {python_file}")

            spec = TestTaskSpecification(
                target_file=python_file,
                coverage_threshold=coverage_threshold,
            )

            result = await self.generate_tests(spec)
            results[python_file] = result

        return results

    def _create_feedback_task(self, validation_result: TestValidationResult) -> str:
        """Create feedback task from validation issues.

        Args:
            validation_result: Validation result with issues

        Returns:
            Feedback message for retry
        """
        feedback_parts = []

        if not validation_result.syntax_valid:
            feedback_parts.append("- Fix syntax errors in the test file")

        if not validation_result.tests_pass:
            feedback_parts.append("- Fix failing tests to ensure all tests pass")

        if validation_result.coverage_percentage < 70.0:  # Assuming default threshold
            feedback_parts.append(
                f"- Increase coverage from {validation_result.coverage_percentage}% to ≥70%"
            )

        if not validation_result.conventions_followed:
            feedback_parts.append("- Follow TTA testing conventions (see issues below)")

        if validation_result.issues:
            issues_list = "\n".join(
                f"  - {issue}" for issue in validation_result.issues
            )
            feedback_parts.append(f"- Address these specific issues:\n{issues_list}")

        feedback = "\n".join(feedback_parts)
        return f"The previous test generation had issues:\n\n{feedback}\n\nPlease fix these issues and regenerate the tests."
