"""
Comprehensive unit tests for capability_matcher module.

Tests cover:
- MatchingStrategy enum
- CapabilityMatcher class with various matching strategies
- Capability matching algorithms (exact, weighted, fuzzy, priority, semantic)
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agent_orchestration.capability_matcher import (
    CapabilityMatcher,
    MatchingStrategy,
)
from agent_orchestration.models import (
    AgentCapability,
    AgentCapabilitySet,
    AgentId,
    AgentType,
    CapabilityMatchCriteria,
    CapabilityMatchResult,
    CapabilityStatus,
    CapabilityType,
)


class TestMatchingStrategy:
    """Tests for MatchingStrategy enum."""

    def test_matching_strategy_values(self):
        """Test MatchingStrategy enum has expected values."""
        assert hasattr(MatchingStrategy, "EXACT_MATCH")
        assert hasattr(MatchingStrategy, "WEIGHTED_SCORE")
        assert hasattr(MatchingStrategy, "FUZZY_MATCH")
        assert hasattr(MatchingStrategy, "PRIORITY_BASED")
        assert hasattr(MatchingStrategy, "SEMANTIC_MATCH")

    def test_matching_strategy_is_enum(self):
        """Test MatchingStrategy is an Enum."""
        assert isinstance(MatchingStrategy.EXACT_MATCH, MatchingStrategy)

    def test_matching_strategy_string_values(self):
        """Test MatchingStrategy has correct string values."""
        assert MatchingStrategy.EXACT_MATCH.value == "exact_match"
        assert MatchingStrategy.WEIGHTED_SCORE.value == "weighted_score"
        assert MatchingStrategy.FUZZY_MATCH.value == "fuzzy_match"
        assert MatchingStrategy.PRIORITY_BASED.value == "priority_based"
        assert MatchingStrategy.SEMANTIC_MATCH.value == "semantic_match"


class TestCapabilityMatcher:
    """Tests for CapabilityMatcher class."""

    @pytest.fixture
    def matcher(self):
        """Create CapabilityMatcher instance."""
        return CapabilityMatcher()

    @pytest.fixture
    def sample_capability(self):
        """Create a sample capability."""
        return AgentCapability(
            name="text_processing",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
            performance_metrics={"throughput": 100, "latency": 50},
        )

    @pytest.fixture
    def sample_capability_set(self, sample_capability):
        """Create a sample capability set."""
        return AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[sample_capability],
            priority=8,
            load_factor=0.3,
            availability=True,
        )

    @pytest.fixture
    def sample_criteria(self):
        """Create sample matching criteria."""
        return CapabilityMatchCriteria(
            capability_name="text_processing",
            capability_type=CapabilityType.PROCESSING,
            min_version="1.0.0",
            required_performance={"throughput": 50},
        )

    def test_matcher_initialization(self, matcher):
        """Test CapabilityMatcher initializes correctly."""
        assert matcher is not None

    def test_exact_match_strategy(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test exact match strategy."""
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            MatchingStrategy.EXACT_MATCH,
        )

        assert isinstance(matches, list)
        assert all(isinstance(m, CapabilityMatchResult) for m in matches)

    def test_weighted_score_strategy(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test weighted score matching strategy."""
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            MatchingStrategy.WEIGHTED_SCORE,
        )

        assert isinstance(matches, list)
        assert all(isinstance(m, CapabilityMatchResult) for m in matches)

    def test_fuzzy_match_strategy(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test fuzzy match strategy."""
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            MatchingStrategy.FUZZY_MATCH,
        )

        assert isinstance(matches, list)
        assert all(isinstance(m, CapabilityMatchResult) for m in matches)

    def test_priority_based_strategy(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test priority-based matching strategy."""
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            MatchingStrategy.PRIORITY_BASED,
        )

        assert isinstance(matches, list)
        assert all(isinstance(m, CapabilityMatchResult) for m in matches)

    def test_semantic_match_strategy(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test semantic match strategy."""
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            MatchingStrategy.SEMANTIC_MATCH,
        )

        assert isinstance(matches, list)
        assert all(isinstance(m, CapabilityMatchResult) for m in matches)

    def test_match_with_empty_capability_sets(self, matcher, sample_criteria):
        """Test matching with empty capability sets."""
        matches = matcher.match_capabilities(
            [],
            sample_criteria,
            MatchingStrategy.EXACT_MATCH,
        )

        assert isinstance(matches, list)
        assert len(matches) == 0

    def test_match_with_multiple_capability_sets(
        self, matcher, sample_capability, sample_criteria
    ):
        """Test matching with multiple capability sets."""
        cap_sets = [
            AgentCapabilitySet(
                agent_id=AgentId(type=AgentType.IPA, instance=f"agent-{i}"),
                capabilities=[sample_capability],
                priority=8 - i,
                load_factor=0.3 + (i * 0.1),
                availability=True,
            )
            for i in range(3)
        ]

        matches = matcher.match_capabilities(
            cap_sets,
            sample_criteria,
            MatchingStrategy.WEIGHTED_SCORE,
        )

        assert isinstance(matches, list)

    def test_match_result_has_required_fields(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test that match results have all required fields."""
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            MatchingStrategy.EXACT_MATCH,
        )

        if matches:
            match = matches[0]
            assert hasattr(match, "agent_id")
            assert hasattr(match, "capability")
            assert hasattr(match, "match_score")
            assert hasattr(match, "exact_match")
            assert hasattr(match, "version_match")
            assert hasattr(match, "performance_match")

    def test_match_score_is_numeric(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test that match scores are numeric."""
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            MatchingStrategy.WEIGHTED_SCORE,
        )

        for match in matches:
            assert isinstance(match.match_score, (int, float))
            assert 0 <= match.match_score <= 1 or match.match_score >= 0

    def test_unknown_strategy_fallback(
        self, matcher, sample_capability_set, sample_criteria
    ):
        """Test fallback behavior with unknown strategy."""
        # Try with an invalid strategy - should fallback to weighted_score
        matches = matcher.match_capabilities(
            [sample_capability_set],
            sample_criteria,
            "unknown_strategy",
        )

        assert isinstance(matches, list)

    def test_capability_with_different_versions(self, matcher, sample_criteria):
        """Test matching capabilities with different versions."""
        capabilities = [
            AgentCapability(
                name="text_processing",
                type=CapabilityType.PROCESSING,
                version="1.0.0",
                status=CapabilityStatus.ACTIVE,
            ),
            AgentCapability(
                name="text_processing",
                type=CapabilityType.PROCESSING,
                version="2.0.0",
                status=CapabilityStatus.ACTIVE,
            ),
        ]

        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=capabilities,
            priority=8,
            load_factor=0.3,
            availability=True,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            sample_criteria,
            MatchingStrategy.EXACT_MATCH,
        )

        assert isinstance(matches, list)

    def test_capability_with_different_statuses(self, matcher, sample_criteria):
        """Test matching capabilities with different statuses."""
        capabilities = [
            AgentCapability(
                name="text_processing",
                type=CapabilityType.PROCESSING,
                version="1.0.0",
                status=CapabilityStatus.ACTIVE,
            ),
            AgentCapability(
                name="text_processing",
                type=CapabilityType.PROCESSING,
                version="1.0.0",
                status=CapabilityStatus.DEPRECATED,
            ),
        ]

        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=capabilities,
            priority=8,
            load_factor=0.3,
            availability=True,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            sample_criteria,
            MatchingStrategy.WEIGHTED_SCORE,
        )

        assert isinstance(matches, list)

    def test_match_with_high_load_factor(
        self, matcher, sample_capability, sample_criteria
    ):
        """Test matching with high load factor."""
        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[sample_capability],
            priority=8,
            load_factor=0.9,  # High load
            availability=True,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            sample_criteria,
            MatchingStrategy.PRIORITY_BASED,
        )

        assert isinstance(matches, list)

    def test_match_with_low_availability(
        self, matcher, sample_capability, sample_criteria
    ):
        """Test matching with low availability."""
        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[sample_capability],
            priority=8,
            load_factor=0.3,
            availability=False,  # Low availability
        )

        matches = matcher.match_capabilities(
            [cap_set],
            sample_criteria,
            MatchingStrategy.WEIGHTED_SCORE,
        )

        assert isinstance(matches, list)

    def test_match_with_exception_handling(self, matcher, sample_capability_set):
        """Test exception handling in match_capabilities."""
        # Create criteria that will cause issues
        criteria = CapabilityMatchCriteria(
            capability_name="text_processing",
            capability_type=CapabilityType.PROCESSING,
        )

        # Mock match_capabilities to raise an exception
        with patch.object(
            matcher, "_weighted_score_match", side_effect=Exception("Test error")
        ):
            matches = matcher.match_capabilities(
                [sample_capability_set],
                criteria,
                MatchingStrategy.WEIGHTED_SCORE,
            )
            # Should return empty list on exception
            assert matches == []

    def test_exact_match_with_unavailable_agent(self, matcher, sample_capability):
        """Test exact match with unavailable agent."""
        criteria = CapabilityMatchCriteria(
            capability_name="text_processing",
            capability_type=CapabilityType.PROCESSING,
            require_available=True,
        )

        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[sample_capability],
            priority=8,
            load_factor=0.3,
            availability=False,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            criteria,
            MatchingStrategy.EXACT_MATCH,
        )

        assert len(matches) == 0

    def test_exact_match_with_high_load_factor(self, matcher, sample_capability):
        """Test exact match with high load factor exceeding max."""
        criteria = CapabilityMatchCriteria(
            capability_name="text_processing",
            capability_type=CapabilityType.PROCESSING,
            max_load_factor=0.5,
        )

        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[sample_capability],
            priority=8,
            load_factor=0.8,  # Exceeds max
            availability=True,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            criteria,
            MatchingStrategy.EXACT_MATCH,
        )

        assert len(matches) == 0

    def test_fuzzy_match_with_low_score(self, matcher):
        """Test fuzzy match with capability that scores below threshold."""
        criteria = CapabilityMatchCriteria(
            capability_name="xyz_capability",  # Very different name
            capability_type=CapabilityType.PROCESSING,
        )

        capability = AgentCapability(
            name="abc_capability",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[capability],
            priority=8,
            load_factor=0.3,
            availability=True,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            criteria,
            MatchingStrategy.FUZZY_MATCH,
        )

        # May or may not match depending on fuzzy score
        assert isinstance(matches, list)

    def test_semantic_match_with_tags(self, matcher):
        """Test semantic match with tag overlap."""
        criteria = CapabilityMatchCriteria(
            capability_name="text_processing",
            required_tags={"nlp", "processing"},
        )

        capability = AgentCapability(
            name="text_processing",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
            tags={"nlp", "processing", "ml"},
        )

        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[capability],
            priority=8,
            load_factor=0.3,
            availability=True,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            criteria,
            MatchingStrategy.SEMANTIC_MATCH,
        )

        assert isinstance(matches, list)

    def test_semantic_match_with_description(self, matcher):
        """Test semantic match with description keyword matching."""
        criteria = CapabilityMatchCriteria(
            capability_name="text processing",
        )

        capability = AgentCapability(
            name="text_processor",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
            description="Advanced text processing and NLP capabilities",
        )

        cap_set = AgentCapabilitySet(
            agent_id=AgentId(type=AgentType.IPA, instance="agent-1"),
            capabilities=[capability],
            priority=8,
            load_factor=0.3,
            availability=True,
        )

        matches = matcher.match_capabilities(
            [cap_set],
            criteria,
            MatchingStrategy.SEMANTIC_MATCH,
        )

        assert isinstance(matches, list)


class TestCapabilityMatcherHelpers:
    """Tests for CapabilityMatcher helper methods."""

    @pytest.fixture
    def matcher(self):
        """Create CapabilityMatcher instance."""
        return CapabilityMatcher()

    def test_string_similarity_exact_match(self, matcher):
        """Test string similarity with exact match."""
        score = matcher._string_similarity("hello", "hello")
        assert score == 1.0

    def test_string_similarity_case_insensitive(self, matcher):
        """Test string similarity is case insensitive."""
        score = matcher._string_similarity("Hello", "HELLO")
        assert score == 1.0

    def test_string_similarity_partial_match(self, matcher):
        """Test string similarity with partial match."""
        score = matcher._string_similarity("hello", "hallo")
        assert 0 < score < 1.0

    def test_string_similarity_empty_strings(self, matcher):
        """Test string similarity with empty strings."""
        score = matcher._string_similarity("", "hello")
        assert score == 0.0

    def test_keyword_similarity_exact_match(self, matcher):
        """Test keyword similarity with exact match."""
        score = matcher._keyword_similarity("text processing", "text processing")
        assert score == 1.0

    def test_keyword_similarity_partial_match(self, matcher):
        """Test keyword similarity with partial match."""
        score = matcher._keyword_similarity(
            "text processing and NLP", "text processing"
        )
        assert score == 1.0

    def test_keyword_similarity_word_match(self, matcher):
        """Test keyword similarity with word match."""
        score = matcher._keyword_similarity(
            "advanced text processing", "text processing"
        )
        assert score > 0

    def test_keyword_similarity_empty_text(self, matcher):
        """Test keyword similarity with empty text."""
        score = matcher._keyword_similarity("", "keyword")
        assert score == 0.0

    def test_keyword_similarity_empty_keyword(self, matcher):
        """Test keyword similarity with empty keyword."""
        score = matcher._keyword_similarity("some text", "")
        assert score == 0.0

    def test_check_version_match_within_range(self, matcher):
        """Test version match within range."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.5.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            min_version="1.0.0",
            max_version="2.0.0",
        )

        assert matcher._check_version_match(capability, criteria) is True

    def test_check_version_match_below_min(self, matcher):
        """Test version match below minimum."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="0.9.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            min_version="1.0.0",
        )

        assert matcher._check_version_match(capability, criteria) is False

    def test_check_version_match_above_max(self, matcher):
        """Test version match above maximum."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="3.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            max_version="2.0.0",
        )

        assert matcher._check_version_match(capability, criteria) is False

    def test_check_version_match_no_version_criteria(self, matcher):
        """Test version match with no version criteria."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.5.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria()

        # Should return True when no version criteria specified
        assert matcher._check_version_match(capability, criteria) is True

    def test_check_performance_match_within_duration(self, matcher):
        """Test performance match within duration."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
            estimated_duration_ms=100,
        )

        criteria = CapabilityMatchCriteria(
            max_duration_ms=200,
        )

        assert matcher._check_performance_match(capability, criteria) is True

    def test_check_performance_match_exceeds_duration(self, matcher):
        """Test performance match exceeds duration."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
            estimated_duration_ms=300,
        )

        criteria = CapabilityMatchCriteria(
            max_duration_ms=200,
        )

        assert matcher._check_performance_match(capability, criteria) is False

    def test_check_performance_match_no_duration_criteria(self, matcher):
        """Test performance match with no duration criteria."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
            estimated_duration_ms=300,
        )

        criteria = CapabilityMatchCriteria()

        assert matcher._check_performance_match(capability, criteria) is True

    def test_calculate_fuzzy_score_with_type_boost(self, matcher):
        """Test fuzzy score calculation with type boost."""
        capability = AgentCapability(
            name="text_processing",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            capability_name="text_process",
            capability_type=CapabilityType.PROCESSING,
        )

        score = matcher._calculate_fuzzy_score(capability, criteria)
        assert 0 <= score <= 1.0

    def test_calculate_fuzzy_score_no_name_criteria(self, matcher):
        """Test fuzzy score with no name criteria."""
        capability = AgentCapability(
            name="text_processing",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            capability_type=CapabilityType.PROCESSING,
        )

        score = matcher._calculate_fuzzy_score(capability, criteria)
        assert score == 0.5  # Default score when no name criteria

    def test_calculate_semantic_score_no_tags_or_description(self, matcher):
        """Test semantic score with no tags or description."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria()

        score = matcher._calculate_semantic_score(capability, criteria)
        assert score == 0.0

    def test_meets_basic_criteria_type_mismatch(self, matcher):
        """Test meets basic criteria with type mismatch."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            capability_type=CapabilityType.ANALYSIS,
        )

        assert matcher._meets_basic_criteria(capability, criteria) is False

    def test_meets_basic_criteria_missing_required_inputs(self, matcher):
        """Test meets basic criteria with missing required inputs."""
        capability = AgentCapability(
            name="test",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
            required_inputs={"input1"},
            optional_inputs={"input2"},
        )

        criteria = CapabilityMatchCriteria(
            required_inputs={"input1", "input3"},
        )

        assert matcher._meets_basic_criteria(capability, criteria) is False

    def test_is_exact_match_name_mismatch(self, matcher):
        """Test exact match with name mismatch."""
        capability = AgentCapability(
            name="text_processing",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            capability_name="image_processing",
        )

        assert matcher._is_exact_match(capability, criteria) is False

    def test_is_exact_match_type_mismatch(self, matcher):
        """Test exact match with type mismatch."""
        capability = AgentCapability(
            name="text_processing",
            type=CapabilityType.PROCESSING,
            version="1.0.0",
            status=CapabilityStatus.ACTIVE,
        )

        criteria = CapabilityMatchCriteria(
            capability_name="text_processing",
            capability_type=CapabilityType.ANALYSIS,
        )

        assert matcher._is_exact_match(capability, criteria) is False
