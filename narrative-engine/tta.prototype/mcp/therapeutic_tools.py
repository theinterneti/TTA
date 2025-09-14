"""
Therapeutic Tools for MCP Integration

This module provides therapeutic text adventure tools that can be exposed
through MCP servers for external integration and extensibility.

Classes:
    TherapeuticToolsManager: Manager for therapeutic tools
    TherapeuticTool: Base class for therapeutic tools
    EmotionalStateAnalyzer: Tool for analyzing emotional states
    CopingStrategyGenerator: Tool for generating coping strategies
    TherapeuticInterventionSelector: Tool for selecting appropriate interventions
    NarrativeTherapyIntegrator: Tool for integrating therapy into narrative
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TherapeuticContext:
    """Context information for therapeutic interventions."""
    user_id: str
    session_id: str
    current_emotional_state: str
    narrative_context: str
    user_history: dict[str, Any]
    therapeutic_goals: list[str]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TherapeuticResponse:
    """Response from a therapeutic tool."""
    tool_name: str
    response_type: str
    content: str
    confidence: float
    metadata: dict[str, Any]
    therapeutic_value: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TherapeuticTool(ABC):
    """Base class for therapeutic tools."""

    def __init__(self, name: str, description: str):
        """
        Initialize the therapeutic tool.

        Args:
            name: Name of the tool
            description: Description of the tool's purpose
        """
        self.name = name
        self.description = description
        self.usage_count = 0
        self.success_rate = 0.0

    @abstractmethod
    def process(self, context: TherapeuticContext) -> TherapeuticResponse:
        """
        Process a therapeutic request.

        Args:
            context: Therapeutic context information

        Returns:
            TherapeuticResponse: Response from the tool
        """
        pass

    def get_tool_info(self) -> dict[str, Any]:
        """Get information about this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "tool_type": self.__class__.__name__
        }


class EmotionalStateAnalyzer(TherapeuticTool):
    """Tool for analyzing emotional states from user input."""

    def __init__(self):
        super().__init__(
            name="emotional_state_analyzer",
            description="Analyzes user emotional state from text input and narrative choices"
        )

        # Emotional indicators mapping
        self.emotional_indicators = {
            "anxiety": ["worried", "nervous", "scared", "anxious", "panic", "stress"],
            "depression": ["sad", "hopeless", "empty", "worthless", "tired", "alone"],
            "anger": ["angry", "frustrated", "mad", "furious", "irritated", "rage"],
            "joy": ["happy", "excited", "joyful", "pleased", "content", "elated"],
            "fear": ["afraid", "terrified", "frightened", "scared", "worried", "panic"],
            "calm": ["peaceful", "relaxed", "serene", "tranquil", "composed", "centered"]
        }

    def process(self, context: TherapeuticContext) -> TherapeuticResponse:
        """
        Analyze emotional state from context.

        Args:
            context: Therapeutic context information

        Returns:
            TherapeuticResponse: Analysis results
        """
        self.usage_count += 1

        try:
            # Analyze current emotional state
            emotional_analysis = self._analyze_emotional_indicators(
                context.current_emotional_state,
                context.narrative_context
            )

            # Generate emotional pattern insights
            patterns = self._identify_emotional_patterns(context.user_history)

            # Calculate confidence based on available data
            confidence = self._calculate_confidence(emotional_analysis, patterns)

            # Create response
            response_content = {
                "primary_emotion": emotional_analysis["primary_emotion"],
                "emotional_intensity": emotional_analysis["intensity"],
                "secondary_emotions": emotional_analysis["secondary_emotions"],
                "emotional_patterns": patterns,
                "recommendations": self._generate_emotional_recommendations(emotional_analysis)
            }

            therapeutic_value = self._calculate_therapeutic_value(emotional_analysis)

            response = TherapeuticResponse(
                tool_name=self.name,
                response_type="emotional_analysis",
                content=json.dumps(response_content, indent=2),
                confidence=confidence,
                metadata={
                    "analysis_method": "keyword_pattern_matching",
                    "emotional_indicators_found": emotional_analysis["indicators_found"],
                    "pattern_analysis_depth": len(patterns)
                },
                therapeutic_value=therapeutic_value
            )

            # Update success rate
            self.success_rate = (self.success_rate * (self.usage_count - 1) + confidence) / self.usage_count

            return response

        except Exception as e:
            logger.error(f"Error in emotional state analysis: {e}")
            return TherapeuticResponse(
                tool_name=self.name,
                response_type="error",
                content=f"Error analyzing emotional state: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)},
                therapeutic_value=0.0
            )

    def _analyze_emotional_indicators(self, emotional_state: str, narrative_context: str) -> dict[str, Any]:
        """Analyze emotional indicators in text."""
        text_to_analyze = f"{emotional_state} {narrative_context}".lower()

        emotion_scores = {}
        indicators_found = []

        # Score each emotion based on keyword presence
        for emotion, keywords in self.emotional_indicators.items():
            score = 0
            found_keywords = []

            for keyword in keywords:
                if keyword in text_to_analyze:
                    score += 1
                    found_keywords.append(keyword)

            if score > 0:
                emotion_scores[emotion] = score / len(keywords)  # Normalize score
                indicators_found.extend(found_keywords)

        # Determine primary emotion
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else "neutral"

        # Calculate intensity
        intensity = emotion_scores.get(primary_emotion, 0.0)

        # Get secondary emotions
        secondary_emotions = [
            emotion for emotion, score in sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
            if score > 0.1
        ]

        return {
            "primary_emotion": primary_emotion,
            "intensity": min(intensity * 2, 1.0),  # Scale intensity
            "secondary_emotions": secondary_emotions,
            "emotion_scores": emotion_scores,
            "indicators_found": indicators_found
        }

    def _identify_emotional_patterns(self, user_history: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify emotional patterns from user history."""
        patterns = []

        # Analyze session history if available
        if "sessions" in user_history:
            sessions = user_history["sessions"]
            if len(sessions) >= 2:
                # Look for emotional progression patterns
                recent_emotions = [session.get("primary_emotion", "neutral") for session in sessions[-5:]]

                if len(set(recent_emotions)) == 1:
                    patterns.append({
                        "type": "consistent_emotion",
                        "emotion": recent_emotions[0],
                        "duration": len(recent_emotions),
                        "significance": "high"
                    })

                # Look for improvement patterns
                negative_emotions = ["anxiety", "depression", "anger", "fear"]
                positive_emotions = ["joy", "calm"]

                if any(emotion in negative_emotions for emotion in recent_emotions[:2]) and \
                   any(emotion in positive_emotions for emotion in recent_emotions[-2:]):
                    patterns.append({
                        "type": "emotional_improvement",
                        "from_emotions": recent_emotions[:2],
                        "to_emotions": recent_emotions[-2:],
                        "significance": "high"
                    })

        return patterns

    def _calculate_confidence(self, emotional_analysis: dict[str, Any], patterns: list[dict[str, Any]]) -> float:
        """Calculate confidence in the analysis."""
        base_confidence = 0.5

        # Increase confidence based on indicators found
        indicators_bonus = min(len(emotional_analysis["indicators_found"]) * 0.1, 0.3)

        # Increase confidence based on pattern consistency
        pattern_bonus = min(len(patterns) * 0.1, 0.2)

        return min(base_confidence + indicators_bonus + pattern_bonus, 1.0)

    def _generate_emotional_recommendations(self, emotional_analysis: dict[str, Any]) -> list[str]:
        """Generate recommendations based on emotional analysis."""
        recommendations = []
        primary_emotion = emotional_analysis["primary_emotion"]
        intensity = emotional_analysis["intensity"]

        if primary_emotion == "anxiety" and intensity > 0.5:
            recommendations.extend([
                "Consider introducing breathing exercises in the narrative",
                "Provide grounding techniques through character interactions",
                "Create safe spaces in the story for emotional processing"
            ])
        elif primary_emotion == "depression" and intensity > 0.5:
            recommendations.extend([
                "Focus on small, achievable goals within the narrative",
                "Introduce supportive characters and relationships",
                "Highlight moments of hope and possibility"
            ])
        elif primary_emotion == "anger" and intensity > 0.5:
            recommendations.extend([
                "Provide healthy outlets for anger expression",
                "Explore underlying causes through story elements",
                "Introduce conflict resolution scenarios"
            ])
        elif primary_emotion in ["joy", "calm"]:
            recommendations.extend([
                "Reinforce positive emotional states",
                "Build on current strengths and resources",
                "Introduce growth opportunities"
            ])

        return recommendations

    def _calculate_therapeutic_value(self, emotional_analysis: dict[str, Any]) -> float:
        """Calculate the therapeutic value of the analysis."""
        base_value = 0.6

        # Higher value for identifying concerning emotions
        concerning_emotions = ["anxiety", "depression", "anger", "fear"]
        if emotional_analysis["primary_emotion"] in concerning_emotions:
            base_value += 0.2

        # Higher value for high-intensity emotions (need more attention)
        if emotional_analysis["intensity"] > 0.7:
            base_value += 0.1

        # Higher value for complex emotional states
        if len(emotional_analysis["secondary_emotions"]) > 1:
            base_value += 0.1

        return min(base_value, 1.0)


class CopingStrategyGenerator(TherapeuticTool):
    """Tool for generating appropriate coping strategies."""

    def __init__(self):
        super().__init__(
            name="coping_strategy_generator",
            description="Generates personalized coping strategies based on emotional state and context"
        )

        # Coping strategies database
        self.coping_strategies = {
            "anxiety": [
                {
                    "name": "Deep Breathing",
                    "description": "Practice slow, deep breathing to calm the nervous system",
                    "narrative_integration": "Have the character teach breathing techniques during a peaceful moment",
                    "difficulty": "easy",
                    "effectiveness": 0.8
                },
                {
                    "name": "Grounding Technique",
                    "description": "Focus on 5 things you can see, 4 you can hear, 3 you can touch, 2 you can smell, 1 you can taste",
                    "narrative_integration": "Guide the character through sensory exploration of their environment",
                    "difficulty": "easy",
                    "effectiveness": 0.7
                },
                {
                    "name": "Progressive Muscle Relaxation",
                    "description": "Systematically tense and relax different muscle groups",
                    "narrative_integration": "Incorporate physical relaxation into character actions",
                    "difficulty": "medium",
                    "effectiveness": 0.9
                }
            ],
            "depression": [
                {
                    "name": "Behavioral Activation",
                    "description": "Engage in small, meaningful activities to improve mood",
                    "narrative_integration": "Present small, achievable tasks that provide sense of accomplishment",
                    "difficulty": "medium",
                    "effectiveness": 0.8
                },
                {
                    "name": "Gratitude Practice",
                    "description": "Identify three things to be grateful for each day",
                    "narrative_integration": "Have characters reflect on positive aspects of their journey",
                    "difficulty": "easy",
                    "effectiveness": 0.6
                },
                {
                    "name": "Social Connection",
                    "description": "Reach out to supportive friends or family members",
                    "narrative_integration": "Introduce supportive characters and meaningful relationships",
                    "difficulty": "medium",
                    "effectiveness": 0.9
                }
            ],
            "anger": [
                {
                    "name": "Anger Thermometer",
                    "description": "Rate anger intensity from 1-10 and use appropriate responses",
                    "narrative_integration": "Help character assess and respond to conflict situations",
                    "difficulty": "easy",
                    "effectiveness": 0.7
                },
                {
                    "name": "Time-Out Technique",
                    "description": "Take a break from the situation to cool down",
                    "narrative_integration": "Provide opportunities for character to step back and reflect",
                    "difficulty": "easy",
                    "effectiveness": 0.8
                },
                {
                    "name": "Assertiveness Training",
                    "description": "Express needs and feelings in a healthy, direct way",
                    "narrative_integration": "Practice healthy communication through character dialogue",
                    "difficulty": "hard",
                    "effectiveness": 0.9
                }
            ],
            "general": [
                {
                    "name": "Mindfulness Meditation",
                    "description": "Practice present-moment awareness without judgment",
                    "narrative_integration": "Incorporate mindful moments into story progression",
                    "difficulty": "medium",
                    "effectiveness": 0.8
                },
                {
                    "name": "Journaling",
                    "description": "Write about thoughts and feelings to process emotions",
                    "narrative_integration": "Have character keep a journal or reflect on experiences",
                    "difficulty": "easy",
                    "effectiveness": 0.7
                },
                {
                    "name": "Physical Exercise",
                    "description": "Engage in physical activity to improve mood and reduce stress",
                    "narrative_integration": "Include physical challenges or activities in the story",
                    "difficulty": "medium",
                    "effectiveness": 0.9
                }
            ]
        }

    def process(self, context: TherapeuticContext) -> TherapeuticResponse:
        """
        Generate appropriate coping strategies.

        Args:
            context: Therapeutic context information

        Returns:
            TherapeuticResponse: Generated coping strategies
        """
        self.usage_count += 1

        try:
            # Determine primary emotional state
            primary_emotion = self._extract_primary_emotion(context.current_emotional_state)

            # Select appropriate strategies
            strategies = self._select_strategies(primary_emotion, context)

            # Personalize strategies based on user history
            personalized_strategies = self._personalize_strategies(strategies, context.user_history)

            # Calculate confidence
            confidence = self._calculate_strategy_confidence(personalized_strategies, context)

            # Create response
            response_content = {
                "primary_emotion": primary_emotion,
                "recommended_strategies": personalized_strategies,
                "implementation_guidance": self._generate_implementation_guidance(personalized_strategies),
                "narrative_integration_suggestions": self._generate_narrative_integration(personalized_strategies)
            }

            therapeutic_value = self._calculate_strategy_therapeutic_value(personalized_strategies)

            response = TherapeuticResponse(
                tool_name=self.name,
                response_type="coping_strategies",
                content=json.dumps(response_content, indent=2),
                confidence=confidence,
                metadata={
                    "strategy_count": len(personalized_strategies),
                    "target_emotion": primary_emotion,
                    "personalization_applied": len(context.user_history) > 0
                },
                therapeutic_value=therapeutic_value
            )

            # Update success rate
            self.success_rate = (self.success_rate * (self.usage_count - 1) + confidence) / self.usage_count

            return response

        except Exception as e:
            logger.error(f"Error generating coping strategies: {e}")
            return TherapeuticResponse(
                tool_name=self.name,
                response_type="error",
                content=f"Error generating coping strategies: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)},
                therapeutic_value=0.0
            )

    def _extract_primary_emotion(self, emotional_state: str) -> str:
        """Extract primary emotion from emotional state description."""
        emotional_state_lower = emotional_state.lower()

        # Check for specific emotions
        if any(word in emotional_state_lower for word in ["anxious", "worried", "nervous", "panic"]):
            return "anxiety"
        elif any(word in emotional_state_lower for word in ["sad", "depressed", "hopeless", "empty"]):
            return "depression"
        elif any(word in emotional_state_lower for word in ["angry", "frustrated", "mad", "furious"]):
            return "anger"
        elif any(word in emotional_state_lower for word in ["afraid", "scared", "terrified", "fear"]):
            return "anxiety"  # Treat fear as anxiety for coping purposes
        else:
            return "general"

    def _select_strategies(self, primary_emotion: str, context: TherapeuticContext) -> list[dict[str, Any]]:
        """Select appropriate strategies for the emotional state."""
        # Get emotion-specific strategies
        emotion_strategies = self.coping_strategies.get(primary_emotion, [])

        # Add some general strategies
        general_strategies = self.coping_strategies.get("general", [])

        # Combine and limit to top strategies
        all_strategies = emotion_strategies + general_strategies[:2]

        # Sort by effectiveness and select top 3-4
        sorted_strategies = sorted(all_strategies, key=lambda x: x["effectiveness"], reverse=True)

        return sorted_strategies[:4]

    def _personalize_strategies(self, strategies: list[dict[str, Any]], user_history: dict[str, Any]) -> list[dict[str, Any]]:
        """Personalize strategies based on user history."""
        personalized = []

        # Get user preferences if available
        preferred_difficulty = user_history.get("preferred_difficulty", "medium")
        tried_strategies = user_history.get("tried_strategies", [])
        successful_strategies = user_history.get("successful_strategies", [])

        for strategy in strategies:
            strategy_copy = strategy.copy()

            # Add personalization notes
            personalization_notes = []

            # Check if user has tried this before
            if strategy["name"] in tried_strategies:
                if strategy["name"] in successful_strategies:
                    personalization_notes.append("You've found this helpful before")
                    strategy_copy["effectiveness"] += 0.1  # Boost effectiveness
                else:
                    personalization_notes.append("You've tried this before - consider modifications")

            # Adjust for difficulty preference
            if strategy["difficulty"] == preferred_difficulty:
                personalization_notes.append("Matches your preferred difficulty level")
                strategy_copy["effectiveness"] += 0.05

            strategy_copy["personalization_notes"] = personalization_notes
            personalized.append(strategy_copy)

        return personalized

    def _calculate_strategy_confidence(self, strategies: list[dict[str, Any]], context: TherapeuticContext) -> float:
        """Calculate confidence in strategy recommendations."""
        base_confidence = 0.7

        # Higher confidence with more user history
        history_bonus = min(len(context.user_history) * 0.05, 0.2)

        # Higher confidence with high-effectiveness strategies
        avg_effectiveness = sum(s["effectiveness"] for s in strategies) / len(strategies) if strategies else 0
        effectiveness_bonus = (avg_effectiveness - 0.5) * 0.2

        return min(base_confidence + history_bonus + effectiveness_bonus, 1.0)

    def _generate_implementation_guidance(self, strategies: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Generate implementation guidance for strategies."""
        guidance = []

        for strategy in strategies:
            guidance.append({
                "strategy": strategy["name"],
                "when_to_use": f"When feeling {strategy.get('target_emotion', 'overwhelmed')}",
                "how_to_start": f"Begin with {strategy['description'].split('.')[0].lower()}",
                "expected_outcome": f"Should help reduce intensity and provide {strategy.get('benefit', 'relief')}",
                "difficulty_level": strategy["difficulty"]
            })

        return guidance

    def _generate_narrative_integration(self, strategies: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Generate suggestions for integrating strategies into narrative."""
        integration_suggestions = []

        for strategy in strategies:
            integration_suggestions.append({
                "strategy": strategy["name"],
                "narrative_approach": strategy["narrative_integration"],
                "story_elements": self._suggest_story_elements(strategy),
                "character_actions": self._suggest_character_actions(strategy)
            })

        return integration_suggestions

    def _suggest_story_elements(self, strategy: dict[str, Any]) -> list[str]:
        """Suggest story elements that support the strategy."""
        strategy_name = strategy["name"].lower()

        if "breathing" in strategy_name:
            return ["peaceful garden setting", "meditation teacher character", "calming natural sounds"]
        elif "grounding" in strategy_name:
            return ["rich sensory environment", "detailed location descriptions", "interactive objects"]
        elif "gratitude" in strategy_name:
            return ["helpful NPCs", "beautiful scenery", "positive story outcomes"]
        elif "social" in strategy_name:
            return ["supportive companions", "community gatherings", "meaningful conversations"]
        else:
            return ["supportive environment", "encouraging characters", "safe spaces"]

    def _suggest_character_actions(self, strategy: dict[str, Any]) -> list[str]:
        """Suggest character actions that demonstrate the strategy."""
        strategy_name = strategy["name"].lower()

        if "breathing" in strategy_name:
            return ["character demonstrates breathing technique", "guides player through exercise", "models calm behavior"]
        elif "grounding" in strategy_name:
            return ["character points out sensory details", "encourages exploration", "asks about observations"]
        elif "gratitude" in strategy_name:
            return ["character expresses appreciation", "reflects on positive experiences", "encourages thankfulness"]
        elif "social" in strategy_name:
            return ["character offers support", "initiates meaningful conversation", "shows empathy"]
        else:
            return ["character models healthy coping", "provides encouragement", "offers guidance"]

    def _calculate_strategy_therapeutic_value(self, strategies: list[dict[str, Any]]) -> float:
        """Calculate therapeutic value of the strategy recommendations."""
        if not strategies:
            return 0.0

        # Base value for providing strategies
        base_value = 0.7

        # Higher value for evidence-based strategies
        avg_effectiveness = sum(s["effectiveness"] for s in strategies) / len(strategies)
        effectiveness_bonus = (avg_effectiveness - 0.5) * 0.2

        # Higher value for personalized strategies
        personalized_count = sum(1 for s in strategies if s.get("personalization_notes"))
        personalization_bonus = (personalized_count / len(strategies)) * 0.1

        return min(base_value + effectiveness_bonus + personalization_bonus, 1.0)


class TherapeuticToolsManager:
    """Manager for therapeutic tools and MCP integration."""

    def __init__(self):
        """Initialize the therapeutic tools manager."""
        self.tools: dict[str, TherapeuticTool] = {}
        self.usage_stats: dict[str, dict[str, Any]] = {}

        # Initialize default tools
        self._initialize_default_tools()

        logger.info(f"TherapeuticToolsManager initialized with {len(self.tools)} tools")

    def _initialize_default_tools(self):
        """Initialize default therapeutic tools."""
        # Add emotional state analyzer
        emotional_analyzer = EmotionalStateAnalyzer()
        self.register_tool(emotional_analyzer)

        # Add coping strategy generator
        coping_generator = CopingStrategyGenerator()
        self.register_tool(coping_generator)

        # Initialize usage stats
        for tool_name in self.tools.keys():
            self.usage_stats[tool_name] = {
                "total_uses": 0,
                "success_count": 0,
                "average_confidence": 0.0,
                "average_therapeutic_value": 0.0
            }

    def register_tool(self, tool: TherapeuticTool):
        """
        Register a therapeutic tool.

        Args:
            tool: Therapeutic tool to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered therapeutic tool: {tool.name}")

    def get_tool(self, tool_name: str) -> TherapeuticTool | None:
        """
        Get a therapeutic tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Optional[TherapeuticTool]: Tool if found, None otherwise
        """
        return self.tools.get(tool_name)

    def list_tools(self) -> list[dict[str, Any]]:
        """
        List all available therapeutic tools.

        Returns:
            List[Dict[str, Any]]: List of tool information
        """
        return [tool.get_tool_info() for tool in self.tools.values()]

    def process_therapeutic_request(self, tool_name: str, context: TherapeuticContext) -> TherapeuticResponse:
        """
        Process a therapeutic request using the specified tool.

        Args:
            tool_name: Name of the tool to use
            context: Therapeutic context information

        Returns:
            TherapeuticResponse: Response from the tool
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return TherapeuticResponse(
                tool_name=tool_name,
                response_type="error",
                content=f"Tool '{tool_name}' not found",
                confidence=0.0,
                metadata={"error": "tool_not_found"},
                therapeutic_value=0.0
            )

        # Process the request
        response = tool.process(context)

        # Update usage statistics
        self._update_usage_stats(tool_name, response)

        return response

    def _update_usage_stats(self, tool_name: str, response: TherapeuticResponse):
        """Update usage statistics for a tool."""
        if tool_name not in self.usage_stats:
            self.usage_stats[tool_name] = {
                "total_uses": 0,
                "success_count": 0,
                "average_confidence": 0.0,
                "average_therapeutic_value": 0.0
            }

        stats = self.usage_stats[tool_name]
        stats["total_uses"] += 1

        # Count as success if confidence > 0.5
        if response.confidence > 0.5:
            stats["success_count"] += 1

        # Update averages
        total_uses = stats["total_uses"]
        stats["average_confidence"] = (
            (stats["average_confidence"] * (total_uses - 1) + response.confidence) / total_uses
        )
        stats["average_therapeutic_value"] = (
            (stats["average_therapeutic_value"] * (total_uses - 1) + response.therapeutic_value) / total_uses
        )

    def get_usage_statistics(self) -> dict[str, dict[str, Any]]:
        """
        Get usage statistics for all tools.

        Returns:
            Dict[str, Dict[str, Any]]: Usage statistics by tool name
        """
        return self.usage_stats.copy()

    def get_tool_recommendations(self, context: TherapeuticContext) -> list[str]:
        """
        Get tool recommendations based on context.

        Args:
            context: Therapeutic context information

        Returns:
            List[str]: Recommended tool names
        """
        recommendations = []

        # Always recommend emotional state analysis first
        recommendations.append("emotional_state_analyzer")

        # Recommend coping strategies if emotional distress is detected
        emotional_keywords = ["anxious", "sad", "angry", "stressed", "overwhelmed", "depressed"]
        if any(keyword in context.current_emotional_state.lower() for keyword in emotional_keywords):
            recommendations.append("coping_strategy_generator")

        return recommendations


# Singleton instance
_THERAPEUTIC_TOOLS_MANAGER = None

def get_therapeutic_tools_manager() -> TherapeuticToolsManager:
    """
    Get the singleton instance of the TherapeuticToolsManager.

    Returns:
        TherapeuticToolsManager: Singleton instance
    """
    global _THERAPEUTIC_TOOLS_MANAGER
    if _THERAPEUTIC_TOOLS_MANAGER is None:
        _THERAPEUTIC_TOOLS_MANAGER = TherapeuticToolsManager()
    return _THERAPEUTIC_TOOLS_MANAGER
