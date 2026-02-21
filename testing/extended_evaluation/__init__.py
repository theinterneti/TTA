"""

# Logseq: [[TTA.dev/Testing/Extended_evaluation/__init__]]
TTA Extended Quality Evaluation Framework

This package provides comprehensive testing infrastructure for evaluating
the TTA storytelling system through extended sessions (20-50+ turns) with
focus on living worlds consistency, narrative coherence, and user engagement.
"""

from .analysis_reporting import QualityAnalysisReporter
from .data_collection import ComprehensiveDataCollector
from .extended_session_framework import ExtendedSessionTestFramework
from .living_worlds_metrics import LivingWorldsEvaluator, WorldStateMetrics
from .narrative_analysis import CoherenceMetrics, NarrativeAnalyzer
from .simulated_user_profiles import SimulatedUserProfile, UserBehaviorPattern

__all__ = [
    "ExtendedSessionTestFramework",
    "SimulatedUserProfile",
    "UserBehaviorPattern",
    "LivingWorldsEvaluator",
    "WorldStateMetrics",
    "NarrativeAnalyzer",
    "CoherenceMetrics",
    "ComprehensiveDataCollector",
    "QualityAnalysisReporter",
]

__version__ = "1.0.0"
