"""
Tests for Clinical Validation Manager

This module tests the clinical validation framework functionality including
evidence-based outcome measurement, therapeutic effectiveness validation,
and clinical research data collection.
"""

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.components.clinical_validation.clinical_validation_manager import (
    ClinicalOutcome,
    ClinicalResearchData,
    ClinicalValidationManager,
    OutcomeType,
    TherapeuticEffectivenessReport,
    ValidationStatus,
)


class TestClinicalValidationManager:
    """Test Clinical Validation Manager functionality."""

    @pytest_asyncio.fixture
    async def validation_manager(self):
        """Create validation manager instance."""
        manager = ClinicalValidationManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.fixture
    def mock_validation_components(self):
        """Create mock validation components."""
        components = {}

        for component_name in [
            "outcome_measurement_system",
            "therapeutic_effectiveness_validator",
            "clinical_research_data_collector",
            "clinical_compliance_framework",
            "evidence_based_analytics"
        ]:
            mock_component = AsyncMock()
            mock_component.initialize.return_value = None

            if component_name == "outcome_measurement_system":
                mock_component.process_outcome_measurement.return_value = None
            elif component_name == "therapeutic_effectiveness_validator":
                mock_component.validate_effectiveness_report.return_value = None
            elif component_name == "clinical_research_data_collector":
                mock_component.process_research_data.return_value = None
            elif component_name == "clinical_compliance_framework":
                mock_component.validate_compliance.return_value = {
                    "compliance_status": "validated",
                    "compliance_percentage": 100.0
                }
            elif component_name == "evidence_based_analytics":
                mock_component.generate_analytics.return_value = {
                    "analysis_type": "effectiveness",
                    "statistical_significance": 0.95,
                    "recommendations": ["Continue therapy"]
                }

            components[component_name] = mock_component

        return components

    @pytest.fixture
    def mock_integration_systems(self):
        """Create mock integration systems."""
        systems = {}

        # Mock clinical dashboard manager
        clinical_dashboard = AsyncMock()
        clinical_dashboard.health_check.return_value = {"status": "healthy"}
        systems["clinical_dashboard_manager"] = clinical_dashboard

        # Mock cloud deployment manager
        cloud_deployment = AsyncMock()
        cloud_deployment.health_check.return_value = {"status": "healthy"}
        systems["cloud_deployment_manager"] = cloud_deployment

        # Mock therapeutic systems
        for system_name in [
            "consequence_system",
            "emotional_safety_system",
            "adaptive_difficulty_engine"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.mark.asyncio
    async def test_initialization(self, validation_manager):
        """Test validation manager initialization."""
        assert validation_manager.status == ValidationStatus.ACTIVE
        assert len(validation_manager.clinical_outcomes) == 0
        assert len(validation_manager.effectiveness_reports) == 0
        assert len(validation_manager.research_data) == 0

        # Should have background tasks running
        assert validation_manager._validation_monitoring_task is not None
        assert validation_manager._outcome_analysis_task is not None
        assert validation_manager._compliance_check_task is not None

    @pytest.mark.asyncio
    async def test_validation_component_injection(self, validation_manager, mock_validation_components):
        """Test validation component dependency injection."""
        validation_manager.inject_validation_components(**mock_validation_components)

        # Should have all components injected
        assert validation_manager.outcome_measurement_system is not None
        assert validation_manager.therapeutic_effectiveness_validator is not None
        assert validation_manager.clinical_research_data_collector is not None
        assert validation_manager.clinical_compliance_framework is not None
        assert validation_manager.evidence_based_analytics is not None

    @pytest.mark.asyncio
    async def test_integration_systems_injection(self, validation_manager, mock_integration_systems):
        """Test integration systems dependency injection."""
        validation_manager.inject_integration_systems(**mock_integration_systems)

        # Should have integration systems injected
        assert validation_manager.clinical_dashboard_manager is not None
        assert validation_manager.cloud_deployment_manager is not None
        assert len(validation_manager.therapeutic_systems) == 3

    @pytest.mark.asyncio
    async def test_clinical_outcome_measurement(self, validation_manager):
        """Test clinical outcome measurement."""
        outcome = await validation_manager.measure_clinical_outcome(
            user_id="test_user_001",
            session_id="test_session_001",
            outcome_type=OutcomeType.SYMPTOM_REDUCTION,
            measurement_name="anxiety_level",
            current_value=6.0,
            baseline_value=9.0,
            target_value=4.0,
            therapeutic_context={"intervention": "CBT", "session_number": 5}
        )

        # Should create clinical outcome
        assert isinstance(outcome, ClinicalOutcome)
        assert outcome.user_id == "test_user_001"
        assert outcome.session_id == "test_session_001"
        assert outcome.outcome_type == OutcomeType.SYMPTOM_REDUCTION
        assert outcome.measurement_name == "anxiety_level"
        assert outcome.current_value == 6.0
        assert outcome.baseline_value == 9.0
        assert outcome.target_value == 4.0

        # Should calculate improvement percentage
        expected_improvement = ((6.0 - 9.0) / 9.0) * 100  # -33.33% (reduction)
        assert abs(outcome.improvement_percentage - expected_improvement) < 0.01

        # Should assess clinical significance (>20% reduction for symptom reduction)
        assert outcome.clinical_significance is True

        # Should be stored in clinical outcomes
        assert outcome.outcome_id in validation_manager.clinical_outcomes
        assert validation_manager.validation_metrics["outcomes_measured"] == 1

    @pytest.mark.asyncio
    async def test_therapeutic_effectiveness_validation(self, validation_manager):
        """Test therapeutic effectiveness validation."""
        # First, create some clinical outcomes
        outcomes = []
        for i in range(3):
            outcome = await validation_manager.measure_clinical_outcome(
                user_id="test_user_002",
                session_id=f"test_session_{i+1:03d}",
                outcome_type=OutcomeType.EMOTIONAL_REGULATION,
                measurement_name="emotional_stability",
                current_value=7.0 + i,
                baseline_value=5.0,
                therapeutic_context={"session_number": i+1}
            )
            outcomes.append(outcome)

        # Validate therapeutic effectiveness
        report = await validation_manager.validate_therapeutic_effectiveness(
            user_id="test_user_002",
            session_ids=[f"test_session_{i+1:03d}" for i in range(3)],
            evaluation_period_days=30
        )

        # Should create effectiveness report
        assert isinstance(report, TherapeuticEffectivenessReport)
        assert report.user_id == "test_user_002"
        assert len(report.session_ids) == 3
        assert len(report.outcomes_measured) == 3
        assert report.overall_effectiveness_score > 0.0
        assert report.compliance_status == "validated"

        # Should be stored in effectiveness reports
        assert report.report_id in validation_manager.effectiveness_reports
        assert validation_manager.validation_metrics["effectiveness_reports_generated"] == 1

    @pytest.mark.asyncio
    async def test_research_data_collection(self, validation_manager):
        """Test clinical research data collection."""
        research_data = await validation_manager.collect_research_data(
            study_id="clinical_study_001",
            participant_id="participant_123",
            data_type="therapeutic_outcome",
            data_points={
                "anxiety_score": 6.5,
                "depression_score": 4.2,
                "quality_of_life": 7.8,
                "session_engagement": 8.5
            },
            consent_status="obtained"
        )

        # Should create research data record
        assert isinstance(research_data, ClinicalResearchData)
        assert research_data.study_id == "clinical_study_001"
        assert research_data.data_type == "therapeutic_outcome"
        assert research_data.consent_status == "obtained"
        assert research_data.anonymized is True
        assert research_data.data_quality_score > 0.0
        assert len(research_data.data_integrity_hash) > 0

        # Should be stored in research data
        assert research_data.data_id in validation_manager.research_data
        assert validation_manager.validation_metrics["research_data_points_collected"] == 1

    @pytest.mark.asyncio
    async def test_clinical_compliance_validation(self, validation_manager, mock_validation_components):
        """Test clinical compliance validation."""
        validation_manager.inject_validation_components(**mock_validation_components)

        compliance_result = await validation_manager.validate_clinical_compliance(
            validation_type="HIPAA_compliance",
            compliance_criteria={
                "data_encryption": True,
                "access_controls": True,
                "audit_logging": True,
                "patient_consent": True
            }
        )

        # Should return compliance validation result
        assert compliance_result["compliance_status"] == "validated"
        assert compliance_result["compliance_percentage"] == 100.0
        assert validation_manager.validation_metrics["compliance_validations"] == 1

    @pytest.mark.asyncio
    async def test_evidence_based_analytics_generation(self, validation_manager, mock_validation_components):
        """Test evidence-based analytics generation."""
        validation_manager.inject_validation_components(**mock_validation_components)

        analytics_result = await validation_manager.generate_evidence_based_analytics(
            analysis_type="therapeutic_effectiveness",
            data_scope={
                "user_cohort": "anxiety_treatment",
                "time_period": "30_days",
                "outcome_types": ["symptom_reduction", "quality_of_life"]
            }
        )

        # Should return analytics result
        assert analytics_result["analysis_type"] == "effectiveness"
        assert analytics_result["statistical_significance"] == 0.95
        assert len(analytics_result["recommendations"]) > 0
        assert validation_manager.validation_metrics["evidence_based_recommendations"] > 0

    @pytest.mark.asyncio
    async def test_clinical_validation_overview(self, validation_manager, mock_validation_components, mock_integration_systems):
        """Test clinical validation overview generation."""
        # Inject dependencies
        validation_manager.inject_validation_components(**mock_validation_components)
        validation_manager.inject_integration_systems(**mock_integration_systems)

        # Create some test data
        await validation_manager.measure_clinical_outcome(
            user_id="overview_user",
            session_id="overview_session",
            outcome_type=OutcomeType.QUALITY_OF_LIFE,
            measurement_name="life_satisfaction",
            current_value=8.0,
            baseline_value=6.0
        )

        overview = await validation_manager.get_clinical_validation_overview()

        # Should return comprehensive overview
        assert overview["validation_status"] == ValidationStatus.ACTIVE.value
        assert "summary" in overview
        assert "performance_metrics" in overview
        assert "recent_outcomes" in overview
        assert "recent_reports" in overview
        assert "system_health" in overview

        # Should have correct counts
        assert overview["summary"]["outcomes_measured"] == 1
        assert overview["system_health"]["validation_components_available"] == 5
        assert overview["system_health"]["integration_systems_available"] == 5  # 2 + 3 therapeutic systems

    @pytest.mark.asyncio
    async def test_clinical_significance_assessment(self, validation_manager):
        """Test clinical significance assessment for different outcome types."""
        # Test symptom reduction (significant reduction)
        outcome1 = await validation_manager.measure_clinical_outcome(
            user_id="significance_test_1",
            session_id="session_001",
            outcome_type=OutcomeType.SYMPTOM_REDUCTION,
            measurement_name="depression_score",
            current_value=6.0,
            baseline_value=10.0  # 40% reduction - should be significant
        )
        assert outcome1.clinical_significance is True

        # Test behavioral change (significant improvement)
        outcome2 = await validation_manager.measure_clinical_outcome(
            user_id="significance_test_2",
            session_id="session_002",
            outcome_type=OutcomeType.BEHAVIORAL_CHANGE,
            measurement_name="social_interaction",
            current_value=8.0,
            baseline_value=6.0  # 33% improvement - should be significant
        )
        assert outcome2.clinical_significance is True

        # Test minimal change (not significant)
        outcome3 = await validation_manager.measure_clinical_outcome(
            user_id="significance_test_3",
            session_id="session_003",
            outcome_type=OutcomeType.COGNITIVE_IMPROVEMENT,
            measurement_name="memory_score",
            current_value=7.5,
            baseline_value=7.0  # 7% improvement - should not be significant
        )
        assert outcome3.clinical_significance is False

    @pytest.mark.asyncio
    async def test_effectiveness_score_calculation(self, validation_manager):
        """Test therapeutic effectiveness score calculation."""
        # Create outcomes with varying levels of improvement and significance
        outcomes = []

        # High improvement, clinically significant
        outcome1 = await validation_manager.measure_clinical_outcome(
            user_id="effectiveness_test",
            session_id="session_001",
            outcome_type=OutcomeType.SYMPTOM_REDUCTION,
            measurement_name="anxiety",
            current_value=4.0,
            baseline_value=8.0  # 50% reduction
        )
        outcomes.append(outcome1)

        # Moderate improvement, clinically significant
        outcome2 = await validation_manager.measure_clinical_outcome(
            user_id="effectiveness_test",
            session_id="session_002",
            outcome_type=OutcomeType.QUALITY_OF_LIFE,
            measurement_name="life_satisfaction",
            current_value=8.0,
            baseline_value=6.0  # 33% improvement
        )
        outcomes.append(outcome2)

        # Generate effectiveness report
        report = await validation_manager.validate_therapeutic_effectiveness(
            user_id="effectiveness_test",
            session_ids=["session_001", "session_002"],
            evaluation_period_days=30
        )

        # Should have reasonable effectiveness score
        assert 0.0 <= report.overall_effectiveness_score <= 1.0
        assert report.overall_effectiveness_score > 0.5  # Should be good given significant improvements

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, validation_manager):
        """Test performance benchmarks for clinical validation."""
        import time

        # Test outcome measurement performance
        start_time = time.perf_counter()

        await validation_manager.measure_clinical_outcome(
            user_id="perf_test",
            session_id="perf_session",
            outcome_type=OutcomeType.THERAPEUTIC_ENGAGEMENT,
            measurement_name="engagement_score",
            current_value=8.5,
            baseline_value=7.0
        )

        measurement_time = (time.perf_counter() - start_time) * 1000
        assert measurement_time < 100.0  # Should be under 100ms

        # Test effectiveness validation performance
        start_time = time.perf_counter()

        await validation_manager.validate_therapeutic_effectiveness(
            user_id="perf_test",
            session_ids=["perf_session"],
            evaluation_period_days=30
        )

        validation_time = (time.perf_counter() - start_time) * 1000
        assert validation_time < 500.0  # Should be under 500ms

        # Test overview generation performance
        start_time = time.perf_counter()

        await validation_manager.get_clinical_validation_overview()

        overview_time = (time.perf_counter() - start_time) * 1000
        assert overview_time < 200.0  # Should be under 200ms

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, validation_manager, mock_validation_components, mock_integration_systems):
        """Test compatibility with E2E test interface expectations."""
        # Inject all dependencies
        validation_manager.inject_validation_components(**mock_validation_components)
        validation_manager.inject_integration_systems(**mock_integration_systems)

        # Test complete clinical validation workflow
        outcome = await validation_manager.measure_clinical_outcome(
            user_id="e2e_test_user",
            session_id="e2e_test_session",
            outcome_type=OutcomeType.SYMPTOM_REDUCTION,
            measurement_name="e2e_test_measure",
            current_value=5.0,
            baseline_value=8.0
        )

        # Should match expected structure
        assert hasattr(outcome, "outcome_id")
        assert hasattr(outcome, "user_id")
        assert hasattr(outcome, "outcome_type")
        assert hasattr(outcome, "clinical_significance")
        assert hasattr(outcome, "improvement_percentage")

        # Test effectiveness validation
        report = await validation_manager.validate_therapeutic_effectiveness(
            user_id="e2e_test_user",
            session_ids=["e2e_test_session"],
            evaluation_period_days=30
        )

        # Should match expected structure
        assert hasattr(report, "report_id")
        assert hasattr(report, "overall_effectiveness_score")
        assert hasattr(report, "evidence_based_rating")
        assert hasattr(report, "clinical_recommendations")

        # Test overview generation
        overview = await validation_manager.get_clinical_validation_overview()

        # Should match expected structure
        assert "validation_status" in overview
        assert "summary" in overview
        assert "performance_metrics" in overview
        assert "system_health" in overview
