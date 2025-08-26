"""
Therapeutic Integration System for Core Gameplay Loop

This module provides natural therapeutic concept embedding, progress tracking,
and adaptive therapeutic approaches for meaningful therapeutic adventures.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from uuid import uuid4
import json

from src.components.gameplay_loop.services.session_state import SessionState
from src.components.gameplay_loop.models.core import UserChoice, ChoiceType, ConsequenceSet
from .events import EventBus, EventType, NarrativeEvent


logger = logging.getLogger(__name__)


class TherapeuticApproach(str, Enum):
    """Therapeutic approaches for concept integration."""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    DIALECTICAL_BEHAVIORAL = "dialectical_behavioral"
    MINDFULNESS_BASED = "mindfulness_based"
    ACCEPTANCE_COMMITMENT = "acceptance_commitment"
    NARRATIVE_THERAPY = "narrative_therapy"
    SOLUTION_FOCUSED = "solution_focused"
    HUMANISTIC = "humanistic"
    PSYCHODYNAMIC = "psychodynamic"


class IntegrationStrategy(str, Enum):
    """Strategies for therapeutic concept integration."""
    DIRECT_TEACHING = "direct_teaching"
    EXPERIENTIAL_LEARNING = "experiential_learning"
    METAPHORICAL_EMBEDDING = "metaphorical_embedding"
    SKILL_PRACTICE = "skill_practice"
    REFLECTION_PROMPTING = "reflection_prompting"
    MODELING_DEMONSTRATION = "modeling_demonstration"
    GRADUAL_EXPOSURE = "gradual_exposure"
    COLLABORATIVE_EXPLORATION = "collaborative_exploration"


class ProgressMilestone(str, Enum):
    """Types of therapeutic progress milestones."""
    SKILL_ACQUISITION = "skill_acquisition"
    INSIGHT_DEVELOPMENT = "insight_development"
    BEHAVIORAL_CHANGE = "behavioral_change"
    EMOTIONAL_REGULATION = "emotional_regulation"
    RELATIONSHIP_IMPROVEMENT = "relationship_improvement"
    GOAL_ACHIEVEMENT = "goal_achievement"
    RESILIENCE_BUILDING = "resilience_building"
    SELF_AWARENESS_GROWTH = "self_awareness_growth"


class ResistanceType(str, Enum):
    """Types of therapeutic resistance."""
    COGNITIVE_RESISTANCE = "cognitive_resistance"
    EMOTIONAL_AVOIDANCE = "emotional_avoidance"
    BEHAVIORAL_RELUCTANCE = "behavioral_reluctance"
    MOTIVATIONAL_AMBIVALENCE = "motivational_ambivalence"
    TRUST_ISSUES = "trust_issues"
    OVERWHELM_RESPONSE = "overwhelm_response"
    PERFECTIONISM = "perfectionism"
    LEARNED_HELPLESSNESS = "learned_helplessness"


@dataclass
class TherapeuticConcept:
    """Represents a therapeutic concept to be integrated."""
    concept_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    
    # Therapeutic framework
    approach: TherapeuticApproach = TherapeuticApproach.COGNITIVE_BEHAVIORAL
    core_principles: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    
    # Integration details
    integration_strategies: List[IntegrationStrategy] = field(default_factory=list)
    story_metaphors: List[str] = field(default_factory=list)
    practice_scenarios: List[str] = field(default_factory=list)
    
    # Prerequisites and dependencies
    prerequisite_concepts: List[str] = field(default_factory=list)
    difficulty_level: int = 1  # 1-10 scale
    estimated_sessions: int = 1
    
    # Assessment criteria
    mastery_indicators: List[str] = field(default_factory=list)
    progress_markers: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_practiced: Optional[datetime] = None
    mastery_level: float = 0.0  # 0.0-1.0


@dataclass
class TherapeuticProgress:
    """Tracks therapeutic progress for a user."""
    progress_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""
    
    # Progress tracking
    concept_id: str = ""
    concept_name: str = ""
    approach: TherapeuticApproach = TherapeuticApproach.COGNITIVE_BEHAVIORAL
    
    # Progress metrics
    initial_level: float = 0.0
    current_level: float = 0.0
    target_level: float = 1.0
    progress_rate: float = 0.0  # Progress per session
    
    # Practice tracking
    practice_sessions: int = 0
    successful_applications: int = 0
    total_attempts: int = 0
    
    # Milestone tracking
    milestones_achieved: List[ProgressMilestone] = field(default_factory=list)
    milestone_dates: Dict[str, datetime] = field(default_factory=dict)
    
    # Story integration
    story_contexts: List[str] = field(default_factory=list)
    character_developments: List[str] = field(default_factory=list)
    narrative_celebrations: List[str] = field(default_factory=list)
    
    # Metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None


@dataclass
class ResistancePattern:
    """Tracks patterns of therapeutic resistance."""
    pattern_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    
    # Resistance details
    resistance_type: ResistanceType = ResistanceType.COGNITIVE_RESISTANCE
    concept_areas: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    manifestations: List[str] = field(default_factory=list)
    
    # Pattern analysis
    frequency: int = 0
    intensity: float = 0.0  # 0.0-1.0
    duration_pattern: str = ""  # brief, moderate, extended
    
    # Adaptive responses
    successful_interventions: List[str] = field(default_factory=list)
    alternative_approaches: List[TherapeuticApproach] = field(default_factory=list)
    bypass_strategies: List[str] = field(default_factory=list)
    
    # Metadata
    first_observed: datetime = field(default_factory=datetime.utcnow)
    last_observed: datetime = field(default_factory=datetime.utcnow)
    resolution_status: str = "active"  # active, improving, resolved


@dataclass
class TherapeuticIntegration:
    """Represents a specific therapeutic integration in a story context."""
    integration_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    user_id: str = ""
    
    # Integration details
    concept_id: str = ""
    strategy: IntegrationStrategy = IntegrationStrategy.EXPERIENTIAL_LEARNING
    story_context: str = ""
    
    # Implementation
    narrative_embedding: str = ""
    character_involvement: List[str] = field(default_factory=list)
    practice_opportunities: List[str] = field(default_factory=list)
    
    # Feedback and assessment
    immediate_feedback: str = ""
    story_outcomes: List[str] = field(default_factory=list)
    character_reactions: List[str] = field(default_factory=list)
    
    # Effectiveness tracking
    user_engagement: float = 0.0  # 0.0-1.0
    concept_understanding: float = 0.0  # 0.0-1.0
    skill_demonstration: float = 0.0  # 0.0-1.0
    emotional_response: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    effectiveness_score: Optional[float] = None


class TherapeuticIntegrationSystem:
    """Main system for therapeutic concept integration and progress tracking."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Therapeutic concept library
        self.therapeutic_concepts: Dict[str, TherapeuticConcept] = {}
        self.concept_templates = self._load_concept_templates()
        
        # Progress tracking
        self.user_progress: Dict[str, List[TherapeuticProgress]] = {}
        self.resistance_patterns: Dict[str, List[ResistancePattern]] = {}
        self.integration_history: Dict[str, List[TherapeuticIntegration]] = {}
        
        # Integration strategies
        self.integration_strategies = self._load_integration_strategies()
        self.story_metaphors = self._load_story_metaphors()
        self.celebration_templates = self._load_celebration_templates()
        
        # Configuration
        self.progress_threshold = 0.8  # Threshold for milestone achievement
        self.resistance_detection_threshold = 3  # Number of failed attempts before detecting resistance
        self.adaptation_sensitivity = 0.7  # Sensitivity to user response for approach adaptation
        
        # Metrics
        self.metrics = {
            "concepts_integrated": 0,
            "progress_milestones_achieved": 0,
            "resistance_patterns_detected": 0,
            "adaptive_interventions": 0,
            "celebration_events": 0
        }
    
    def _load_concept_templates(self) -> Dict[TherapeuticApproach, List[Dict[str, Any]]]:
        """Load therapeutic concept templates for different approaches."""
        return {
            TherapeuticApproach.COGNITIVE_BEHAVIORAL: [
                {
                    "name": "Thought Challenging",
                    "description": "Learning to identify and challenge unhelpful thought patterns",
                    "core_principles": ["Thoughts affect feelings", "Evidence-based thinking", "Balanced perspective"],
                    "learning_objectives": ["Identify cognitive distortions", "Generate alternative thoughts", "Evaluate evidence"],
                    "story_metaphors": ["Detective investigating clues", "Scientist testing hypotheses", "Judge weighing evidence"],
                    "difficulty_level": 3
                },
                {
                    "name": "Behavioral Activation",
                    "description": "Increasing engagement in meaningful and rewarding activities",
                    "core_principles": ["Action leads to mood improvement", "Values-based living", "Gradual progress"],
                    "learning_objectives": ["Identify valued activities", "Schedule pleasant events", "Monitor mood changes"],
                    "story_metaphors": ["Hero embarking on quests", "Gardener tending plants", "Explorer discovering new lands"],
                    "difficulty_level": 2
                }
            ],
            TherapeuticApproach.MINDFULNESS_BASED: [
                {
                    "name": "Present Moment Awareness",
                    "description": "Developing ability to stay present and aware in the current moment",
                    "core_principles": ["Non-judgmental awareness", "Acceptance of present experience", "Observing without reacting"],
                    "learning_objectives": ["Practice mindful breathing", "Notice mind wandering", "Return attention to present"],
                    "story_metaphors": ["Wise sage observing nature", "Lighthouse keeper watching storms", "Mountain remaining steady"],
                    "difficulty_level": 2
                }
            ],
            TherapeuticApproach.DIALECTICAL_BEHAVIORAL: [
                {
                    "name": "Distress Tolerance",
                    "description": "Learning to tolerate and survive crisis situations without making them worse",
                    "core_principles": ["Distress is temporary", "Survival over solving", "Radical acceptance"],
                    "learning_objectives": ["Use TIPP skills", "Practice distraction techniques", "Accept difficult emotions"],
                    "story_metaphors": ["Sailor weathering storms", "Warrior enduring battles", "Tree bending in wind"],
                    "difficulty_level": 4
                }
            ]
        }
    
    def _load_integration_strategies(self) -> Dict[IntegrationStrategy, Dict[str, Any]]:
        """Load integration strategy configurations."""
        return {
            IntegrationStrategy.EXPERIENTIAL_LEARNING: {
                "description": "Learning through direct experience and practice in story scenarios",
                "implementation": "Create situations where users must apply therapeutic skills",
                "feedback_style": "Natural consequences and character reactions",
                "engagement_level": "high"
            },
            IntegrationStrategy.METAPHORICAL_EMBEDDING: {
                "description": "Using story metaphors to represent therapeutic concepts",
                "implementation": "Embed concepts in fantasy/adventure metaphors",
                "feedback_style": "Symbolic outcomes and metaphorical progress",
                "engagement_level": "medium"
            },
            IntegrationStrategy.SKILL_PRACTICE: {
                "description": "Direct practice of therapeutic skills in story context",
                "implementation": "Present clear skill practice opportunities",
                "feedback_style": "Explicit skill feedback and coaching",
                "engagement_level": "medium"
            },
            IntegrationStrategy.REFLECTION_PROMPTING: {
                "description": "Encouraging reflection on experiences and insights",
                "implementation": "Use character dialogue to prompt self-reflection",
                "feedback_style": "Validating insights and encouraging deeper thinking",
                "engagement_level": "low"
            }
        }
    
    def _load_story_metaphors(self) -> Dict[str, List[str]]:
        """Load story metaphors for different therapeutic concepts."""
        return {
            "emotional_regulation": [
                "Taming wild dragons (emotions) through understanding and patience",
                "Learning to navigate stormy seas with skill and wisdom",
                "Becoming a master gardener who tends to all plants (emotions) with care"
            ],
            "anxiety_management": [
                "Facing the shadow monsters that grow smaller when approached with courage",
                "Learning to be a lighthouse keeper who remains steady in all weather",
                "Becoming a skilled archer who breathes deeply before each shot"
            ],
            "depression_recovery": [
                "Climbing out of the deep cave with the help of inner light and companions",
                "Tending a garden back to life after a long winter",
                "Rebuilding a village with patience, one stone at a time"
            ]
        }
    
    def _load_celebration_templates(self) -> Dict[ProgressMilestone, List[str]]:
        """Load celebration templates for different milestone types."""
        return {
            ProgressMilestone.SKILL_ACQUISITION: [
                "The wise mentor acknowledges your growing mastery with a proud smile",
                "Your character gains a new ability that reflects your real-world skill development",
                "The community celebrates your newfound wisdom with a festival in your honor"
            ],
            ProgressMilestone.INSIGHT_DEVELOPMENT: [
                "A moment of clarity illuminates the path ahead like sunrise after a long night",
                "The ancient oracle nods approvingly as you demonstrate deep understanding",
                "Your character's eyes shine with newfound wisdom that others notice and admire"
            ],
            ProgressMilestone.BEHAVIORAL_CHANGE: [
                "Your actions inspire others in the story to follow your positive example",
                "The consequences of your new approach create ripples of positive change",
                "Your character becomes known for their transformed way of being in the world"
            ]
        }
    
    async def integrate_therapeutic_concept(self, session_state: SessionState,
                                          concept_id: str, story_context: str,
                                          strategy: IntegrationStrategy = IntegrationStrategy.EXPERIENTIAL_LEARNING) -> TherapeuticIntegration:
        """Integrate a therapeutic concept into the current story context."""
        try:
            # Get or create therapeutic concept
            concept = await self._get_or_create_concept(concept_id, session_state)
            
            # Create integration
            integration = TherapeuticIntegration(
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                concept_id=concept_id,
                strategy=strategy,
                story_context=story_context
            )
            
            # Generate narrative embedding
            integration.narrative_embedding = await self._generate_narrative_embedding(
                concept, strategy, story_context, session_state
            )
            
            # Create practice opportunities
            integration.practice_opportunities = await self._create_practice_opportunities(
                concept, strategy, story_context
            )
            
            # Generate immediate feedback framework
            integration.immediate_feedback = await self._generate_feedback_framework(
                concept, strategy
            )
            
            # Store integration
            user_id = session_state.user_id
            if user_id not in self.integration_history:
                self.integration_history[user_id] = []
            
            self.integration_history[user_id].append(integration)
            
            # Update session context
            session_state.context["current_therapeutic_integration"] = integration.integration_id
            session_state.context["therapeutic_concept_active"] = concept_id
            
            # Publish integration event
            await self._publish_integration_event(session_state, integration)
            
            self.metrics["concepts_integrated"] += 1
            
            return integration
            
        except Exception as e:
            logger.error(f"Failed to integrate therapeutic concept {concept_id} for user {session_state.user_id}: {e}")
            # Return minimal integration
            return TherapeuticIntegration(
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                concept_id=concept_id,
                strategy=strategy,
                story_context=story_context
            )

    async def _get_or_create_concept(self, concept_id: str, session_state: SessionState) -> TherapeuticConcept:
        """Get existing concept or create from template."""
        if concept_id in self.therapeutic_concepts:
            return self.therapeutic_concepts[concept_id]

        # Try to create from template based on therapeutic goals
        therapeutic_goals = session_state.therapeutic_goals
        user_approach = session_state.context.get("preferred_therapeutic_approach", TherapeuticApproach.COGNITIVE_BEHAVIORAL)

        # Find matching template
        if user_approach in self.concept_templates:
            templates = self.concept_templates[user_approach]

            # Match concept_id to template name or create generic
            for template in templates:
                if concept_id.lower() in template["name"].lower().replace(" ", "_"):
                    concept = TherapeuticConcept(
                        concept_id=concept_id,
                        name=template["name"],
                        description=template["description"],
                        approach=user_approach,
                        core_principles=template["core_principles"],
                        learning_objectives=template["learning_objectives"],
                        story_metaphors=template["story_metaphors"],
                        difficulty_level=template["difficulty_level"]
                    )

                    self.therapeutic_concepts[concept_id] = concept
                    return concept

        # Create generic concept if no template found
        concept = TherapeuticConcept(
            concept_id=concept_id,
            name=concept_id.replace("_", " ").title(),
            description=f"Therapeutic concept: {concept_id}",
            approach=user_approach
        )

        self.therapeutic_concepts[concept_id] = concept
        return concept

    async def _generate_narrative_embedding(self, concept: TherapeuticConcept,
                                          strategy: IntegrationStrategy,
                                          story_context: str,
                                          session_state: SessionState) -> str:
        """Generate narrative embedding for therapeutic concept."""
        strategy_config = self.integration_strategies[strategy]

        if strategy == IntegrationStrategy.METAPHORICAL_EMBEDDING:
            # Use story metaphors
            if concept.story_metaphors:
                metaphor = concept.story_metaphors[0]  # Use first metaphor
                return f"In this moment, you find yourself {metaphor.lower()}. {story_context}"

        elif strategy == IntegrationStrategy.EXPERIENTIAL_LEARNING:
            # Create experiential scenario
            return f"The situation before you presents an opportunity to practice {concept.name.lower()}. {story_context} How you respond will shape both the story and your own growth."

        elif strategy == IntegrationStrategy.SKILL_PRACTICE:
            # Direct skill practice
            return f"This is a perfect moment to apply the {concept.name} skills you've been developing. {story_context} Take a moment to consider which techniques might be most helpful here."

        elif strategy == IntegrationStrategy.REFLECTION_PROMPTING:
            # Encourage reflection
            return f"As you navigate this situation, you might notice connections to {concept.name}. {story_context} What insights arise as you consider your options?"

        # Default embedding
        return f"The current situation offers insights into {concept.name}. {story_context}"

    async def _create_practice_opportunities(self, concept: TherapeuticConcept,
                                           strategy: IntegrationStrategy,
                                           story_context: str) -> List[str]:
        """Create practice opportunities for the therapeutic concept."""
        opportunities = []

        # Base opportunities on learning objectives
        for objective in concept.learning_objectives:
            if strategy == IntegrationStrategy.EXPERIENTIAL_LEARNING:
                opportunities.append(f"Experience {objective.lower()} through story choices and consequences")
            elif strategy == IntegrationStrategy.SKILL_PRACTICE:
                opportunities.append(f"Practice {objective.lower()} in a safe story environment")
            elif strategy == IntegrationStrategy.REFLECTION_PROMPTING:
                opportunities.append(f"Reflect on how {objective.lower()} applies to your character's situation")

        # Add strategy-specific opportunities
        if strategy == IntegrationStrategy.METAPHORICAL_EMBEDDING:
            opportunities.append("Explore the metaphorical representation of the therapeutic concept")
        elif strategy == IntegrationStrategy.MODELING_DEMONSTRATION:
            opportunities.append("Observe how story characters model the therapeutic approach")
        elif strategy == IntegrationStrategy.COLLABORATIVE_EXPLORATION:
            opportunities.append("Work with story characters to explore different approaches")

        return opportunities[:3]  # Limit to 3 opportunities

    async def _generate_feedback_framework(self, concept: TherapeuticConcept,
                                         strategy: IntegrationStrategy) -> str:
        """Generate framework for providing immediate feedback."""
        strategy_config = self.integration_strategies[strategy]
        feedback_style = strategy_config["feedback_style"]

        if feedback_style == "Natural consequences and character reactions":
            return f"Story outcomes and character responses will reflect your application of {concept.name} principles"
        elif feedback_style == "Symbolic outcomes and metaphorical progress":
            return f"Metaphorical progress in the story will mirror your development in {concept.name}"
        elif feedback_style == "Explicit skill feedback and coaching":
            return f"Characters will provide direct feedback on your {concept.name} skill application"
        elif feedback_style == "Validating insights and encouraging deeper thinking":
            return f"Story characters will validate your insights about {concept.name} and encourage deeper exploration"

        return f"The story will provide feedback on your {concept.name} practice"

    async def _publish_integration_event(self, session_state: SessionState,
                                       integration: TherapeuticIntegration) -> None:
        """Publish therapeutic integration event."""
        event = NarrativeEvent(
            event_type=EventType.THERAPEUTIC_CONCEPT_INTEGRATED,
            session_id=session_state.session_id,
            user_id=session_state.user_id,
            context={
                "integration_id": integration.integration_id,
                "concept_id": integration.concept_id,
                "strategy": integration.strategy.value,
                "story_context": integration.story_context,
                "narrative_embedding": integration.narrative_embedding
            }
        )

        await self.event_bus.publish(event)

    async def track_therapeutic_progress(self, session_state: SessionState,
                                       concept_id: str, progress_data: Dict[str, Any]) -> TherapeuticProgress:
        """Track therapeutic progress for a specific concept."""
        try:
            user_id = session_state.user_id

            # Find existing progress or create new
            progress = None
            if user_id in self.user_progress:
                for p in self.user_progress[user_id]:
                    if p.concept_id == concept_id:
                        progress = p
                        break

            if not progress:
                # Create new progress tracking
                concept = await self._get_or_create_concept(concept_id, session_state)
                progress = TherapeuticProgress(
                    user_id=user_id,
                    session_id=session_state.session_id,
                    concept_id=concept_id,
                    concept_name=concept.name,
                    approach=concept.approach
                )

                if user_id not in self.user_progress:
                    self.user_progress[user_id] = []

                self.user_progress[user_id].append(progress)

            # Update progress metrics
            if "skill_demonstration" in progress_data:
                skill_level = progress_data["skill_demonstration"]
                progress.current_level = max(progress.current_level, skill_level)
                progress.progress_rate = (progress.current_level - progress.initial_level) / max(1, progress.practice_sessions)

            if "practice_attempt" in progress_data:
                progress.practice_sessions += 1
                progress.total_attempts += 1

                if progress_data.get("successful", False):
                    progress.successful_applications += 1

            # Check for milestone achievement
            await self._check_milestone_achievement(progress, session_state)

            # Update story integration
            if "story_context" in progress_data:
                progress.story_contexts.append(progress_data["story_context"])

            if "character_development" in progress_data:
                progress.character_developments.append(progress_data["character_development"])

            progress.last_updated = datetime.utcnow()

            # Publish progress event
            await self._publish_progress_event(session_state, progress)

            return progress

        except Exception as e:
            logger.error(f"Failed to track therapeutic progress for concept {concept_id}, user {session_state.user_id}: {e}")
            # Return minimal progress
            return TherapeuticProgress(
                user_id=session_state.user_id,
                session_id=session_state.session_id,
                concept_id=concept_id
            )

    async def _check_milestone_achievement(self, progress: TherapeuticProgress,
                                         session_state: SessionState) -> None:
        """Check if therapeutic milestones have been achieved."""
        milestones_achieved = []

        # Skill acquisition milestone
        if (progress.current_level >= self.progress_threshold and
            ProgressMilestone.SKILL_ACQUISITION not in progress.milestones_achieved):
            milestones_achieved.append(ProgressMilestone.SKILL_ACQUISITION)

        # Behavioral change milestone
        success_rate = progress.successful_applications / max(1, progress.total_attempts)
        if (success_rate >= 0.7 and progress.total_attempts >= 5 and
            ProgressMilestone.BEHAVIORAL_CHANGE not in progress.milestones_achieved):
            milestones_achieved.append(ProgressMilestone.BEHAVIORAL_CHANGE)

        # Insight development milestone
        if (len(progress.story_contexts) >= 3 and
            ProgressMilestone.INSIGHT_DEVELOPMENT not in progress.milestones_achieved):
            milestones_achieved.append(ProgressMilestone.INSIGHT_DEVELOPMENT)

        # Process achieved milestones
        for milestone in milestones_achieved:
            await self._celebrate_milestone(progress, milestone, session_state)
            progress.milestones_achieved.append(milestone)
            progress.milestone_dates[milestone.value] = datetime.utcnow()

            self.metrics["progress_milestones_achieved"] += 1

    async def _celebrate_milestone(self, progress: TherapeuticProgress,
                                 milestone: ProgressMilestone,
                                 session_state: SessionState) -> None:
        """Create celebration for achieved milestone."""
        try:
            # Get celebration template
            celebration_templates = self.celebration_templates.get(milestone, [
                "Your growth and progress are recognized and celebrated"
            ])

            celebration = celebration_templates[0]  # Use first template

            # Customize celebration
            celebration = celebration.replace("{concept}", progress.concept_name)
            celebration = celebration.replace("{milestone}", milestone.value.replace("_", " "))

            # Add to progress tracking
            progress.narrative_celebrations.append(celebration)

            # Update session context
            session_state.context["recent_milestone"] = {
                "type": milestone.value,
                "concept": progress.concept_name,
                "celebration": celebration,
                "achieved_at": datetime.utcnow().isoformat()
            }

            # Publish celebration event
            event = NarrativeEvent(
                event_type=EventType.MILESTONE_ACHIEVED,
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                context={
                    "milestone_type": milestone.value,
                    "concept_id": progress.concept_id,
                    "concept_name": progress.concept_name,
                    "celebration": celebration,
                    "progress_level": progress.current_level
                }
            )

            await self.event_bus.publish(event)

            self.metrics["celebration_events"] += 1

        except Exception as e:
            logger.error(f"Failed to celebrate milestone {milestone} for user {session_state.user_id}: {e}")

    async def _publish_progress_event(self, session_state: SessionState,
                                    progress: TherapeuticProgress) -> None:
        """Publish therapeutic progress event."""
        event = NarrativeEvent(
            event_type=EventType.THERAPEUTIC_PROGRESS_UPDATED,
            session_id=session_state.session_id,
            user_id=session_state.user_id,
            context={
                "progress_id": progress.progress_id,
                "concept_id": progress.concept_id,
                "concept_name": progress.concept_name,
                "current_level": progress.current_level,
                "progress_rate": progress.progress_rate,
                "milestones_achieved": [m.value for m in progress.milestones_achieved]
            }
        )

        await self.event_bus.publish(event)

    async def detect_therapeutic_resistance(self, session_state: SessionState,
                                          concept_id: str, interaction_data: Dict[str, Any]) -> Optional[ResistancePattern]:
        """Detect patterns of therapeutic resistance."""
        try:
            user_id = session_state.user_id

            # Check for resistance indicators
            resistance_indicators = []

            if interaction_data.get("engagement_level", 1.0) < 0.3:
                resistance_indicators.append("low_engagement")

            if interaction_data.get("skill_demonstration", 1.0) < 0.2:
                resistance_indicators.append("skill_avoidance")

            if interaction_data.get("emotional_response") == "frustrated":
                resistance_indicators.append("emotional_frustration")

            if interaction_data.get("choice_pattern") == "avoidant":
                resistance_indicators.append("avoidant_choices")

            # Check if resistance threshold is met
            if len(resistance_indicators) < 2:
                return None

            # Find existing resistance pattern or create new
            resistance_pattern = None
            if user_id in self.resistance_patterns:
                for pattern in self.resistance_patterns[user_id]:
                    if concept_id in pattern.concept_areas and pattern.resolution_status == "active":
                        resistance_pattern = pattern
                        break

            if not resistance_pattern:
                # Determine resistance type
                resistance_type = self._determine_resistance_type(resistance_indicators)

                resistance_pattern = ResistancePattern(
                    user_id=user_id,
                    resistance_type=resistance_type,
                    concept_areas=[concept_id],
                    triggers=resistance_indicators,
                    manifestations=resistance_indicators
                )

                if user_id not in self.resistance_patterns:
                    self.resistance_patterns[user_id] = []

                self.resistance_patterns[user_id].append(resistance_pattern)

                self.metrics["resistance_patterns_detected"] += 1
            else:
                # Update existing pattern
                resistance_pattern.frequency += 1
                resistance_pattern.last_observed = datetime.utcnow()
                resistance_pattern.manifestations.extend(resistance_indicators)

            # Trigger adaptive intervention
            await self._trigger_adaptive_intervention(resistance_pattern, session_state)

            return resistance_pattern

        except Exception as e:
            logger.error(f"Failed to detect therapeutic resistance for concept {concept_id}, user {session_state.user_id}: {e}")
            return None

    def _determine_resistance_type(self, indicators: List[str]) -> ResistanceType:
        """Determine the type of therapeutic resistance based on indicators."""
        if "emotional_frustration" in indicators:
            return ResistanceType.EMOTIONAL_AVOIDANCE
        elif "skill_avoidance" in indicators:
            return ResistanceType.BEHAVIORAL_RELUCTANCE
        elif "low_engagement" in indicators:
            return ResistanceType.MOTIVATIONAL_AMBIVALENCE
        elif "avoidant_choices" in indicators:
            return ResistanceType.COGNITIVE_RESISTANCE
        else:
            return ResistanceType.COGNITIVE_RESISTANCE  # Default

    async def _trigger_adaptive_intervention(self, resistance_pattern: ResistancePattern,
                                           session_state: SessionState) -> None:
        """Trigger adaptive intervention for therapeutic resistance."""
        try:
            # Determine intervention strategy based on resistance type
            intervention_strategies = {
                ResistanceType.COGNITIVE_RESISTANCE: [
                    "Provide alternative perspectives and gentle reframing",
                    "Use Socratic questioning to explore thoughts",
                    "Offer psychoeducation about the therapeutic process"
                ],
                ResistanceType.EMOTIONAL_AVOIDANCE: [
                    "Validate emotions and normalize the experience",
                    "Introduce grounding techniques and emotional regulation skills",
                    "Create safe spaces for emotional exploration"
                ],
                ResistanceType.BEHAVIORAL_RELUCTANCE: [
                    "Break down skills into smaller, manageable steps",
                    "Provide more scaffolding and support",
                    "Use behavioral experiments and gradual exposure"
                ],
                ResistanceType.MOTIVATIONAL_AMBIVALENCE: [
                    "Explore values and personal meaning",
                    "Use motivational interviewing techniques",
                    "Highlight discrepancies between values and current behavior"
                ]
            }

            strategies = intervention_strategies.get(resistance_pattern.resistance_type, [
                "Provide additional support and alternative approaches"
            ])

            # Update resistance pattern with successful interventions
            resistance_pattern.successful_interventions.extend(strategies)

            # Update session context
            session_state.context["therapeutic_resistance_detected"] = {
                "pattern_id": resistance_pattern.pattern_id,
                "resistance_type": resistance_pattern.resistance_type.value,
                "intervention_strategies": strategies,
                "detected_at": datetime.utcnow().isoformat()
            }

            # Publish resistance detection event
            event = NarrativeEvent(
                event_type=EventType.THERAPEUTIC_RESISTANCE_DETECTED,
                session_id=session_state.session_id,
                user_id=session_state.user_id,
                context={
                    "pattern_id": resistance_pattern.pattern_id,
                    "resistance_type": resistance_pattern.resistance_type.value,
                    "concept_areas": resistance_pattern.concept_areas,
                    "intervention_strategies": strategies
                }
            )

            await self.event_bus.publish(event)

            self.metrics["adaptive_interventions"] += 1

        except Exception as e:
            logger.error(f"Failed to trigger adaptive intervention for user {session_state.user_id}: {e}")

    async def provide_alternative_pathway(self, session_state: SessionState,
                                        concept_id: str, current_approach: TherapeuticApproach) -> Dict[str, Any]:
        """Provide alternative therapeutic pathway for resistant concepts."""
        try:
            # Get alternative approaches
            alternative_approaches = [
                approach for approach in TherapeuticApproach
                if approach != current_approach
            ]

            # Select best alternative based on user profile
            user_preferences = session_state.context.get("therapeutic_preferences", {})
            learning_style = user_preferences.get("learning_style", "balanced")

            # Match learning style to approach
            approach_mapping = {
                "visual": TherapeuticApproach.NARRATIVE_THERAPY,
                "experiential": TherapeuticApproach.ACCEPTANCE_COMMITMENT,
                "analytical": TherapeuticApproach.COGNITIVE_BEHAVIORAL,
                "emotional": TherapeuticApproach.HUMANISTIC,
                "practical": TherapeuticApproach.SOLUTION_FOCUSED,
                "mindful": TherapeuticApproach.MINDFULNESS_BASED
            }

            preferred_approach = approach_mapping.get(learning_style, TherapeuticApproach.COGNITIVE_BEHAVIORAL)

            if preferred_approach in alternative_approaches:
                selected_approach = preferred_approach
            else:
                selected_approach = alternative_approaches[0] if alternative_approaches else current_approach

            # Create alternative pathway
            pathway = {
                "alternative_approach": selected_approach.value,
                "integration_strategy": IntegrationStrategy.COLLABORATIVE_EXPLORATION.value,
                "story_adaptation": f"The story adapts to explore {concept_id} through {selected_approach.value} principles",
                "support_level": "high",
                "pacing": "gentle"
            }

            # Update session context
            session_state.context["alternative_pathway"] = pathway

            return pathway

        except Exception as e:
            logger.error(f"Failed to provide alternative pathway for concept {concept_id}, user {session_state.user_id}: {e}")
            return {
                "alternative_approach": current_approach.value,
                "integration_strategy": IntegrationStrategy.REFLECTION_PROMPTING.value,
                "story_adaptation": "The story provides gentle support and alternative perspectives",
                "support_level": "high",
                "pacing": "very_gentle"
            }

    def get_therapeutic_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive therapeutic progress summary for a user."""
        if user_id not in self.user_progress:
            return {"error": "No progress data available"}

        user_progress_list = self.user_progress[user_id]

        # Calculate overall metrics
        total_concepts = len(user_progress_list)
        total_milestones = sum(len(p.milestones_achieved) for p in user_progress_list)
        average_progress = sum(p.current_level for p in user_progress_list) / max(1, total_concepts)

        # Get recent progress
        recent_progress = [
            p for p in user_progress_list
            if p.last_updated > datetime.utcnow() - timedelta(days=7)
        ]

        # Get milestone achievements
        milestone_summary = {}
        for progress in user_progress_list:
            for milestone in progress.milestones_achieved:
                if milestone not in milestone_summary:
                    milestone_summary[milestone] = 0
                milestone_summary[milestone] += 1

        return {
            "user_id": user_id,
            "total_concepts": total_concepts,
            "total_milestones": total_milestones,
            "average_progress": average_progress,
            "recent_activity": len(recent_progress),
            "milestone_summary": {m.value: count for m, count in milestone_summary.items()},
            "concept_progress": [
                {
                    "concept_id": p.concept_id,
                    "concept_name": p.concept_name,
                    "current_level": p.current_level,
                    "progress_rate": p.progress_rate,
                    "milestones_achieved": [m.value for m in p.milestones_achieved],
                    "last_updated": p.last_updated.isoformat()
                }
                for p in user_progress_list
            ]
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get therapeutic integration system metrics."""
        return {
            **self.metrics,
            "total_concepts_loaded": len(self.therapeutic_concepts),
            "active_users_tracked": len(self.user_progress),
            "resistance_patterns_active": sum(
                len([p for p in patterns if p.resolution_status == "active"])
                for patterns in self.resistance_patterns.values()
            ),
            "integration_strategies_available": len(self.integration_strategies)
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of therapeutic integration system."""
        return {
            "status": "healthy",
            "concept_templates_loaded": sum(len(templates) for templates in self.concept_templates.values()),
            "integration_strategies_configured": len(self.integration_strategies),
            "story_metaphors_available": sum(len(metaphors) for metaphors in self.story_metaphors.values()),
            "celebration_templates_loaded": sum(len(templates) for templates in self.celebration_templates.values()),
            "progress_threshold": self.progress_threshold,
            "resistance_detection_threshold": self.resistance_detection_threshold,
            "metrics": self.get_metrics()
        }
