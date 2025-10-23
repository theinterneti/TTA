"""
Spec to Production Workflow

Main workflow orchestrator that integrates:
- AI Context Management (session tracking)
- Error Recovery (retry logic)
- Development Observability (metrics tracking)
- Quality Gates (validation)
- Component Maturity Workflow (dev→staging→production)

Usage:
    python spec_to_production.py \\
        --spec specs/my_component.md \\
        --component my_component \\
        --target staging

    # Or use as module:
    from workflow.spec_to_production import run_workflow

    result = run_workflow(
        spec_file="specs/my_component.md",
        component_name="my_component",
        target_stage="staging"
    )
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.observability.dashboard import generate_dashboard
from scripts.observability.dev_metrics import get_collector, track_execution
from scripts.primitives.error_recovery import RetryConfig, with_retry

# Import context manager
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".augment"))
    from context.conversation_manager import (
        AIConversationContextManager,
        create_tta_session,
    )
    CONTEXT_MANAGER_AVAILABLE = True
except ImportError:
    CONTEXT_MANAGER_AVAILABLE = False
    print("WARNING: AI Context Manager not available")

from scripts.workflow.stage_handlers import (
    ProductionDeploymentStage,
    RefactoringStage,
    SpecificationParser,
    StageResult,
    StagingDeploymentStage,
    TestingStage,
)


@dataclass
class WorkflowResult:
    """Result of complete workflow execution."""

    success: bool
    component_name: str
    target_stage: str
    stages_completed: list[str] = field(default_factory=list)
    stages_failed: list[str] = field(default_factory=list)
    stage_results: dict[str, StageResult] = field(default_factory=dict)
    total_execution_time_ms: float = 0.0
    context_session_id: str | None = None
    metrics_dashboard: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "component_name": self.component_name,
            "target_stage": self.target_stage,
            "stages_completed": self.stages_completed,
            "stages_failed": self.stages_failed,
            "stage_results": {
                name: result.to_dict() for name, result in self.stage_results.items()
            },
            "total_execution_time_ms": self.total_execution_time_ms,
            "context_session_id": self.context_session_id,
            "metrics_dashboard": self.metrics_dashboard,
        }

    def save_report(self, output_file: Path):
        """Save workflow report to file."""
        with open(output_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class WorkflowOrchestrator:
    """Orchestrates the complete spec-to-production workflow."""

    def __init__(
        self,
        spec_file: Path,
        component_name: str,
        target_stage: str = "staging",
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize workflow orchestrator.

        Args:
            spec_file: Path to specification file
            component_name: Name of component
            target_stage: Target maturity stage (dev/staging/production)
            config: Optional configuration overrides
        """
        self.spec_file = spec_file
        self.component_name = component_name
        self.target_stage = target_stage
        self.config = config or {}

        self.component_path = Path("src") / component_name

        # Initialize context manager session
        self.context_session_id = None
        self.context_manager = None
        if CONTEXT_MANAGER_AVAILABLE:
            self._init_context_session()

    def _init_context_session(self):
        """Initialize AI context management session."""
        try:
            session_id = f"{self.component_name}-workflow-{datetime.utcnow().strftime('%Y-%m-%d')}"
            self.context_manager, self.context_session_id = create_tta_session(session_id)

            # Add initial context
            self.context_manager.add_message(
                session_id=self.context_session_id,
                role="user",
                content=f"Starting workflow for component '{self.component_name}' targeting '{self.target_stage}' stage",
                importance=1.0,
            )
        except Exception as e:
            print(f"WARNING: Failed to initialize context session: {e}")

    def _update_context(self, message: str, importance: float = 0.7):
        """Update AI context with workflow progress."""
        if self.context_manager and self.context_session_id:
            try:
                self.context_manager.add_message(
                    session_id=self.context_session_id,
                    role="user",
                    content=message,
                    importance=importance,
                )
                self.context_manager.save_session(self.context_session_id)
            except Exception as e:
                print(f"WARNING: Failed to update context: {e}")

    @track_execution("workflow_complete")
    def run(self) -> WorkflowResult:
        """
        Run complete workflow.

        Returns:
            WorkflowResult with execution details
        """
        start_time = datetime.utcnow()

        result = WorkflowResult(
            success=False,
            component_name=self.component_name,
            target_stage=self.target_stage,
            context_session_id=self.context_session_id,
        )

        try:
            # Stage 1: Parse Specification
            spec_result = self._run_specification_stage()
            result.stage_results["specification"] = spec_result

            if not spec_result.success:
                result.stages_failed.append("specification")
                return result

            result.stages_completed.append("specification")
            self._update_context(
                f"Specification parsed successfully: {spec_result.outputs.get('spec_file')}",
                importance=0.9,
            )

            # Stage 2: Testing
            testing_result = self._run_testing_stage()
            result.stage_results["testing"] = testing_result

            if not testing_result.success:
                result.stages_failed.append("testing")
                self._update_context(
                    f"Testing stage failed: {', '.join(testing_result.errors)}",
                    importance=0.9,
                )
                return result

            result.stages_completed.append("testing")
            self._update_context(
                f"Testing stage passed: {testing_result.outputs.get('gates_passed')}",
                importance=0.9,
            )

            # Stage 3: Refactoring
            refactoring_result = self._run_refactoring_stage()
            result.stage_results["refactoring"] = refactoring_result

            if not refactoring_result.success:
                result.stages_failed.append("refactoring")
                self._update_context(
                    f"Refactoring stage failed: {', '.join(refactoring_result.errors)}",
                    importance=0.7,
                )
                return result

            result.stages_completed.append("refactoring")
            self._update_context(
                f"Refactoring stage passed: {refactoring_result.outputs.get('gates_passed')}",
                importance=0.7,
            )

            # Stage 4: Staging Deployment (if target is staging or production)
            if self.target_stage in ["staging", "production"]:
                staging_result = self._run_staging_deployment_stage()
                result.stage_results["staging_deployment"] = staging_result

                if not staging_result.success:
                    result.stages_failed.append("staging_deployment")
                    self._update_context(
                        f"Staging deployment failed: {', '.join(staging_result.errors)}",
                        importance=0.9,
                    )
                    return result

                result.stages_completed.append("staging_deployment")
                self._update_context(
                    f"Staging deployment successful",
                    importance=0.9,
                )

            # Stage 5: Production Deployment (if target is production)
            if self.target_stage == "production":
                production_result = self._run_production_deployment_stage()
                result.stage_results["production_deployment"] = production_result

                if not production_result.success:
                    result.stages_failed.append("production_deployment")
                    self._update_context(
                        f"Production deployment failed: {', '.join(production_result.errors)}",
                        importance=1.0,
                    )
                    return result

                result.stages_completed.append("production_deployment")
                self._update_context(
                    f"Production deployment successful - component is now in production!",
                    importance=1.0,
                )

            # All stages completed successfully
            result.success = True

            # Generate metrics dashboard
            dashboard_file = f"workflow_dashboard_{self.component_name}.html"
            generate_dashboard(output_file=dashboard_file, days=1)
            result.metrics_dashboard = dashboard_file

            # Calculate total execution time
            end_time = datetime.utcnow()
            result.total_execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return result

        except Exception as e:
            result.stages_failed.append("workflow_orchestration")
            self._update_context(
                f"Workflow failed with exception: {str(e)}",
                importance=1.0,
            )
            return result

    def _run_specification_stage(self) -> StageResult:
        """Run specification parsing stage."""
        parser = SpecificationParser(self.spec_file)
        return parser.parse()

    def _run_testing_stage(self) -> StageResult:
        """Run testing stage."""
        stage = TestingStage(self.component_path, self.config)
        return stage.execute()

    def _run_refactoring_stage(self) -> StageResult:
        """Run refactoring stage."""
        stage = RefactoringStage(self.component_path, self.config)
        return stage.execute()

    def _run_staging_deployment_stage(self) -> StageResult:
        """Run staging deployment stage."""
        stage = StagingDeploymentStage(self.component_path, self.config)
        return stage.execute()

    def _run_production_deployment_stage(self) -> StageResult:
        """Run production deployment stage."""
        stage = ProductionDeploymentStage(self.component_path, self.config)
        return stage.execute()


def run_workflow(
    spec_file: str,
    component_name: str,
    target_stage: str = "staging",
    config: dict[str, Any] | None = None,
) -> WorkflowResult:
    """
    Run complete spec-to-production workflow.

    Args:
        spec_file: Path to specification file
        component_name: Name of component
        target_stage: Target maturity stage (dev/staging/production)
        config: Optional configuration overrides

    Returns:
        WorkflowResult with execution details
    """
    orchestrator = WorkflowOrchestrator(
        spec_file=Path(spec_file),
        component_name=component_name,
        target_stage=target_stage,
        config=config,
    )

    return orchestrator.run()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run spec-to-production workflow for TTA components"
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to specification file",
    )
    parser.add_argument(
        "--component",
        required=True,
        help="Component name",
    )
    parser.add_argument(
        "--target",
        default="staging",
        choices=["dev", "staging", "production"],
        help="Target maturity stage (default: staging)",
    )
    parser.add_argument(
        "--output",
        help="Output file for workflow report (default: workflow_report_<component>.json)",
    )

    args = parser.parse_args()

    # Run workflow
    result = run_workflow(
        spec_file=args.spec,
        component_name=args.component,
        target_stage=args.target,
    )

    # Save report
    output_file = args.output or f"workflow_report_{args.component}.json"
    result.save_report(Path(output_file))

    # Print summary
    print("\n" + "=" * 60)
    print("WORKFLOW SUMMARY")
    print("=" * 60)
    print(f"Component: {result.component_name}")
    print(f"Target Stage: {result.target_stage}")
    print(f"Success: {'✓ YES' if result.success else '✗ NO'}")
    print(f"Stages Completed: {', '.join(result.stages_completed)}")
    if result.stages_failed:
        print(f"Stages Failed: {', '.join(result.stages_failed)}")
    print(f"Total Time: {result.total_execution_time_ms:.0f}ms")
    if result.context_session_id:
        print(f"Context Session: {result.context_session_id}")
    if result.metrics_dashboard:
        print(f"Metrics Dashboard: {result.metrics_dashboard}")
    print(f"Report Saved: {output_file}")
    print("=" * 60)

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
