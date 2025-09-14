"""
Outcome Measurement System

Evidence-based outcome measurement system providing comprehensive therapeutic
outcome tracking, standardized assessment tools, and clinical-grade metrics
collection for the TTA therapeutic platform.
"""

import logging
import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MeasurementType(Enum):
    """Types of outcome measurements."""

    STANDARDIZED_SCALE = "standardized_scale"
    BEHAVIORAL_METRIC = "behavioral_metric"
    PHYSIOLOGICAL_MARKER = "physiological_marker"
    SELF_REPORT = "self_report"
    CLINICIAN_RATED = "clinician_rated"
    OBJECTIVE_PERFORMANCE = "objective_performance"


class AssessmentTool(Enum):
    """Standardized assessment tools."""

    PHQ9 = "phq9"  # Patient Health Questionnaire-9
    GAD7 = "gad7"  # Generalized Anxiety Disorder-7
    DASS21 = "dass21"  # Depression, Anxiety and Stress Scale-21
    WEMWBS = "wemwbs"  # Warwick-Edinburgh Mental Well-being Scale
    PSS = "pss"  # Perceived Stress Scale
    SWLS = "swls"  # Satisfaction with Life Scale
    CUSTOM_TTA = "custom_tta"  # TTA-specific therapeutic metrics


class ClinicalSignificance(Enum):
    """Clinical significance levels."""

    HIGHLY_SIGNIFICANT = "highly_significant"  # >2 SD improvement
    CLINICALLY_SIGNIFICANT = "clinically_significant"  # 1-2 SD improvement
    MEANINGFUL_CHANGE = "meaningful_change"  # 0.5-1 SD improvement
    MINIMAL_CHANGE = "minimal_change"  # <0.5 SD improvement
    NO_CHANGE = "no_change"  # No significant change
    DETERIORATION = "deterioration"  # Negative change


@dataclass
class OutcomeMeasurement:
    """Individual outcome measurement record."""

    measurement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    measurement_type: MeasurementType = MeasurementType.SELF_REPORT
    assessment_tool: AssessmentTool = AssessmentTool.CUSTOM_TTA
    measurement_name: str = ""
    raw_score: float = 0.0
    standardized_score: float = 0.0
    percentile_rank: float = 0.0
    clinical_significance: ClinicalSignificance = ClinicalSignificance.NO_CHANGE
    baseline_score: float | None = None
    improvement_percentage: float = 0.0
    measurement_context: dict[str, Any] = field(default_factory=dict)
    therapeutic_goals: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    validated: bool = False
    notes: str = ""


@dataclass
class AssessmentBattery:
    """Collection of related outcome measurements."""

    battery_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    battery_name: str = ""
    measurements: list[OutcomeMeasurement] = field(default_factory=list)
    composite_score: float = 0.0
    overall_significance: ClinicalSignificance = ClinicalSignificance.NO_CHANGE
    completion_percentage: float = 0.0
    administration_time: timedelta = field(default_factory=lambda: timedelta(minutes=0))
    timestamp: datetime = field(default_factory=datetime.utcnow)


class OutcomeMeasurementSystem:
    """Evidence-based outcome measurement and tracking system."""

    def __init__(self):
        """Initialize the outcome measurement system."""
        self.measurements: dict[str, OutcomeMeasurement] = {}
        self.assessment_batteries: dict[str, AssessmentBattery] = {}
        self.user_baselines: dict[str, dict[str, float]] = {}
        self.standardized_norms: dict[AssessmentTool, dict[str, float]] = {}
        self.measurement_metrics = {
            "total_measurements": 0,
            "validated_measurements": 0,
            "clinical_significance_rate": 0.0,
            "average_improvement": 0.0,
            "assessment_completion_rate": 0.0,
        }
        self._initialize_standardized_norms()

    def _initialize_standardized_norms(self):
        """Initialize standardized assessment tool norms."""
        # PHQ-9 norms (0-27 scale)
        self.standardized_norms[AssessmentTool.PHQ9] = {
            "minimal": 4.0,
            "mild": 9.0,
            "moderate": 14.0,
            "moderately_severe": 19.0,
            "severe": 27.0,
            "clinical_cutoff": 10.0,
            "reliable_change": 5.0,
        }

        # GAD-7 norms (0-21 scale)
        self.standardized_norms[AssessmentTool.GAD7] = {
            "minimal": 4.0,
            "mild": 9.0,
            "moderate": 14.0,
            "severe": 21.0,
            "clinical_cutoff": 8.0,
            "reliable_change": 4.0,
        }

        # DASS-21 norms (0-63 scale for each subscale)
        self.standardized_norms[AssessmentTool.DASS21] = {
            "depression_mild": 9.0,
            "depression_moderate": 20.0,
            "depression_severe": 27.0,
            "anxiety_mild": 7.0,
            "anxiety_moderate": 14.0,
            "anxiety_severe": 20.0,
            "stress_mild": 14.0,
            "stress_moderate": 25.0,
            "stress_severe": 33.0,
            "reliable_change": 5.0,
        }

    async def initialize(self):
        """Initialize the outcome measurement system."""
        logger.info("OutcomeMeasurementSystem initialization complete")
        logger.info(
            f"Loaded {len(self.standardized_norms)} standardized assessment tools"
        )

    async def create_outcome_measurement(
        self,
        user_id: str,
        session_id: str,
        measurement_type: MeasurementType,
        assessment_tool: AssessmentTool,
        measurement_name: str,
        raw_score: float,
        therapeutic_goals: list[str] | None = None,
        measurement_context: dict[str, Any] | None = None,
    ) -> OutcomeMeasurement:
        """Create a new outcome measurement."""
        try:
            # Get baseline score if available
            baseline_score = await self._get_baseline_score(
                user_id, assessment_tool, measurement_name
            )

            # Calculate standardized score and percentile
            standardized_score = await self._calculate_standardized_score(
                assessment_tool, raw_score
            )
            percentile_rank = await self._calculate_percentile_rank(
                assessment_tool, raw_score
            )

            # Calculate improvement percentage
            improvement_percentage = 0.0
            if baseline_score is not None:
                if baseline_score != 0:
                    improvement_percentage = (
                        (raw_score - baseline_score) / baseline_score
                    ) * 100

            # Assess clinical significance
            clinical_significance = await self._assess_clinical_significance(
                assessment_tool, baseline_score, raw_score
            )

            # Create measurement
            measurement = OutcomeMeasurement(
                user_id=user_id,
                session_id=session_id,
                measurement_type=measurement_type,
                assessment_tool=assessment_tool,
                measurement_name=measurement_name,
                raw_score=raw_score,
                standardized_score=standardized_score,
                percentile_rank=percentile_rank,
                clinical_significance=clinical_significance,
                baseline_score=baseline_score,
                improvement_percentage=improvement_percentage,
                therapeutic_goals=therapeutic_goals or [],
                measurement_context=measurement_context or {},
            )

            # Store measurement
            self.measurements[measurement.measurement_id] = measurement

            # Update metrics
            self.measurement_metrics["total_measurements"] += 1

            logger.info(
                f"Created outcome measurement: {measurement_name} for user {user_id}"
            )

            return measurement

        except Exception as e:
            logger.error(f"Error creating outcome measurement: {e}")
            raise

    async def _get_baseline_score(
        self, user_id: str, assessment_tool: AssessmentTool, measurement_name: str
    ) -> float | None:
        """Get baseline score for a user and measurement."""
        user_key = f"{user_id}_{assessment_tool.value}_{measurement_name}"
        return self.user_baselines.get(user_id, {}).get(user_key)

    async def _calculate_standardized_score(
        self, assessment_tool: AssessmentTool, raw_score: float
    ) -> float:
        """Calculate standardized score based on assessment tool norms."""
        if assessment_tool not in self.standardized_norms:
            return raw_score

        self.standardized_norms[assessment_tool]

        # For PHQ-9 and GAD-7, convert to standardized scale (0-100)
        if assessment_tool in [AssessmentTool.PHQ9, AssessmentTool.GAD7]:
            max_score = 27.0 if assessment_tool == AssessmentTool.PHQ9 else 21.0
            return (raw_score / max_score) * 100

        # For other tools, return raw score (implement specific standardization as needed)
        return raw_score

    async def _calculate_percentile_rank(
        self, assessment_tool: AssessmentTool, raw_score: float
    ) -> float:
        """Calculate percentile rank based on normative data."""
        if assessment_tool not in self.standardized_norms:
            return 50.0  # Default to 50th percentile

        norms = self.standardized_norms[assessment_tool]

        # Simplified percentile calculation based on severity levels
        if assessment_tool == AssessmentTool.PHQ9:
            if raw_score <= norms["minimal"]:
                return 25.0
            elif raw_score <= norms["mild"]:
                return 50.0
            elif raw_score <= norms["moderate"]:
                return 75.0
            else:
                return 90.0

        return 50.0  # Default percentile

    async def _assess_clinical_significance(
        self,
        assessment_tool: AssessmentTool,
        baseline_score: float | None,
        current_score: float,
    ) -> ClinicalSignificance:
        """Assess clinical significance of change."""
        if baseline_score is None:
            return ClinicalSignificance.NO_CHANGE

        change = (
            baseline_score - current_score
        )  # Positive change = improvement for symptom scales

        if assessment_tool not in self.standardized_norms:
            # Use generic thresholds
            if abs(change) < 0.5:
                return ClinicalSignificance.NO_CHANGE
            elif abs(change) < 2.0:
                return ClinicalSignificance.MINIMAL_CHANGE
            elif abs(change) < 5.0:
                return ClinicalSignificance.MEANINGFUL_CHANGE
            else:
                return (
                    ClinicalSignificance.CLINICALLY_SIGNIFICANT
                    if change > 0
                    else ClinicalSignificance.DETERIORATION
                )

        norms = self.standardized_norms[assessment_tool]
        reliable_change = norms.get("reliable_change", 5.0)

        if change < -reliable_change:
            return ClinicalSignificance.DETERIORATION
        elif change < reliable_change * 0.5:
            return ClinicalSignificance.NO_CHANGE
        elif change < reliable_change:
            return ClinicalSignificance.MINIMAL_CHANGE
        elif change < reliable_change * 1.5:
            return ClinicalSignificance.MEANINGFUL_CHANGE
        elif change < reliable_change * 2:
            return ClinicalSignificance.CLINICALLY_SIGNIFICANT
        else:
            return ClinicalSignificance.HIGHLY_SIGNIFICANT

    async def create_assessment_battery(
        self,
        user_id: str,
        session_id: str,
        battery_name: str,
        assessment_tools: list[AssessmentTool],
    ) -> AssessmentBattery:
        """Create a comprehensive assessment battery."""
        try:
            battery = AssessmentBattery(
                user_id=user_id, session_id=session_id, battery_name=battery_name
            )

            # Create placeholder measurements for each tool
            for tool in assessment_tools:
                measurement = OutcomeMeasurement(
                    user_id=user_id,
                    session_id=session_id,
                    measurement_type=MeasurementType.STANDARDIZED_SCALE,
                    assessment_tool=tool,
                    measurement_name=f"{tool.value}_assessment",
                )
                battery.measurements.append(measurement)

            self.assessment_batteries[battery.battery_id] = battery

            logger.info(
                f"Created assessment battery: {battery_name} for user {user_id}"
            )

            return battery

        except Exception as e:
            logger.error(f"Error creating assessment battery: {e}")
            raise

    async def process_outcome_measurement(self, outcome: OutcomeMeasurement) -> bool:
        """Process and validate an outcome measurement."""
        try:
            # Validate measurement data
            if not await self._validate_measurement(outcome):
                logger.warning(
                    f"Measurement validation failed: {outcome.measurement_id}"
                )
                return False

            # Mark as validated
            outcome.validated = True
            self.measurement_metrics["validated_measurements"] += 1

            # Update user baseline if this is the first measurement
            user_key = f"{outcome.user_id}_{outcome.assessment_tool.value}_{outcome.measurement_name}"
            if outcome.user_id not in self.user_baselines:
                self.user_baselines[outcome.user_id] = {}

            if user_key not in self.user_baselines[outcome.user_id]:
                self.user_baselines[outcome.user_id][user_key] = outcome.raw_score

            # Update metrics
            await self._update_metrics()

            logger.info(f"Processed outcome measurement: {outcome.measurement_id}")

            return True

        except Exception as e:
            logger.error(f"Error processing outcome measurement: {e}")
            return False

    async def _validate_measurement(self, measurement: OutcomeMeasurement) -> bool:
        """Validate measurement data quality and consistency."""
        try:
            # Check required fields
            if not all(
                [
                    measurement.user_id,
                    measurement.measurement_name,
                    measurement.assessment_tool,
                ]
            ):
                return False

            # Check score ranges based on assessment tool
            if measurement.assessment_tool in self.standardized_norms:
                self.standardized_norms[measurement.assessment_tool]

                # PHQ-9 range check
                if measurement.assessment_tool == AssessmentTool.PHQ9:
                    if not (0 <= measurement.raw_score <= 27):
                        return False

                # GAD-7 range check
                elif measurement.assessment_tool == AssessmentTool.GAD7:
                    if not (0 <= measurement.raw_score <= 21):
                        return False

            return True

        except Exception as e:
            logger.error(f"Error validating measurement: {e}")
            return False

    async def _update_metrics(self):
        """Update system metrics."""
        try:
            total_measurements = len(self.measurements)
            validated_measurements = sum(
                1 for m in self.measurements.values() if m.validated
            )

            if total_measurements > 0:
                self.measurement_metrics["validated_measurements"] = (
                    validated_measurements
                )
                self.measurement_metrics["clinical_significance_rate"] = (
                    sum(
                        1
                        for m in self.measurements.values()
                        if m.clinical_significance
                        in [
                            ClinicalSignificance.CLINICALLY_SIGNIFICANT,
                            ClinicalSignificance.HIGHLY_SIGNIFICANT,
                        ]
                    )
                    / total_measurements
                )

                # Calculate average improvement
                improvements = [
                    m.improvement_percentage
                    for m in self.measurements.values()
                    if m.baseline_score is not None
                ]
                if improvements:
                    self.measurement_metrics["average_improvement"] = statistics.mean(
                        improvements
                    )

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")

    async def get_user_outcomes(self, user_id: str) -> list[OutcomeMeasurement]:
        """Get all outcome measurements for a user."""
        return [m for m in self.measurements.values() if m.user_id == user_id]

    async def get_clinical_progress_report(self, user_id: str) -> dict[str, Any]:
        """Generate comprehensive clinical progress report for a user."""
        try:
            user_measurements = await self.get_user_outcomes(user_id)

            if not user_measurements:
                return {"user_id": user_id, "status": "no_data"}

            # Group by assessment tool
            by_tool = {}
            for measurement in user_measurements:
                tool = measurement.assessment_tool.value
                if tool not in by_tool:
                    by_tool[tool] = []
                by_tool[tool].append(measurement)

            # Calculate progress for each tool
            progress_summary = {}
            for tool, measurements in by_tool.items():
                sorted_measurements = sorted(measurements, key=lambda x: x.timestamp)
                latest = sorted_measurements[-1]
                baseline = sorted_measurements[0]

                progress_summary[tool] = {
                    "baseline_score": baseline.raw_score,
                    "current_score": latest.raw_score,
                    "improvement_percentage": latest.improvement_percentage,
                    "clinical_significance": latest.clinical_significance.value,
                    "measurement_count": len(measurements),
                    "last_assessment": latest.timestamp.isoformat(),
                }

            # Overall summary
            overall_significance = ClinicalSignificance.NO_CHANGE
            if user_measurements:
                significance_levels = [
                    m.clinical_significance for m in user_measurements
                ]
                if ClinicalSignificance.HIGHLY_SIGNIFICANT in significance_levels:
                    overall_significance = ClinicalSignificance.HIGHLY_SIGNIFICANT
                elif ClinicalSignificance.CLINICALLY_SIGNIFICANT in significance_levels:
                    overall_significance = ClinicalSignificance.CLINICALLY_SIGNIFICANT
                elif ClinicalSignificance.MEANINGFUL_CHANGE in significance_levels:
                    overall_significance = ClinicalSignificance.MEANINGFUL_CHANGE

            return {
                "user_id": user_id,
                "status": "complete",
                "total_measurements": len(user_measurements),
                "assessment_tools_used": list(by_tool.keys()),
                "overall_clinical_significance": overall_significance.value,
                "progress_by_tool": progress_summary,
                "report_generated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating clinical progress report: {e}")
            return {"user_id": user_id, "status": "error", "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            return {
                "status": "healthy",
                "service": "outcome_measurement_system",
                "total_measurements": len(self.measurements),
                "validated_measurements": self.measurement_metrics[
                    "validated_measurements"
                ],
                "assessment_batteries": len(self.assessment_batteries),
                "users_with_baselines": len(self.user_baselines),
                "standardized_tools": len(self.standardized_norms),
                "clinical_significance_rate": self.measurement_metrics[
                    "clinical_significance_rate"
                ],
                "average_improvement": self.measurement_metrics["average_improvement"],
                "metrics": self.measurement_metrics,
            }

        except Exception as e:
            logger.error(f"Error in outcome measurement system health check: {e}")
            return {
                "status": "unhealthy",
                "service": "outcome_measurement_system",
                "error": str(e),
            }
