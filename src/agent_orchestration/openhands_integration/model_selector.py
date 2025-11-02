"""
Model selector for intelligent model selection based on task requirements.

Provides:
- ModelSelector: Selects optimal model for task
- TaskRequirements: Task-specific requirements
- ModelCapability: Model capability tracking
- Cost/performance optimization
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TaskCategory(str, Enum):
    """Task categories for model selection."""

    UNIT_TEST = "unit_test"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    BUILD_SCRIPT = "build_script"


class ModelSpecialization(str, Enum):
    """Model specialization types."""

    SPEED = "speed"  # Fastest execution
    QUALITY = "quality"  # Highest quality output
    BALANCED = "balanced"  # Good balance
    REASONING = "reasoning"  # Complex reasoning


@dataclass
class TaskRequirements:
    """Task-specific requirements for model selection."""

    category: TaskCategory
    complexity: str  # "simple", "moderate", "complex"
    quality_threshold: float = 0.7  # 0-1 scale
    max_latency_ms: int = 5000
    max_tokens: int = 4000
    specialization: Optional[ModelSpecialization] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.metadata:
            self.metadata = {}


@dataclass
class ModelCapability:
    """Model capability and performance metrics."""

    model_id: str
    name: str
    specialization: ModelSpecialization
    avg_latency_ms: float
    quality_score: float  # 0-5 scale
    success_rate: float  # 0-1 scale
    cost_per_1k_tokens: float
    max_tokens: int
    supported_categories: list[TaskCategory]
    is_available: bool = True
    last_used: Optional[float] = None
    failure_count: int = 0


class ModelSelector:
    """Intelligent model selection based on task requirements."""

    # Model registry with capabilities
    MODELS: dict[str, ModelCapability] = {
        "mistral-small": ModelCapability(
            model_id="mistral-small",
            name="Mistral Small",
            specialization=ModelSpecialization.SPEED,
            avg_latency_ms=880,
            quality_score=4.2,
            success_rate=0.95,
            cost_per_1k_tokens=0.14,
            max_tokens=32000,
            supported_categories=[
                TaskCategory.DOCUMENTATION,
                TaskCategory.CODE_GENERATION,
                TaskCategory.UNIT_TEST,
            ],
        ),
        "llama-3.3": ModelCapability(
            model_id="llama-3.3",
            name="Llama 3.3",
            specialization=ModelSpecialization.BALANCED,
            avg_latency_ms=1200,
            quality_score=4.5,
            success_rate=0.92,
            cost_per_1k_tokens=0.18,
            max_tokens=8000,
            supported_categories=[
                TaskCategory.UNIT_TEST,
                TaskCategory.REFACTORING,
                TaskCategory.CODE_GENERATION,
            ],
        ),
        "deepseek-chat": ModelCapability(
            model_id="deepseek-chat",
            name="DeepSeek Chat",
            specialization=ModelSpecialization.QUALITY,
            avg_latency_ms=1500,
            quality_score=4.7,
            success_rate=0.90,
            cost_per_1k_tokens=0.14,
            max_tokens=4000,
            supported_categories=[
                TaskCategory.REFACTORING,
                TaskCategory.ANALYSIS,
                TaskCategory.UNIT_TEST,
            ],
        ),
        "gemini-flash": ModelCapability(
            model_id="gemini-flash",
            name="Gemini Flash",
            specialization=ModelSpecialization.SPEED,
            avg_latency_ms=950,
            quality_score=4.3,
            success_rate=0.93,
            cost_per_1k_tokens=0.075,
            max_tokens=4000,
            supported_categories=[
                TaskCategory.DOCUMENTATION,
                TaskCategory.CODE_GENERATION,
            ],
        ),
    }

    def __init__(self):
        """Initialize model selector."""
        self.models = self.MODELS.copy()

    def select_model(self, requirements: TaskRequirements) -> Optional[ModelCapability]:
        """Select optimal model for task.

        Args:
            requirements: Task requirements

        Returns:
            Selected model or None if no suitable model found
        """
        candidates = self._filter_candidates(requirements)

        if not candidates:
            logger.warning(f"No suitable model found for {requirements.category}")
            return None

        # Score candidates
        scored = [
            (model, self._score_model(model, requirements)) for model in candidates
        ]

        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)

        selected = scored[0][0]
        logger.info(
            f"Selected {selected.name} for {requirements.category} "
            f"(score: {scored[0][1]:.2f})"
        )
        return selected

    def _filter_candidates(self, requirements: TaskRequirements) -> list[ModelCapability]:
        """Filter models by requirements.

        Args:
            requirements: Task requirements

        Returns:
            List of candidate models
        """
        candidates = []

        for model in self.models.values():
            # Check availability
            if not model.is_available:
                continue

            # Check category support
            if requirements.category not in model.supported_categories:
                continue

            # Check latency requirement
            if model.avg_latency_ms > requirements.max_latency_ms:
                continue

            # Check token limit
            if model.max_tokens < requirements.max_tokens:
                continue

            # Check quality threshold
            if model.quality_score / 5.0 < requirements.quality_threshold:
                continue

            candidates.append(model)

        return candidates

    def _score_model(
        self, model: ModelCapability, requirements: TaskRequirements
    ) -> float:
        """Score model for task.

        Args:
            model: Model to score
            requirements: Task requirements

        Returns:
            Score (0-100)
        """
        score = 0.0

        # Quality score (40%)
        quality_normalized = model.quality_score / 5.0
        score += quality_normalized * 40

        # Success rate (30%)
        score += model.success_rate * 30

        # Latency score (20%) - prefer faster models
        latency_score = max(0, 1 - (model.avg_latency_ms / requirements.max_latency_ms))
        score += latency_score * 20

        # Specialization match (10%)
        if requirements.specialization == model.specialization:
            score += 10

        return score

    def mark_failure(self, model_id: str) -> None:
        """Mark model as having a failure.

        Args:
            model_id: Model ID
        """
        if model_id in self.models:
            self.models[model_id].failure_count += 1
            if self.models[model_id].failure_count > 5:
                self.models[model_id].is_available = False
                logger.warning(f"Model {model_id} marked unavailable after 5 failures")

    def mark_success(self, model_id: str) -> None:
        """Mark model as having a success.

        Args:
            model_id: Model ID
        """
        if model_id in self.models:
            self.models[model_id].failure_count = max(0, self.models[model_id].failure_count - 1)

