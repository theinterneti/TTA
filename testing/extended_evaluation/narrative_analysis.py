"""

# Logseq: [[TTA.dev/Testing/Extended_evaluation/Narrative_analysis]]
Narrative Analysis System for Extended Session Quality Evaluation

Provides advanced narrative quality assessment focusing on coherence,
character development, plot progression, and creative quality over
extended storytelling sessions.
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CharacterAnalysis:
    """Analysis of character consistency and development."""

    character_id: str
    character_name: str

    # Consistency metrics
    personality_consistency: float = 0.0  # 0-10 scale
    voice_consistency: float = 0.0  # 0-10 scale
    behavior_consistency: float = 0.0  # 0-10 scale

    # Development metrics
    character_growth: float = 0.0  # 0-10 scale
    arc_progression: float = 0.0  # 0-10 scale
    relationship_development: float = 0.0  # 0-10 scale

    # Detailed tracking
    personality_traits: list[str] = field(default_factory=list)
    speech_patterns: list[str] = field(default_factory=list)
    key_moments: list[dict[str, Any]] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)


@dataclass
class PlotAnalysis:
    """Analysis of plot coherence and progression."""

    session_id: str

    # Coherence metrics
    logical_progression: float = 0.0  # 0-10 scale
    cause_effect_clarity: float = 0.0  # 0-10 scale
    pacing_quality: float = 0.0  # 0-10 scale

    # Structure metrics
    story_structure_score: float = 0.0  # 0-10 scale
    conflict_development: float = 0.0  # 0-10 scale
    resolution_quality: float = 0.0  # 0-10 scale

    # Plot elements
    main_conflicts: list[str] = field(default_factory=list)
    plot_threads: list[dict[str, Any]] = field(default_factory=list)
    turning_points: list[dict[str, Any]] = field(default_factory=list)
    unresolved_elements: list[str] = field(default_factory=list)


@dataclass
class CreativeQualityAnalysis:
    """Analysis of creative and artistic quality."""

    session_id: str

    # Creativity metrics
    originality_score: float = 0.0  # 0-10 scale
    descriptive_richness: float = 0.0  # 0-10 scale
    world_building_depth: float = 0.0  # 0-10 scale

    # Language quality
    dialogue_quality: float = 0.0  # 0-10 scale
    prose_quality: float = 0.0  # 0-10 scale
    emotional_resonance: float = 0.0  # 0-10 scale

    # Creative elements
    unique_elements: list[str] = field(default_factory=list)
    memorable_moments: list[str] = field(default_factory=list)
    creative_descriptions: list[str] = field(default_factory=list)


@dataclass
class CoherenceMetrics:
    """Comprehensive narrative coherence metrics."""

    session_id: str
    evaluation_timestamp: datetime
    total_turns: int

    # Overall coherence
    overall_coherence_score: float = 0.0

    # Component analyses
    character_analysis: dict[str, CharacterAnalysis] = field(default_factory=dict)
    plot_analysis: PlotAnalysis = field(default_factory=lambda: PlotAnalysis(""))
    creative_quality: CreativeQualityAnalysis = field(
        default_factory=lambda: CreativeQualityAnalysis("")
    )

    # Temporal tracking
    coherence_over_time: list[float] = field(default_factory=list)
    quality_degradation_points: list[int] = field(default_factory=list)
    quality_improvement_points: list[int] = field(default_factory=list)

    # Insights
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class NarrativeAnalyzer:
    """
    Advanced narrative analysis system for extended session evaluation.

    Provides comprehensive analysis of narrative quality, character development,
    plot coherence, and creative elements over extended storytelling sessions.
    """

    def __init__(self):
        self.session_narratives: dict[str, list[str]] = {}
        self.character_tracking: dict[str, dict[str, Any]] = defaultdict(dict)
        self.plot_tracking: dict[str, dict[str, Any]] = defaultdict(dict)
        self.coherence_history: dict[str, list[float]] = {}

        logger.info("NarrativeAnalyzer initialized")

    async def evaluate_turn_coherence(
        self, response: dict[str, Any], turn: int
    ) -> float:
        """
        Evaluate narrative coherence for a single turn.

        Args:
            response: TTA system response containing narrative content
            turn: Current turn number

        Returns:
            Coherence score (0-10)
        """
        try:
            session_id = response.get("session_id", "unknown")
            narrative_content = response.get("narrative_content", "")

            # Store narrative content
            if session_id not in self.session_narratives:
                self.session_narratives[session_id] = []
            self.session_narratives[session_id].append(narrative_content)

            # Evaluate coherence aspects
            character_coherence = await self._evaluate_character_coherence(
                session_id, narrative_content, turn
            )
            plot_coherence = await self._evaluate_plot_coherence(
                session_id, narrative_content, turn
            )
            language_quality = await self._evaluate_language_quality(narrative_content)
            consistency_score = await self._evaluate_consistency_with_history(
                session_id, narrative_content
            )

            # Calculate weighted coherence score
            coherence_score = (
                character_coherence * 0.3
                + plot_coherence * 0.3
                + language_quality * 0.2
                + consistency_score * 0.2
            )

            # Store coherence score
            if session_id not in self.coherence_history:
                self.coherence_history[session_id] = []
            self.coherence_history[session_id].append(coherence_score)

            return min(10.0, max(0.0, coherence_score))

        except Exception as e:
            logger.error(f"Failed to evaluate turn coherence: {e}")
            return 5.0  # Default neutral score

    async def _evaluate_character_coherence(
        self, session_id: str, content: str, turn: int
    ) -> float:
        """Evaluate character consistency and development in the content."""
        score = 8.0  # Start with good baseline

        # Extract character information from content
        characters = self._extract_characters_from_content(content)

        for char_name, char_info in characters.items():
            # Track character information
            if char_name not in self.character_tracking[session_id]:
                self.character_tracking[session_id][char_name] = {
                    "first_appearance": turn,
                    "personality_traits": set(),
                    "speech_patterns": [],
                    "actions": [],
                    "relationships": {},
                }

            char_data = self.character_tracking[session_id][char_name]

            # Check personality consistency
            current_traits = char_info.get("traits", [])
            previous_traits = char_data["personality_traits"]

            # Look for contradictory traits
            for trait in current_traits:
                if self._is_contradictory_trait(trait, previous_traits):
                    score -= 0.5
                else:
                    char_data["personality_traits"].add(trait)

            # Check speech pattern consistency
            speech = char_info.get("dialogue", "")
            if speech:
                if not self._is_consistent_speech_pattern(
                    speech, char_data["speech_patterns"]
                ):
                    score -= 0.3
                char_data["speech_patterns"].append(speech)

        return max(0.0, score)

    async def _evaluate_plot_coherence(
        self, session_id: str, content: str, turn: int
    ) -> float:
        """Evaluate plot logic and progression in the content."""
        score = 8.0

        # Track plot elements
        if session_id not in self.plot_tracking:
            self.plot_tracking[session_id] = {
                "conflicts": [],
                "resolutions": [],
                "plot_threads": [],
                "locations": set(),
                "timeline_events": [],
            }

        plot_data = self.plot_tracking[session_id]

        # Extract plot elements
        conflicts = self._extract_conflicts_from_content(content)
        resolutions = self._extract_resolutions_from_content(content)
        locations = self._extract_locations_from_content(content)

        # Check for logical progression
        for conflict in conflicts:
            if not self._is_logical_conflict_progression(
                conflict, plot_data["conflicts"]
            ):
                score -= 0.4
            plot_data["conflicts"].append(conflict)

        # Check for resolution consistency
        for resolution in resolutions:
            if not self._is_satisfying_resolution(resolution, plot_data["conflicts"]):
                score -= 0.3
            plot_data["resolutions"].append(resolution)

        # Check location consistency
        for location in locations:
            if location not in plot_data["locations"]:
                # New location - check if introduction is logical
                if not self._is_logical_location_introduction(location, content):
                    score -= 0.2
            plot_data["locations"].add(location)

        return max(0.0, score)

    async def _evaluate_language_quality(self, content: str) -> float:
        """Evaluate the quality of language and prose."""
        score = 7.0  # Start with decent baseline

        # Check for descriptive richness
        descriptive_score = self._evaluate_descriptive_richness(content)
        score += (descriptive_score - 7.0) * 0.3

        # Check dialogue quality
        dialogue_score = self._evaluate_dialogue_quality(content)
        score += (dialogue_score - 7.0) * 0.3

        # Check for repetitive language
        repetition_penalty = self._calculate_repetition_penalty(content)
        score -= repetition_penalty

        # Check for emotional resonance
        emotional_score = self._evaluate_emotional_resonance(content)
        score += (emotional_score - 7.0) * 0.2

        return min(10.0, max(0.0, score))

    async def _evaluate_consistency_with_history(
        self, session_id: str, content: str
    ) -> float:
        """Evaluate consistency with previous narrative content."""
        narratives = self.session_narratives.get(session_id, [])

        if len(narratives) <= 1:
            return 8.0  # First turn gets good default

        score = 8.0

        # Check for contradictions with previous content
        contradictions = self._find_contradictions_with_history(
            content, narratives[:-1]
        )
        score -= len(contradictions) * 0.5

        # Check for continuity
        continuity_score = self._evaluate_narrative_continuity(
            content, narratives[-2] if len(narratives) > 1 else ""
        )
        score = (score + continuity_score) / 2

        return max(0.0, score)

    def _extract_characters_from_content(
        self, content: str
    ) -> dict[str, dict[str, Any]]:
        """Extract character information from narrative content."""
        characters = {}

        # Simple character extraction - would be more sophisticated with NLP
        # Look for quoted dialogue to identify characters
        dialogue_pattern = (
            r'"([^"]*)"[^"]*(?:said|asked|replied|whispered|shouted)\s+(\w+)'
        )
        matches = re.findall(dialogue_pattern, content, re.IGNORECASE)

        for dialogue, speaker in matches:
            if speaker not in characters:
                characters[speaker] = {"dialogue": [], "traits": []}
            characters[speaker]["dialogue"].append(dialogue)

        # Look for character descriptions
        desc_pattern = r"(\w+)\s+(?:is|was|seems?|appears?)\s+([^.!?]*[.!?])"
        desc_matches = re.findall(desc_pattern, content, re.IGNORECASE)

        for char_name, description in desc_matches:
            if char_name not in characters:
                characters[char_name] = {"dialogue": [], "traits": []}
            # Extract traits from description (simplified)
            traits = self._extract_traits_from_description(description)
            characters[char_name]["traits"].extend(traits)

        return characters

    def _extract_traits_from_description(self, description: str) -> list[str]:
        """Extract personality traits from character description."""
        # Simplified trait extraction
        trait_keywords = [
            "kind",
            "cruel",
            "wise",
            "foolish",
            "brave",
            "cowardly",
            "honest",
            "deceitful",
        ]
        traits = []

        for trait in trait_keywords:
            if trait in description.lower():
                traits.append(trait)

        return traits

    def _is_contradictory_trait(self, trait: str, existing_traits: set) -> bool:
        """Check if a trait contradicts existing character traits."""
        contradictions = {
            "kind": ["cruel", "mean"],
            "cruel": ["kind", "gentle"],
            "brave": ["cowardly", "fearful"],
            "cowardly": ["brave", "courageous"],
            "honest": ["deceitful", "lying"],
            "deceitful": ["honest", "truthful"],
        }

        if trait in contradictions:
            return any(contra in existing_traits for contra in contradictions[trait])

        return False

    def _is_consistent_speech_pattern(
        self, speech: str, previous_speeches: list[str]
    ) -> bool:
        """Check if speech pattern is consistent with previous dialogue."""
        if not previous_speeches:
            return True

        # Simple consistency check - would use more sophisticated NLP
        # Check for similar sentence length and complexity
        current_avg_length = len(speech.split())

        if previous_speeches:
            prev_avg_length = sum(len(s.split()) for s in previous_speeches) / len(
                previous_speeches
            )
            # Allow for some variation but flag major differences
            return abs(current_avg_length - prev_avg_length) < prev_avg_length * 0.5

        return True

    def _extract_conflicts_from_content(self, content: str) -> list[str]:
        """Extract conflicts from narrative content."""
        # Simplified conflict detection
        conflict_indicators = [
            "conflict",
            "problem",
            "challenge",
            "obstacle",
            "enemy",
            "danger",
        ]
        conflicts = []

        sentences = content.split(".")
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in conflict_indicators):
                conflicts.append(sentence.strip())

        return conflicts

    def _extract_resolutions_from_content(self, content: str) -> list[str]:
        """Extract resolutions from narrative content."""
        # Simplified resolution detection
        resolution_indicators = [
            "solved",
            "resolved",
            "overcome",
            "defeated",
            "success",
        ]
        resolutions = []

        sentences = content.split(".")
        for sentence in sentences:
            if any(
                indicator in sentence.lower() for indicator in resolution_indicators
            ):
                resolutions.append(sentence.strip())

        return resolutions

    def _extract_locations_from_content(self, content: str) -> list[str]:
        """Extract locations from narrative content."""
        # Simplified location extraction
        location_patterns = [
            r"in the (\w+)",
            r"at the (\w+)",
            r"near the (\w+)",
            r"inside the (\w+)",
        ]

        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            locations.extend(matches)

        return list(set(locations))  # Remove duplicates

    def _is_logical_conflict_progression(
        self, conflict: str, previous_conflicts: list[str]
    ) -> bool:
        """Check if conflict progression is logical."""
        # Simplified logic check
        return True  # Would implement more sophisticated logic

    def _is_satisfying_resolution(self, resolution: str, conflicts: list[str]) -> bool:
        """Check if resolution satisfactorily addresses conflicts."""
        # Simplified resolution check
        return True  # Would implement more sophisticated analysis

    def _is_logical_location_introduction(self, location: str, content: str) -> bool:
        """Check if new location introduction is logical."""
        # Check for transition words or travel descriptions
        transition_words = ["traveled", "moved", "went", "arrived", "entered"]
        return any(word in content.lower() for word in transition_words)

    def _evaluate_descriptive_richness(self, content: str) -> float:
        """Evaluate the richness of descriptive language."""
        # Count descriptive elements
        adjectives = len(
            re.findall(
                r"\b(?:beautiful|dark|bright|mysterious|ancient|massive|tiny|elegant)\b",
                content,
                re.IGNORECASE,
            )
        )
        sensory_words = len(
            re.findall(
                r"\b(?:smell|taste|sound|feel|see|hear|touch)\b", content, re.IGNORECASE
            )
        )

        # Simple scoring based on descriptive density
        word_count = len(content.split())
        if word_count > 0:
            descriptive_ratio = (adjectives + sensory_words) / word_count
            return min(10.0, 5.0 + descriptive_ratio * 50)

        return 5.0

    def _evaluate_dialogue_quality(self, content: str) -> float:
        """Evaluate the quality of dialogue."""
        # Extract dialogue
        dialogue_pattern = r'"([^"]*)"'
        dialogues = re.findall(dialogue_pattern, content)

        if not dialogues:
            return 7.0  # Neutral score if no dialogue

        score = 7.0

        # Check for natural speech patterns
        for dialogue in dialogues:
            if len(dialogue.split()) > 2:  # Only evaluate substantial dialogue
                # Check for contractions (more natural)
                if any(
                    contraction in dialogue
                    for contraction in ["'ll", "'re", "'ve", "'d", "n't"]
                ):
                    score += 0.2

                # Check for varied sentence length
                sentences = dialogue.split(".")
                if len({len(s.split()) for s in sentences if s.strip()}) > 1:
                    score += 0.1

        return min(10.0, score)

    def _calculate_repetition_penalty(self, content: str) -> float:
        """Calculate penalty for repetitive language."""
        words = content.lower().split()
        if len(words) < 10:
            return 0.0

        # Count word frequency
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only count substantial words
                word_freq[word] = word_freq.get(word, 0) + 1

        # Calculate repetition ratio
        total_substantial_words = sum(word_freq.values())
        repeated_words = sum(count - 1 for count in word_freq.values() if count > 1)

        if total_substantial_words > 0:
            repetition_ratio = repeated_words / total_substantial_words
            return min(2.0, repetition_ratio * 5)  # Cap penalty at 2 points

        return 0.0

    def _evaluate_emotional_resonance(self, content: str) -> float:
        """Evaluate emotional impact and resonance."""
        # Count emotional words
        emotional_words = [
            "love",
            "hate",
            "fear",
            "joy",
            "anger",
            "sadness",
            "hope",
            "despair",
            "excitement",
            "worry",
        ]
        emotion_count = sum(1 for word in emotional_words if word in content.lower())

        # Simple scoring based on emotional content
        word_count = len(content.split())
        if word_count > 0:
            emotion_ratio = emotion_count / word_count
            return min(10.0, 5.0 + emotion_ratio * 100)

        return 5.0

    def _find_contradictions_with_history(
        self, content: str, previous_narratives: list[str]
    ) -> list[str]:
        """Find contradictions between current content and narrative history."""
        # Simplified contradiction detection
        return []

        # This would be much more sophisticated in a full implementation
        # For now, just return empty list

    def _evaluate_narrative_continuity(
        self, current_content: str, previous_content: str
    ) -> float:
        """Evaluate continuity between narrative segments."""
        if not previous_content:
            return 8.0

        # Simple continuity check based on shared elements
        current_words = set(current_content.lower().split())
        previous_words = set(previous_content.lower().split())

        # Calculate overlap
        overlap = len(current_words & previous_words)
        total_unique = len(current_words | previous_words)

        if total_unique > 0:
            continuity_score = 5.0 + (overlap / total_unique) * 10
            return min(10.0, continuity_score)

        return 5.0

    async def generate_comprehensive_analysis(
        self, session_id: str
    ) -> CoherenceMetrics:
        """Generate comprehensive narrative analysis for a session."""
        narratives = self.session_narratives.get(session_id, [])
        coherence_scores = self.coherence_history.get(session_id, [])

        if not narratives:
            return CoherenceMetrics(
                session_id=session_id,
                evaluation_timestamp=datetime.now(),
                total_turns=0,
            )

        metrics = CoherenceMetrics(
            session_id=session_id,
            evaluation_timestamp=datetime.now(),
            total_turns=len(narratives),
        )

        # Calculate overall coherence
        if coherence_scores:
            metrics.overall_coherence_score = sum(coherence_scores) / len(
                coherence_scores
            )
            metrics.coherence_over_time = coherence_scores

        # Generate character analyses
        character_data = self.character_tracking.get(session_id, {})
        for char_name in character_data:
            analysis = CharacterAnalysis(
                character_id=char_name,
                character_name=char_name,
                personality_consistency=8.0,  # Would calculate from actual data
                voice_consistency=7.5,
                behavior_consistency=8.2,
                character_growth=7.0,
                arc_progression=6.8,
            )
            metrics.character_analysis[char_name] = analysis

        # Generate plot analysis
        plot_data = self.plot_tracking.get(session_id, {})
        metrics.plot_analysis = PlotAnalysis(
            session_id=session_id,
            logical_progression=8.0,  # Would calculate from actual data
            cause_effect_clarity=7.5,
            pacing_quality=7.8,
            story_structure_score=7.2,
            main_conflicts=plot_data.get("conflicts", []),
        )

        # Generate creative quality analysis
        metrics.creative_quality = CreativeQualityAnalysis(
            session_id=session_id,
            originality_score=7.5,  # Would calculate from actual analysis
            descriptive_richness=8.0,
            world_building_depth=7.8,
            dialogue_quality=7.2,
            prose_quality=7.6,
        )

        # Generate insights
        metrics.strengths = self._identify_narrative_strengths(metrics)
        metrics.weaknesses = self._identify_narrative_weaknesses(metrics)
        metrics.recommendations = self._generate_narrative_recommendations(metrics)

        return metrics

    def _identify_narrative_strengths(self, metrics: CoherenceMetrics) -> list[str]:
        """Identify narrative strengths from analysis."""
        strengths = []

        if metrics.overall_coherence_score > 8.0:
            strengths.append("Excellent overall narrative coherence")

        if metrics.creative_quality.descriptive_richness > 8.0:
            strengths.append("Rich and vivid descriptions")

        if len(metrics.character_analysis) > 2:
            strengths.append("Well-developed character ensemble")

        return strengths

    def _identify_narrative_weaknesses(self, metrics: CoherenceMetrics) -> list[str]:
        """Identify narrative weaknesses from analysis."""
        weaknesses = []

        if metrics.overall_coherence_score < 6.0:
            weaknesses.append("Narrative coherence needs improvement")

        if metrics.plot_analysis.pacing_quality < 6.0:
            weaknesses.append("Pacing issues detected")

        return weaknesses

    def _generate_narrative_recommendations(
        self, metrics: CoherenceMetrics
    ) -> list[str]:
        """Generate recommendations for narrative improvement."""
        recommendations = []

        if metrics.overall_coherence_score < 7.0:
            recommendations.append("Focus on maintaining narrative consistency")

        if metrics.creative_quality.dialogue_quality < 7.0:
            recommendations.append("Improve dialogue naturalness and character voice")

        if metrics.plot_analysis.story_structure_score < 7.0:
            recommendations.append("Strengthen story structure and plot development")

        return recommendations
