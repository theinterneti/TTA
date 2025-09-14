"""
AgentOrchestrationService - Main API for multi-agent coordination (Task 16.1).

This service provides the primary interface for processing user input and coordinating
agents through sophisticated workflows, integrating therapeutic safety validation,
session context management, and tying together all orchestration components.
"""

import logging
import time
from typing import Any

from .agents import AgentRegistry
from .interfaces import MessageCoordinator
from .models import (
    AgentId,
    AgentType,
    OrchestrationRequest,
    OrchestrationResponse,
)
from .state import AgentContext, SessionContext
from .workflow import AgentStep, ErrorHandlingStrategy, WorkflowDefinition, WorkflowType
from .workflow_manager import WorkflowManager

logger = logging.getLogger(__name__)

# Type aliases for clarity
WorkflowResult = tuple[OrchestrationResponse | None, str | None, str | None]


class ServiceError(Exception):
    """Base exception for AgentOrchestrationService errors."""

    pass


class TherapeuticSafetyError(ServiceError):
    """Raised when therapeutic safety validation fails."""

    pass


class WorkflowExecutionError(ServiceError):
    """Raised when workflow execution fails."""

    pass


class SessionContextError(ServiceError):
    """Raised when session context management fails."""

    pass


class AgentOrchestrationService:
    """
    Main orchestration service providing the primary API for multi-agent coordination.

    This service serves as the central coordination layer for TTA's multi-agent architecture,
    managing the World Builder Agent (WBA), Input Processor Agent (IPA), and Narrative
    Generator Agent (NGA) through sophisticated workflow management.

    Key Responsibilities:
    - Route incoming requests to appropriate workflows
    - Coordinate agent execution sequences
    - Manage session state and context
    - Ensure therapeutic safety validation
    - Handle error recovery and fallback strategies
    """

    def __init__(
        self,
        workflow_manager: WorkflowManager,
        message_coordinator: MessageCoordinator,
        agent_registry: AgentRegistry,
        therapeutic_validator: Any | None = None,
        resource_manager: Any | None = None,
        optimization_engine: Any | None = None,
        neo4j_manager: Any | None = None,
        crisis_intervention_manager: Any | None = None,
        emergency_protocol_engine: Any | None = None,
        human_oversight_escalation: Any | None = None,
        safety_monitoring_dashboard: Any | None = None,
    ):
        """
        Initialize the AgentOrchestrationService.

        Args:
            workflow_manager: Manager for workflow registration and execution
            message_coordinator: Coordinator for agent message passing
            agent_registry: Registry for agent discovery and management
            therapeutic_validator: Optional validator for therapeutic content safety
            resource_manager: Optional manager for resource allocation and monitoring
            optimization_engine: Optional engine for performance optimization
            neo4j_manager: Optional manager for Neo4j state persistence
            crisis_intervention_manager: Optional manager for crisis interventions
            emergency_protocol_engine: Optional engine for emergency protocols
            human_oversight_escalation: Optional system for human oversight escalation
            safety_monitoring_dashboard: Optional dashboard for safety monitoring
        """
        self.workflow_manager = workflow_manager
        self.message_coordinator = message_coordinator
        self.agent_registry = agent_registry
        self.therapeutic_validator = therapeutic_validator
        self.resource_manager = resource_manager
        self.optimization_engine = optimization_engine
        self.neo4j_manager = neo4j_manager

        # Crisis intervention system components
        self.crisis_intervention_manager = crisis_intervention_manager
        self.emergency_protocol_engine = emergency_protocol_engine
        self.human_oversight_escalation = human_oversight_escalation
        self.safety_monitoring_dashboard = safety_monitoring_dashboard

        # Service state
        self._initialized = False
        self._session_contexts: dict[str, SessionContext] = {}
        self._active_workflows: dict[str, str] = {}  # session_id -> workflow_run_id

        # Performance metrics
        self._request_count = 0
        self._error_count = 0
        self._total_processing_time = 0.0

        logger.info("AgentOrchestrationService initialized")

    async def initialize(self) -> bool:
        """
        Initialize the service and register default workflows.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Register default workflows
            await self._register_default_workflows()

            # Validate component availability
            await self._validate_components()

            self._initialized = True
            logger.info("AgentOrchestrationService initialization complete")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize AgentOrchestrationService: {e}")
            return False

    async def process_user_input(
        self,
        user_input: str,
        session_context: SessionContext,
        workflow_type: WorkflowType | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OrchestrationResponse:
        """
        Process user input through the multi-agent orchestration system.

        This is the main entry point for processing user input. It handles therapeutic
        safety validation, determines the appropriate workflow type, and coordinates
        agent execution to generate a comprehensive response.

        Args:
            user_input: The user's input text to process
            session_context: Current session context and state
            workflow_type: Optional specific workflow type to use
            metadata: Optional additional metadata for processing

        Returns:
            OrchestrationResponse: Comprehensive response with generated content,
                                 updated context, and workflow metadata

        Raises:
            TherapeuticSafetyError: If therapeutic safety validation fails
            WorkflowExecutionError: If workflow execution fails
            SessionContextError: If session context management fails
        """
        if not self._initialized:
            raise ServiceError("Service not initialized. Call initialize() first.")

        start_time = time.time()
        self._request_count += 1

        try:
            # Store/update session context
            self._session_contexts[session_context.session_id] = session_context

            # Perform therapeutic safety validation
            await self._validate_therapeutic_safety(user_input, session_context)

            # Determine workflow type if not specified
            if workflow_type is None:
                workflow_type = await self._determine_workflow_type(
                    user_input, session_context
                )

            # Create orchestration request
            request = OrchestrationRequest(
                session_id=session_context.session_id,
                entrypoint=AgentType.IPA,
                input={
                    "text": user_input,
                    "session_context": session_context.model_dump(),
                    "metadata": metadata or {},
                },
            )

            # Execute workflow
            response = await self._execute_workflow_with_context(
                workflow_type, request, session_context, metadata
            )

            # Update session context with results
            await self._update_session_context(session_context, response)

            # Record performance metrics
            processing_time = time.time() - start_time
            self._total_processing_time += processing_time

            logger.info(
                f"Processed user input for session {session_context.session_id} "
                f"in {processing_time:.2f}s using {workflow_type.value} workflow"
            )

            return response

        except Exception as e:
            self._error_count += 1
            logger.error(f"Error processing user input: {e}")

            if isinstance(
                e, TherapeuticSafetyError | WorkflowExecutionError | SessionContextError
            ):
                raise
            else:
                raise ServiceError(f"Unexpected error during processing: {e}") from e

    async def coordinate_agents(
        self,
        workflow_type: WorkflowType,
        context: AgentContext,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """
        Coordinate agent execution for a specific workflow type.

        This method handles the actual agent coordination, managing workflow execution
        through the WorkflowManager, resource allocation, and agent communication.

        Args:
            workflow_type: Type of workflow to execute
            context: Agent context for workflow execution
            metadata: Optional metadata for workflow execution

        Returns:
            WorkflowResult: Tuple of (response, run_id, error) from workflow execution

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        if not self._initialized:
            raise ServiceError("Service not initialized. Call initialize() first.")

        try:
            # Create orchestration request from context
            request = OrchestrationRequest(
                session_id=context.session_id,
                entrypoint=AgentType.IPA,
                input=context.model_dump(),
            )

            # Get workflow name for the type
            workflow_name = self._get_workflow_name(workflow_type)

            # Allocate resources if resource manager available
            if self.resource_manager:
                await self._allocate_workflow_resources(workflow_type, context)

            # Execute workflow through WorkflowManager
            response, run_id, error = self.workflow_manager.execute_workflow(
                workflow_name, request, context, metadata
            )

            if error:
                logger.error(f"Workflow execution failed: {error}")
                raise WorkflowExecutionError(f"Workflow execution failed: {error}")

            logger.info(
                f"Successfully coordinated agents for {workflow_type.value} workflow"
            )
            return response, run_id, error

        except Exception as e:
            logger.error(f"Error coordinating agents: {e}")
            if isinstance(e, WorkflowExecutionError):
                raise
            else:
                raise WorkflowExecutionError(f"Agent coordination failed: {e}") from e

    def get_therapeutic_safety_metrics(self) -> dict[str, Any]:
        """Get therapeutic safety metrics from the validator."""
        try:
            if hasattr(self.therapeutic_validator, "get_monitoring_metrics"):
                return self.therapeutic_validator.get_monitoring_metrics()
            else:
                return {
                    "error": "Therapeutic validator does not support metrics",
                    "validator_available": self.therapeutic_validator is not None,
                }
        except Exception as e:
            logger.error(f"Error getting therapeutic safety metrics: {e}")
            return {"error": str(e)}

    def get_crisis_intervention_metrics(self) -> dict[str, Any]:
        """Get crisis intervention metrics from all crisis management components."""
        try:
            metrics = {
                "crisis_manager": {},
                "emergency_protocols": {},
                "human_oversight": {},
                "safety_dashboard": {},
            }

            if self.crisis_intervention_manager:
                metrics["crisis_manager"] = (
                    self.crisis_intervention_manager.get_crisis_metrics()
                )

            if self.emergency_protocol_engine:
                metrics["emergency_protocols"] = (
                    self.emergency_protocol_engine.get_protocol_metrics()
                )

            if self.human_oversight_escalation:
                metrics["human_oversight"] = (
                    self.human_oversight_escalation.get_escalation_metrics()
                )

            if self.safety_monitoring_dashboard:
                metrics["safety_dashboard"] = (
                    self.safety_monitoring_dashboard.get_real_time_status()
                )

            return metrics

        except Exception as e:
            logger.error(f"Error getting crisis intervention metrics: {e}")
            return {"error": str(e)}

    def get_crisis_dashboard(self) -> dict[str, Any]:
        """Get comprehensive crisis intervention dashboard."""
        try:
            if self.safety_monitoring_dashboard:
                return self.safety_monitoring_dashboard.get_crisis_dashboard()
            else:
                return {"error": "Safety monitoring dashboard not available"}
        except Exception as e:
            logger.error(f"Error getting crisis dashboard: {e}")
            return {"error": str(e)}

    def get_safety_report(self, time_range_hours: int = 24) -> dict[str, Any]:
        """Generate comprehensive safety report."""
        try:
            if self.safety_monitoring_dashboard:
                return self.safety_monitoring_dashboard.get_safety_report(
                    time_range_hours
                )
            else:
                return {"error": "Safety monitoring dashboard not available"}
        except Exception as e:
            logger.error(f"Error generating safety report: {e}")
            return {"error": str(e)}

    def get_service_status(self) -> dict[str, Any]:
        """
        Get current service status and metrics.

        Returns:
            Dict containing service status, metrics, and component health
        """
        return {
            "initialized": self._initialized,
            "active_sessions": len(self._session_contexts),
            "active_workflows": len(self._active_workflows),
            "metrics": {
                "request_count": self._request_count,
                "error_count": self._error_count,
                "error_rate": self._error_count / max(self._request_count, 1),
                "avg_processing_time": self._total_processing_time
                / max(self._request_count, 1),
            },
            "components": {
                "workflow_manager": self.workflow_manager is not None,
                "message_coordinator": self.message_coordinator is not None,
                "agent_registry": self.agent_registry is not None,
                "therapeutic_validator": self.therapeutic_validator is not None,
                "resource_manager": self.resource_manager is not None,
                "optimization_engine": self.optimization_engine is not None,
                "neo4j_manager": self.neo4j_manager is not None,
                "crisis_intervention_manager": self.crisis_intervention_manager
                is not None,
                "emergency_protocol_engine": self.emergency_protocol_engine is not None,
                "human_oversight_escalation": self.human_oversight_escalation
                is not None,
                "safety_monitoring_dashboard": self.safety_monitoring_dashboard
                is not None,
            },
        }

    async def shutdown(self) -> bool:
        """
        Gracefully shutdown the service.

        Returns:
            bool: True if shutdown successful, False otherwise
        """
        try:
            # Cancel active workflows
            for session_id, run_id in self._active_workflows.items():
                logger.info(
                    f"Cancelling active workflow {run_id} for session {session_id}"
                )
                # Note: Actual cancellation would depend on WorkflowManager implementation

            # Clear state
            self._session_contexts.clear()
            self._active_workflows.clear()
            self._initialized = False

            logger.info("AgentOrchestrationService shutdown complete")
            return True

        except Exception as e:
            logger.error(f"Error during service shutdown: {e}")
            return False

    # ============================================================================
    # Private Helper Methods
    # ============================================================================

    async def _register_default_workflows(self) -> None:
        """Register default workflows for common use cases."""
        try:
            # Standard collaborative workflow (IPA -> WBA -> NGA)
            collaborative_workflow = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(
                        agent=AgentType.IPA, name="input_processing", timeout_seconds=10
                    ),
                    AgentStep(
                        agent=AgentType.WBA, name="world_building", timeout_seconds=15
                    ),
                    AgentStep(
                        agent=AgentType.NGA,
                        name="narrative_generation",
                        timeout_seconds=20,
                    ),
                ],
                error_handling=ErrorHandlingStrategy.RETRY,
            )

            success, error = self.workflow_manager.register_workflow(
                "collaborative", collaborative_workflow
            )
            if not success:
                logger.warning(f"Failed to register collaborative workflow: {error}")

            # Input processing only workflow
            input_workflow = WorkflowDefinition(
                workflow_type=WorkflowType.INPUT_PROCESSING,
                agent_sequence=[
                    AgentStep(
                        agent=AgentType.IPA, name="input_processing", timeout_seconds=10
                    ),
                ],
                error_handling=ErrorHandlingStrategy.FAIL_FAST,
            )

            success, error = self.workflow_manager.register_workflow(
                "input_processing", input_workflow
            )
            if not success:
                logger.warning(f"Failed to register input processing workflow: {error}")

            # World building workflow
            world_building_workflow = WorkflowDefinition(
                workflow_type=WorkflowType.WORLD_BUILDING,
                agent_sequence=[
                    AgentStep(
                        agent=AgentType.WBA, name="world_building", timeout_seconds=15
                    ),
                ],
                error_handling=ErrorHandlingStrategy.RETRY,
            )

            success, error = self.workflow_manager.register_workflow(
                "world_building", world_building_workflow
            )
            if not success:
                logger.warning(f"Failed to register world building workflow: {error}")

            # Narrative generation workflow
            narrative_workflow = WorkflowDefinition(
                workflow_type=WorkflowType.NARRATIVE_GENERATION,
                agent_sequence=[
                    AgentStep(
                        agent=AgentType.NGA,
                        name="narrative_generation",
                        timeout_seconds=20,
                    ),
                ],
                error_handling=ErrorHandlingStrategy.RETRY,
            )

            success, error = self.workflow_manager.register_workflow(
                "narrative_generation", narrative_workflow
            )
            if not success:
                logger.warning(
                    f"Failed to register narrative generation workflow: {error}"
                )

            logger.info("Default workflows registered successfully")

        except Exception as e:
            logger.error(f"Error registering default workflows: {e}")
            raise ServiceError(f"Failed to register default workflows: {e}") from e

    async def _validate_components(self) -> None:
        """Validate that required components are available and functional."""
        try:
            # Check workflow manager
            if not self.workflow_manager:
                raise ServiceError("WorkflowManager is required but not provided")

            # Check message coordinator
            if not self.message_coordinator:
                raise ServiceError("MessageCoordinator is required but not provided")

            # Check agent registry
            if not self.agent_registry:
                raise ServiceError("AgentRegistry is required but not provided")

            # Validate agent availability
            required_agents = [AgentType.IPA, AgentType.WBA, AgentType.NGA]
            for agent_type in required_agents:
                agent_id = AgentId(type=agent_type, instance="default")
                agent = self.agent_registry.get(agent_id)
                if not agent:
                    logger.warning(f"Agent {agent_type.value} not found in registry")

            logger.info("Component validation completed successfully")

        except Exception as e:
            logger.error(f"Component validation failed: {e}")
            raise ServiceError(f"Component validation failed: {e}") from e

    async def _validate_therapeutic_safety(
        self, user_input: str, session_context: SessionContext
    ) -> None:
        """
        Validate therapeutic safety of user input.

        Args:
            user_input: User input to validate
            session_context: Current session context

        Raises:
            TherapeuticSafetyError: If validation fails
        """
        try:
            if self.therapeutic_validator:
                # Use the therapeutic validator if available
                validation_result = await self._call_therapeutic_validator(
                    user_input, session_context
                )

                if not validation_result.get("safe", True):
                    safety_level = validation_result.get("level", "unknown")
                    reason = validation_result.get("reason", "Safety validation failed")
                    crisis_detected = validation_result.get("crisis_detected", False)
                    escalation_recommended = validation_result.get(
                        "escalation_recommended", False
                    )
                    alternative_content = validation_result.get("alternative_content")

                    logger.warning(
                        f"Therapeutic safety validation failed for session "
                        f"{session_context.session_id}: {reason} (level: {safety_level})"
                    )

                    # For blocked content, high risk, or crisis situations, raise an error with alternative
                    if safety_level in ["blocked", "high_risk"] or crisis_detected:
                        error_message = (
                            f"Content blocked due to safety concerns: {reason}"
                        )
                        if alternative_content:
                            error_message += (
                                f"\n\nSuggested response: {alternative_content}"
                            )

                        raise TherapeuticSafetyError(error_message)

                    # For escalation cases, log but don't block (allow human oversight)
                    if escalation_recommended:
                        logger.critical(
                            f"Escalation recommended for session {session_context.session_id}: "
                            f"crisis_types={validation_result.get('crisis_types', [])}"
                        )
            else:
                # Basic safety checks if no validator available
                await self._basic_safety_checks(user_input)

        except TherapeuticSafetyError:
            raise
        except Exception as e:
            logger.error(f"Error during therapeutic safety validation: {e}")
            # Don't block processing for validation errors, but log them
            logger.warning("Proceeding with processing despite validation error")

    async def _call_therapeutic_validator(
        self, user_input: str, session_context: SessionContext
    ) -> dict[str, Any]:
        """Call the enhanced therapeutic validator."""
        try:
            # Import here to avoid circular imports
            from .therapeutic_safety import SafetyLevel, TherapeuticValidator

            # Use the provided validator or create a default one
            if hasattr(self.therapeutic_validator, "validate_text"):
                validator = self.therapeutic_validator
            else:
                # Fallback to default validator
                validator = TherapeuticValidator()

            # Prepare context for validation
            validation_context = {
                "session_id": session_context.session_id,
                "user_id": session_context.user_id,
                "session_count": getattr(session_context, "session_count", 0),
                "previous_violations": getattr(session_context, "safety_violations", 0),
                "therapeutic_session": True,
                "previous_crisis_indicators": getattr(
                    session_context, "crisis_indicators", False
                ),
            }

            # Perform comprehensive validation
            result = validator.validate_text(user_input, context=validation_context)

            # Check if we should alert on this result
            should_alert = (
                validator.should_alert(result)
                if hasattr(validator, "should_alert")
                else False
            )

            # Convert to expected format
            validation_result = {
                "safe": result.level == SafetyLevel.SAFE,
                "level": result.level.value,
                "score": result.score,
                "reason": f"Therapeutic validation: {result.level.value}",
                "crisis_detected": result.crisis_detected,
                "crisis_types": [ct.value for ct in result.crisis_types],
                "escalation_recommended": result.escalation_recommended,
                "alternative_content": result.alternative_content,
                "therapeutic_appropriateness": result.therapeutic_appropriateness,
                "monitoring_flags": result.monitoring_flags,
                "should_alert": should_alert,
                "findings_count": len(result.findings),
            }

            # Log important events
            if result.crisis_detected:
                logger.warning(
                    f"Crisis detected in session {session_context.session_id}: "
                    f"types={result.crisis_types}, escalation={result.escalation_recommended}"
                )

                # Initiate crisis intervention if crisis manager is available
                if self.crisis_intervention_manager:
                    try:
                        # Create session context for crisis assessment
                        crisis_context = {
                            "session_id": session_context.session_id,
                            "user_id": getattr(session_context, "user_id", "unknown"),
                            "session_count": getattr(
                                session_context, "interaction_count", 0
                            ),
                            "previous_violations": getattr(
                                session_context, "safety_violations", 0
                            ),
                            "location": getattr(session_context, "location", "unknown"),
                        }

                        # Assess crisis and initiate intervention
                        assessment = self.crisis_intervention_manager.assess_crisis(
                            result, crisis_context
                        )
                        intervention = (
                            self.crisis_intervention_manager.initiate_intervention(
                                assessment,
                                session_context.session_id,
                                crisis_context["user_id"],
                            )
                        )

                        # Handle escalation if required
                        if (
                            assessment.escalation_required
                            and self.human_oversight_escalation
                        ):
                            if assessment.crisis_level.value == "critical":
                                self.human_oversight_escalation.escalate_to_emergency_services(
                                    intervention, "mental_health"
                                )
                            else:
                                self.human_oversight_escalation.escalate_to_human(
                                    intervention, "crisis_intervention"
                                )

                        # Execute emergency protocol if available
                        if self.emergency_protocol_engine and assessment.crisis_types:
                            for crisis_type in assessment.crisis_types:
                                self.emergency_protocol_engine.execute_protocol(
                                    crisis_type, assessment.crisis_level, crisis_context
                                )

                        # Add alert to monitoring dashboard
                        if self.safety_monitoring_dashboard:
                            self.safety_monitoring_dashboard.add_alert(
                                "crisis_intervention",
                                f"Crisis intervention initiated for session {session_context.session_id}",
                                (
                                    "critical"
                                    if assessment.crisis_level.value == "critical"
                                    else "high"
                                ),
                                {
                                    "intervention_id": intervention.intervention_id,
                                    "crisis_types": [
                                        ct.value for ct in assessment.crisis_types
                                    ],
                                    "crisis_level": assessment.crisis_level.value,
                                },
                            )

                        logger.info(
                            f"Crisis intervention system activated for session {session_context.session_id}"
                        )

                    except Exception as e:
                        logger.error(f"Failed to initiate crisis intervention: {e}")

            if should_alert:
                logger.critical(
                    f"Therapeutic safety alert for session {session_context.session_id}: "
                    f"level={result.level.value}, score={result.score:.2f}"
                )

            return validation_result

        except Exception as e:
            logger.error(f"Enhanced therapeutic validator call failed: {e}")
            return {
                "safe": True,
                "level": "unknown",
                "reason": f"Validation error: {str(e)}",
                "crisis_detected": False,
                "escalation_recommended": False,
            }

    async def _basic_safety_checks(self, user_input: str) -> None:
        """Perform basic safety checks on user input."""
        # Basic keyword-based safety checks
        high_risk_keywords = [
            "suicide",
            "kill myself",
            "end it all",
            "hurt myself",
            "self-harm",
            "cutting",
            "overdose",
        ]

        user_input_lower = user_input.lower()
        for keyword in high_risk_keywords:
            if keyword in user_input_lower:
                logger.warning(f"High-risk keyword detected: {keyword}")
                raise TherapeuticSafetyError(
                    "Content contains potentially harmful language. "
                    "Please contact a mental health professional if you're in crisis."
                )

    async def _determine_workflow_type(
        self, user_input: str, session_context: SessionContext
    ) -> WorkflowType:
        """
        Determine the appropriate workflow type based on user input and context.

        Args:
            user_input: User input to analyze
            session_context: Current session context

        Returns:
            WorkflowType: Determined workflow type
        """
        try:
            # Simple heuristics for workflow type determination
            # In a production system, this could use ML models or more sophisticated analysis

            user_input_lower = user_input.lower().strip()

            # Check for simple commands that only need input processing
            simple_commands = ["help", "status", "quit", "exit", "save"]
            if any(cmd in user_input_lower for cmd in simple_commands):
                return WorkflowType.INPUT_PROCESSING

            # Check for world-building focused inputs
            world_keywords = [
                "look",
                "examine",
                "describe",
                "where am i",
                "surroundings",
            ]
            if any(keyword in user_input_lower for keyword in world_keywords):
                return WorkflowType.WORLD_BUILDING

            # Check for narrative-focused inputs
            narrative_keywords = ["tell me", "story", "what happens", "continue"]
            if any(keyword in user_input_lower for keyword in narrative_keywords):
                return WorkflowType.NARRATIVE_GENERATION

            # Default to collaborative workflow for complex interactions
            return WorkflowType.COLLABORATIVE

        except Exception as e:
            logger.warning(f"Error determining workflow type: {e}")
            # Default to collaborative workflow on error
            return WorkflowType.COLLABORATIVE

    async def _execute_workflow_with_context(
        self,
        workflow_type: WorkflowType,
        request: OrchestrationRequest,
        session_context: SessionContext,
        metadata: dict[str, Any] | None = None,
    ) -> OrchestrationResponse:
        """
        Execute workflow with full context management.

        Args:
            workflow_type: Type of workflow to execute
            request: Orchestration request
            session_context: Session context
            metadata: Optional metadata

        Returns:
            OrchestrationResponse: Workflow execution response
        """
        try:
            # Create agent context from session context
            agent_context = AgentContext(
                user_id=session_context.user_id,
                session_id=session_context.session_id,
                memory=session_context.context.memory,
                world_state=session_context.context.world_state,
                metadata=session_context.context.metadata,
            )

            # Execute workflow
            response, run_id, error = await self.coordinate_agents(
                workflow_type, agent_context, metadata
            )

            if error or not response:
                raise WorkflowExecutionError(f"Workflow execution failed: {error}")

            # Track active workflow
            if run_id:
                self._active_workflows[session_context.session_id] = run_id

            return response

        except Exception as e:
            logger.error(f"Error executing workflow with context: {e}")
            if isinstance(e, WorkflowExecutionError):
                raise
            else:
                raise WorkflowExecutionError(f"Workflow execution failed: {e}") from e

    async def _update_session_context(
        self, session_context: SessionContext, response: OrchestrationResponse
    ) -> None:
        """
        Update session context with workflow response.

        Args:
            session_context: Session context to update
            response: Workflow response containing updates
        """
        try:
            # Update context with response data
            if response.updated_context:
                session_context.context.memory.update(
                    response.updated_context.get("memory", {})
                )
                session_context.context.world_state.update(
                    response.updated_context.get("world_state", {})
                )
                session_context.context.metadata.update(
                    response.updated_context.get("metadata", {})
                )

            # Persist to Neo4j if available
            if self.neo4j_manager:
                await self._persist_session_context(session_context)

            logger.debug(f"Updated session context for {session_context.session_id}")

        except Exception as e:
            logger.error(f"Error updating session context: {e}")
            # Don't raise error for context update failures

    async def _persist_session_context(self, session_context: SessionContext) -> None:
        """Persist session context to Neo4j."""
        try:
            # This would integrate with the Neo4j manager
            # For now, just log the action
            logger.debug(f"Persisting session context for {session_context.session_id}")
        except Exception as e:
            logger.error(f"Error persisting session context: {e}")

    def _get_workflow_name(self, workflow_type: WorkflowType) -> str:
        """Get workflow name for a given workflow type."""
        workflow_names = {
            WorkflowType.COLLABORATIVE: "collaborative",
            WorkflowType.INPUT_PROCESSING: "input_processing",
            WorkflowType.WORLD_BUILDING: "world_building",
            WorkflowType.NARRATIVE_GENERATION: "narrative_generation",
        }
        return workflow_names.get(workflow_type, "collaborative")

    async def _allocate_workflow_resources(
        self, workflow_type: WorkflowType, context: AgentContext
    ) -> None:
        """Allocate resources for workflow execution."""
        try:
            if self.resource_manager:
                # This would integrate with the resource manager
                logger.debug(f"Allocating resources for {workflow_type.value} workflow")
        except Exception as e:
            logger.warning(f"Error allocating workflow resources: {e}")
            # Don't fail workflow execution for resource allocation errors
