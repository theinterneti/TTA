"""

# Logseq: [[TTA.dev/Agent_orchestration/Capability_matcher]]
Capability matching algorithms for agent discovery.

This module provides sophisticated algorithms for matching agent capabilities
against request criteria, supporting various matching strategies and scoring methods.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any

from .models import (
    AgentCapability,
    AgentCapabilitySet,
    CapabilityMatchCriteria,
    CapabilityMatchResult,
)

logger = logging.getLogger(__name__)


class MatchingStrategy(StrEnum):
    """Available capability matching strategies."""

    EXACT_MATCH = "exact_match"  # Exact name and version matching
    WEIGHTED_SCORE = "weighted_score"  # Weighted scoring algorithm
    FUZZY_MATCH = "fuzzy_match"  # Fuzzy string matching
    PRIORITY_BASED = "priority_based"  # Priority-based selection
    SEMANTIC_MATCH = "semantic_match"  # Semantic similarity matching


class CapabilityMatcher:
    """
    Advanced capability matching engine with multiple algorithms.
    """

    def __init__(
        self, default_strategy: MatchingStrategy = MatchingStrategy.WEIGHTED_SCORE
    ):
        self.default_strategy = default_strategy
        self._strategy_weights = {
            "name_match": 0.4,
            "type_match": 0.3,
            "version_match": 0.2,
            "performance_match": 0.1,
        }

    def match_capabilities(
        self,
        capability_sets: list[AgentCapabilitySet],
        criteria: CapabilityMatchCriteria,
        strategy: MatchingStrategy | None = None,
        max_results: int = 10,
    ) -> list[CapabilityMatchResult]:
        """
        Match capabilities against criteria using specified strategy.

        Args:
            capability_sets: List of agent capability sets to search
            criteria: Matching criteria
            strategy: Matching strategy to use (defaults to instance default)
            max_results: Maximum number of results to return

        Returns:
            List of capability match results, sorted by score
        """
        strategy = strategy or self.default_strategy

        try:
            if strategy == MatchingStrategy.EXACT_MATCH:
                matches = self._exact_match(capability_sets, criteria)
            elif strategy == MatchingStrategy.WEIGHTED_SCORE:
                matches = self._weighted_score_match(capability_sets, criteria)
            elif strategy == MatchingStrategy.FUZZY_MATCH:
                matches = self._fuzzy_match(capability_sets, criteria)
            elif strategy == MatchingStrategy.PRIORITY_BASED:
                matches = self._priority_based_match(capability_sets, criteria)
            elif strategy == MatchingStrategy.SEMANTIC_MATCH:
                matches = self._semantic_match(capability_sets, criteria)
            else:
                logger.warning(
                    f"Unknown matching strategy: {strategy}, falling back to weighted_score"
                )
                matches = self._weighted_score_match(capability_sets, criteria)

            # Sort by match score (descending) and limit results
            matches.sort(key=lambda x: x.match_score, reverse=True)
            return matches[:max_results]

        except Exception as e:
            logger.error(f"Capability matching failed: {e}")
            return []

    def _exact_match(
        self,
        capability_sets: list[AgentCapabilitySet],
        criteria: CapabilityMatchCriteria,
    ) -> list[CapabilityMatchResult]:
        """Exact matching strategy - requires perfect matches."""
        matches = []

        for cap_set in capability_sets:
            if not self._check_agent_availability(cap_set, criteria):
                continue

            for capability in cap_set.get_active_capabilities():
                if self._is_exact_match(capability, criteria):
                    match_result = CapabilityMatchResult(
                        agent_id=cap_set.agent_id,
                        capability=capability,
                        match_score=1.0,
                        exact_match=True,
                        version_match=True,
                        performance_match=self._check_performance_match(
                            capability, criteria
                        ),
                        agent_load_factor=cap_set.load_factor,
                        agent_availability=cap_set.availability,
                    )
                    matches.append(match_result)

        return matches

    def _weighted_score_match(
        self,
        capability_sets: list[AgentCapabilitySet],
        criteria: CapabilityMatchCriteria,
    ) -> list[CapabilityMatchResult]:
        """Weighted scoring strategy - calculates scores based on multiple factors."""
        matches = []

        for cap_set in capability_sets:
            if not self._check_agent_availability(cap_set, criteria):
                continue

            for capability in cap_set.get_active_capabilities():
                score_components = self._calculate_score_components(
                    capability, criteria
                )

                if score_components["total_score"] > 0:
                    final_score = self._calculate_weighted_score(score_components)

                    match_result = CapabilityMatchResult(
                        agent_id=cap_set.agent_id,
                        capability=capability,
                        match_score=final_score,
                        exact_match=score_components["exact_match"],
                        version_match=score_components["version_match"],
                        performance_match=score_components["performance_match"],
                        agent_load_factor=cap_set.load_factor,
                        agent_availability=cap_set.availability,
                    )
                    matches.append(match_result)

        return matches

    def _fuzzy_match(
        self,
        capability_sets: list[AgentCapabilitySet],
        criteria: CapabilityMatchCriteria,
    ) -> list[CapabilityMatchResult]:
        """Fuzzy matching strategy - allows partial string matches."""
        matches = []

        for cap_set in capability_sets:
            if not self._check_agent_availability(cap_set, criteria):
                continue

            for capability in cap_set.get_active_capabilities():
                fuzzy_score = self._calculate_fuzzy_score(capability, criteria)

                if fuzzy_score > 0.3:  # Minimum fuzzy threshold
                    match_result = CapabilityMatchResult(
                        agent_id=cap_set.agent_id,
                        capability=capability,
                        match_score=fuzzy_score,
                        exact_match=False,
                        version_match=self._check_version_match(capability, criteria),
                        performance_match=self._check_performance_match(
                            capability, criteria
                        ),
                        agent_load_factor=cap_set.load_factor,
                        agent_availability=cap_set.availability,
                    )
                    matches.append(match_result)

        return matches

    def _priority_based_match(
        self,
        capability_sets: list[AgentCapabilitySet],
        criteria: CapabilityMatchCriteria,
    ) -> list[CapabilityMatchResult]:
        """Priority-based matching - uses agent and capability priorities."""
        matches = []

        for cap_set in capability_sets:
            if not self._check_agent_availability(cap_set, criteria):
                continue

            for capability in cap_set.get_active_capabilities():
                if self._meets_basic_criteria(capability, criteria):
                    # Score based on agent priority and load factor
                    priority_score = (cap_set.priority / 10.0) * (
                        1.0 - cap_set.load_factor
                    )

                    match_result = CapabilityMatchResult(
                        agent_id=cap_set.agent_id,
                        capability=capability,
                        match_score=priority_score,
                        exact_match=self._is_exact_match(capability, criteria),
                        version_match=self._check_version_match(capability, criteria),
                        performance_match=self._check_performance_match(
                            capability, criteria
                        ),
                        agent_load_factor=cap_set.load_factor,
                        agent_availability=cap_set.availability,
                    )
                    matches.append(match_result)

        return matches

    def _semantic_match(
        self,
        capability_sets: list[AgentCapabilitySet],
        criteria: CapabilityMatchCriteria,
    ) -> list[CapabilityMatchResult]:
        """Semantic matching - uses description and tag similarity."""
        matches = []

        for cap_set in capability_sets:
            if not self._check_agent_availability(cap_set, criteria):
                continue

            for capability in cap_set.get_active_capabilities():
                semantic_score = self._calculate_semantic_score(capability, criteria)

                if semantic_score > 0.2:  # Minimum semantic threshold
                    match_result = CapabilityMatchResult(
                        agent_id=cap_set.agent_id,
                        capability=capability,
                        match_score=semantic_score,
                        exact_match=False,
                        version_match=self._check_version_match(capability, criteria),
                        performance_match=self._check_performance_match(
                            capability, criteria
                        ),
                        agent_load_factor=cap_set.load_factor,
                        agent_availability=cap_set.availability,
                    )
                    matches.append(match_result)

        return matches

    # Helper methods for matching logic

    def _check_agent_availability(
        self, cap_set: AgentCapabilitySet, criteria: CapabilityMatchCriteria
    ) -> bool:
        """Check if agent meets availability criteria."""
        if criteria.require_available and not cap_set.availability:
            return False
        return not cap_set.load_factor > criteria.max_load_factor

    def _is_exact_match(
        self, capability: AgentCapability, criteria: CapabilityMatchCriteria
    ) -> bool:
        """Check if capability is an exact match for criteria."""
        if criteria.capability_name and capability.name != criteria.capability_name:
            return False
        if criteria.capability_type and capability.type != criteria.capability_type:
            return False
        if not self._check_version_match(capability, criteria):
            return False
        return not (
            criteria.required_inputs
            and not criteria.required_inputs.issubset(
                capability.required_inputs.union(capability.optional_inputs)
            )
        )

    def _meets_basic_criteria(
        self, capability: AgentCapability, criteria: CapabilityMatchCriteria
    ) -> bool:
        """Check if capability meets basic matching criteria."""
        if criteria.capability_type and capability.type != criteria.capability_type:
            return False
        return not (
            criteria.required_inputs
            and not criteria.required_inputs.issubset(
                capability.required_inputs.union(capability.optional_inputs)
            )
        )

    def _check_version_match(
        self, capability: AgentCapability, criteria: CapabilityMatchCriteria
    ) -> bool:
        """Check if capability version matches criteria."""
        try:
            if criteria.min_version and capability.version < criteria.min_version:
                return False
            return not (
                criteria.max_version and capability.version > criteria.max_version
            )
        except Exception:
            return True  # If version comparison fails, assume compatible

    def _check_performance_match(
        self, capability: AgentCapability, criteria: CapabilityMatchCriteria
    ) -> bool:
        """Check if capability meets performance criteria."""
        if criteria.max_duration_ms and capability.estimated_duration_ms:
            return capability.estimated_duration_ms <= criteria.max_duration_ms
        return True

    def _calculate_score_components(
        self, capability: AgentCapability, criteria: CapabilityMatchCriteria
    ) -> dict[str, Any]:
        """Calculate individual score components for weighted matching."""
        components = {
            "name_score": 0.0,
            "type_score": 0.0,
            "version_score": 0.0,
            "performance_score": 0.0,
            "total_score": 0.0,
            "exact_match": False,
            "version_match": False,
            "performance_match": False,
        }

        # Name matching
        if criteria.capability_name:
            if capability.name == criteria.capability_name:
                components["name_score"] = 1.0
            elif criteria.capability_name.lower() in capability.name.lower():
                components["name_score"] = 0.7
            else:
                return components  # No name match, skip this capability
        else:
            components["name_score"] = 1.0  # No name requirement

        # Type matching
        if criteria.capability_type:
            if capability.type == criteria.capability_type:
                components["type_score"] = 1.0
            else:
                return components  # Type mismatch, skip this capability
        else:
            components["type_score"] = 1.0  # No type requirement

        # Version matching
        components["version_match"] = self._check_version_match(capability, criteria)
        if components["version_match"]:
            if (
                criteria.preferred_version
                and capability.version == criteria.preferred_version
            ):
                components["version_score"] = 1.0
            else:
                components["version_score"] = 0.8
        else:
            return components  # Version mismatch, skip this capability

        # Performance matching
        components["performance_match"] = self._check_performance_match(
            capability, criteria
        )
        if components["performance_match"]:
            components["performance_score"] = 1.0
        else:
            components["performance_score"] = (
                0.5  # Partial score for performance issues
            )

        # Check for exact match
        components["exact_match"] = (
            components["name_score"] == 1.0
            and components["type_score"] == 1.0
            and components["version_score"] == 1.0
            and components["performance_score"] == 1.0
        )

        # At least one component must score
        score_values = [
            components["name_score"],
            components["type_score"],
            components["version_score"],
            components["performance_score"],
        ]
        components["total_score"] = max(score_values)

        return components

    def _calculate_weighted_score(self, components: dict[str, Any]) -> float:
        """Calculate final weighted score from components."""
        weighted_score = (
            components["name_score"] * self._strategy_weights["name_match"]
            + components["type_score"] * self._strategy_weights["type_match"]
            + components["version_score"] * self._strategy_weights["version_match"]
            + components["performance_score"]
            * self._strategy_weights["performance_match"]
        )
        return min(1.0, weighted_score)

    def _calculate_fuzzy_score(
        self, capability: AgentCapability, criteria: CapabilityMatchCriteria
    ) -> float:
        """Calculate fuzzy matching score based on string similarity."""
        if not criteria.capability_name:
            return 0.5  # No name criteria, moderate score

        # Simple fuzzy matching using common subsequences
        name_similarity = self._string_similarity(
            capability.name, criteria.capability_name
        )

        # Boost score if type matches
        type_boost = 0.0
        if criteria.capability_type and capability.type == criteria.capability_type:
            type_boost = 0.3

        return min(1.0, name_similarity + type_boost)

    def _calculate_semantic_score(
        self, capability: AgentCapability, criteria: CapabilityMatchCriteria
    ) -> float:
        """Calculate semantic similarity score."""
        score = 0.0

        # Tag overlap
        if criteria.required_tags and capability.tags:
            tag_overlap = len(criteria.required_tags.intersection(capability.tags))
            tag_score = tag_overlap / len(criteria.required_tags)
            score += tag_score * 0.6

        # Description similarity (simple keyword matching)
        if criteria.capability_name and capability.description:
            desc_similarity = self._keyword_similarity(
                capability.description, criteria.capability_name
            )
            score += desc_similarity * 0.4

        return min(1.0, score)

    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using longest common subsequence."""
        if not str1 or not str2:
            return 0.0

        # Simple similarity based on common characters
        str1_lower = str1.lower()
        str2_lower = str2.lower()

        if str1_lower == str2_lower:
            return 1.0

        # Count common characters
        common_chars = sum(1 for c in str1_lower if c in str2_lower)
        max_len = max(len(str1), len(str2))

        return common_chars / max_len if max_len > 0 else 0.0

    def _keyword_similarity(self, text: str, keyword: str) -> float:
        """Calculate keyword similarity in text."""
        if not text or not keyword:
            return 0.0

        text_lower = text.lower()
        keyword_lower = keyword.lower()

        if keyword_lower in text_lower:
            return 1.0

        # Check for partial matches
        keyword_words = keyword_lower.split()
        matches = sum(1 for word in keyword_words if word in text_lower)

        return matches / len(keyword_words) if keyword_words else 0.0
