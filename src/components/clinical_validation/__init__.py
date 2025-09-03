"""
Clinical Validation Framework Module

This module provides evidence-based outcome measurement, therapeutic effectiveness
validation, and clinical research data collection framework for the TTA platform,
ensuring clinical compliance and research-grade data analysis capabilities.

Components:
- ClinicalValidationManager: Core clinical validation management and orchestration
- OutcomeMeasurementSystem: Evidence-based outcome measurement and tracking
- TherapeuticEffectivenessValidator: Therapeutic effectiveness validation and analysis
- ClinicalResearchDataCollector: Research-grade data collection and management
- ClinicalComplianceFramework: Healthcare regulation compliance validation
- EvidenceBasedAnalytics: Evidence-based therapeutic outcome analytics
"""

from .clinical_compliance_framework import ClinicalComplianceFramework
from .clinical_research_data_collector import ClinicalResearchDataCollector
from .clinical_validation_manager import ClinicalValidationManager
from .evidence_based_analytics import EvidenceBasedAnalytics
from .outcome_measurement_system import OutcomeMeasurementSystem
from .therapeutic_effectiveness_validator import TherapeuticEffectivenessValidator

__all__ = [
    "ClinicalValidationManager",
    "OutcomeMeasurementSystem",
    "TherapeuticEffectivenessValidator",
    "ClinicalResearchDataCollector",
    "ClinicalComplianceFramework",
    "EvidenceBasedAnalytics",
]
