"""
Therapeutic Technique Demonstration System for TTA Prototype

This module implements narrative scenarios that demonstrate coping strategies and therapeutic
techniques through story events. It integrates therapeutic technique demonstrations with
narrative flow and provides reflection and learning opportunities.

Classes:
    TherapeuticTechniqueDemo: Main class for technique demonstration
    NarrativeScenarioGenerator: Creates scenarios that demonstrate techniques
    TechniqueIntegrator: Integrates techniques with story events
    ReflectionOpportunityGenerator: Creates learning and reflection moments
"""

import logging

# Import system components
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Add paths for imports
core_path = Path(__file__).parent
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from ..models.data_models import (
        CompletedIntervention,
        CopingStrategy,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        NarrativeContext,
        SessionState,
        TherapeuticGoal,
        TherapeuticProgress,
        ValidationError,
    )
    from ..models.therapeutic_llm_client import (
        SafetyLevel,
        TherapeuticContentType,
        TherapeuticContext,
        TherapeuticLLMClient,
        TherapeuticResponse,
    )
except ImportError:
    try:
        from data_models import (
            CompletedIntervention,
            CopingStrategy,
            EmotionalState,
            EmotionalStateType,
            InterventionType,
            NarrativeContext,
            SessionState,
            TherapeuticGoal,
            TherapeuticProgress,
            ValidationError,
        )
        from therapeutic_llm_client import (
            SafetyLevel,
            TherapeuticContentType,
            TherapeuticContext,
            TherapeuticLLMClient,
            TherapeuticResponse,
        )
    except ImportError:
        # Mock classes for testing
        logging.warning("Using mock implementations for missing dependencies")

        class MockTherapeuticLLMClient:
            def generate_therapeutic_content(self, context, content_type):
                return MockTherapeuticResponse()

        class MockTherapeuticResponse:
            def __init__(self):
                self.content = '{"scenario": {"title": "Mock Scenario"}}'
                self.therapeutic_value = 0.7
                self.confidence = 0.8
                self.metadata = {}

        TherapeuticLLMClient = MockTherapeuticLLMClient
        TherapeuticResponse = MockTherapeuticResponse

logger = logging.getLogger(__name__)


class TechniqueType(Enum):
    """Types of therapeutic techniques that can be demonstrated."""
    DEEP_BREATHING = "deep_breathing"
    PROGRESSIVE_MUSCLE_RELAXATION = "progressive_muscle_relaxation"
    GROUNDING_5_4_3_2_1 = "grounding_5_4_3_2_1"
    COGNITIVE_REFRAMING = "cognitive_reframing"
    THOUGHT_STOPPING = "thought_stopping"
    MINDFUL_OBSERVATION = "mindful_observation"
    BEHAVIORAL_ACTIVATION = "behavioral_activation"
    PROBLEM_SOLVING_STEPS = "problem_solving_steps"
    EMOTIONAL_REGULATION = "emotional_regulation"
    SELF_COMPASSION = "self_compassion"


class ScenarioType(Enum):
    """Types of narrative scenarios for technique demonstration."""
    GUIDED_PRACTICE = "guided_practice"
    CHARACTER_MODELING = "character_modeling"
    INTERACTIVE_CHALLENGE = "interactive_challenge"
    REFLECTION_MOMENT = "reflection_moment"
    SKILL_APPLICATION = "skill_application"


class LearningObjective(Enum):
    """Learning objectives for technique demonstrations."""
    TECHNIQUE_UNDERSTANDING = "technique_understanding"
    PRACTICAL_APPLICATION = "practical_application"
    EMOTIONAL_AWARENESS = "emotional_awareness"
    SKILL_GENERALIZATION = "skill_generalization"
    CONFIDENCE_BUILDING = "confidence_building"


@dataclass
class TechniqueStep:
    """Represents a step in a therapeutic technique."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int = 1
    instruction: str = ""
    narrative_description: str = ""
    character_guidance: str = ""
    user_action_required: bool = False
    expected_outcome: str = ""
    validation_criteria: list[str] = field(default_factory=list)

    def validate(self) -> bool:
        """Validate technique step data."""
        if not self.instruction.strip():
            raise ValidationError("Step instruction cannot be empty")
        if self.step_number <= 0:
            raise ValidationError("Step number must be positive")
        return True


@dataclass
class NarrativeScenario:
    """Represents a narrative scenario for technique demonstration."""
    scenario_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    scenario_type: ScenarioType = ScenarioType.GUIDED_PRACTICE
    technique_type: TechniqueType = TechniqueType.DEEP_BREATHING
    learning_objectives: list[LearningObjective] = field(default_factory=list)
    narrative_setup: str = ""
    character_role: str = ""
    technique_steps: list[TechniqueStep] = field(default_factory=list)
    reflection_prompts: list[str] = field(default_factory=list)
    success_indicators: list[str] = field(default_factory=list)
    estimated_duration: int = 10  # minutes
    difficulty_level: int = 1  # 1-5 scale
    prerequisites: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate narrative scenario data."""
        if not self.title.strip():
            raise ValidationError("Scenario title cannot be empty")
        if not self.description.strip():
            raise ValidationError("Scenario description cannot be empty")
        if not self.narrative_setup.strip():
            raise ValidationError("Narrative setup cannot be empty")
        if not 1 <= self.difficulty_level <= 5:
            raise ValidationError("Difficulty level must be between 1 and 5")
        if self.estimated_duration <= 0:
            raise ValidationError("Estimated duration must be positive")

        # Validate technique steps
        for step in self.technique_steps:
            step.validate()

        return True


@dataclass
class ReflectionOpportunity:
    """Represents a learning and reflection opportunity."""
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_event: str = ""
    reflection_type: str = "technique_application"
    guiding_questions: list[str] = field(default_factory=list)
    learning_points: list[str] = field(default_factory=list)
    narrative_integration: str = ""
    character_facilitation: str = ""
    expected_insights: list[str] = field(default_factory=list)
    follow_up_actions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate reflection opportunity data."""
        if not self.trigger_event.strip():
            raise ValidationError("Trigger event cannot be empty")
        if not self.guiding_questions:
            raise ValidationError("At least one guiding question is required")
        return True


class NarrativeScenarioGenerator:
    """Creates narrative scenarios that demonstrate therapeutic techniques."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the narrative scenario generator."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.technique_templates = self._initialize_technique_templates()
        self.scenario_templates = self._initialize_scenario_templates()
        logger.info("NarrativeScenarioGenerator initialized")

    def _initialize_technique_templates(self) -> dict[TechniqueType, dict[str, Any]]:
        """Initialize templates for different therapeutic techniques."""
        return {
            TechniqueType.DEEP_BREATHING: {
                "name": "Deep Breathing Exercise",
                "description": "A calming breathing technique to reduce anxiety and stress",
                "steps": [
                    "Find a comfortable position",
                    "Place one hand on chest, one on belly",
                    "Breathe in slowly through nose for 4 counts",
                    "Hold breath for 4 counts",
                    "Exhale slowly through mouth for 6 counts",
                    "Repeat 5-10 times"
                ],
                "narrative_context": "peaceful garden setting",
                "character_guidance": "gentle, encouraging coach",
                "expected_outcomes": ["reduced anxiety", "increased calm", "better focus"]
            },

            TechniqueType.GROUNDING_5_4_3_2_1: {
                "name": "5-4-3-2-1 Grounding Technique",
                "description": "A sensory grounding technique to manage overwhelming emotions",
                "steps": [
                    "Notice 5 things you can see",
                    "Notice 4 things you can touch",
                    "Notice 3 things you can hear",
                    "Notice 2 things you can smell",
                    "Notice 1 thing you can taste"
                ],
                "narrative_context": "detailed environment with rich sensory details",
                "character_guidance": "observant, mindful guide",
                "expected_outcomes": ["present moment awareness", "reduced overwhelm", "grounded feeling"]
            },

            TechniqueType.COGNITIVE_REFRAMING: {
                "name": "Cognitive Reframing",
                "description": "Challenging and changing negative thought patterns",
                "steps": [
                    "Identify the negative thought",
                    "Examine the evidence for and against",
                    "Consider alternative perspectives",
                    "Develop a more balanced thought",
                    "Practice the new thought pattern"
                ],
                "narrative_context": "challenging situation requiring perspective shift",
                "character_guidance": "wise, questioning mentor",
                "expected_outcomes": ["balanced thinking", "reduced negative emotions", "improved problem-solving"]
            }
        }

    def _initialize_scenario_templates(self) -> dict[ScenarioType, dict[str, Any]]:
        """Initialize templates for different scenario types."""
        return {
            ScenarioType.GUIDED_PRACTICE: {
                "structure": "step_by_step_guidance",
                "character_role": "supportive_instructor",
                "interaction_style": "collaborative",
                "pacing": "gentle_and_patient",
                "feedback_frequency": "after_each_step"
            },

            ScenarioType.CHARACTER_MODELING: {
                "structure": "demonstration_then_practice",
                "character_role": "experienced_practitioner",
                "interaction_style": "observational_learning",
                "pacing": "natural_demonstration",
                "feedback_frequency": "after_observation"
            },

            ScenarioType.INTERACTIVE_CHALLENGE: {
                "structure": "problem_solving_scenario",
                "character_role": "supportive_challenger",
                "interaction_style": "guided_discovery",
                "pacing": "adaptive_to_user",
                "feedback_frequency": "real_time_support"
            },

            ScenarioType.REFLECTION_MOMENT: {
                "structure": "contemplative_dialogue",
                "character_role": "reflective_companion",
                "interaction_style": "socratic_questioning",
                "pacing": "thoughtful_and_slow",
                "feedback_frequency": "after_reflection"
            }
        }

    def generate_technique_scenario(self, technique_type: TechniqueType,
                                  scenario_type: ScenarioType,
                                  context: NarrativeContext,
                                  user_needs: dict[str, Any]) -> NarrativeScenario:
        """
        Generate a narrative scenario for demonstrating a therapeutic technique.

        Args:
            technique_type: Type of therapeutic technique to demonstrate
            scenario_type: Type of narrative scenario to create
            context: Current narrative context
            user_needs: User's specific therapeutic needs and preferences

        Returns:
            NarrativeScenario: Generated scenario for technique demonstration
        """
        try:
            # Get technique and scenario templates
            technique_template = self.technique_templates.get(technique_type, {})
            scenario_template = self.scenario_templates.get(scenario_type, {})

            # Create technique steps
            technique_steps = self._create_technique_steps(technique_type, technique_template, context)

            # Generate narrative setup
            narrative_setup = self._generate_narrative_setup(
                technique_type, scenario_type, context, user_needs
            )

            # Create learning objectives
            learning_objectives = self._determine_learning_objectives(technique_type, user_needs)

            # Generate reflection prompts
            reflection_prompts = self._generate_reflection_prompts(technique_type, scenario_type)

            # Create the scenario
            scenario = NarrativeScenario(
                title=f"{technique_template.get('name', technique_type.value)} Practice",
                description=technique_template.get('description', ''),
                scenario_type=scenario_type,
                technique_type=technique_type,
                learning_objectives=learning_objectives,
                narrative_setup=narrative_setup,
                character_role=scenario_template.get('character_role', 'supportive_guide'),
                technique_steps=technique_steps,
                reflection_prompts=reflection_prompts,
                success_indicators=technique_template.get('expected_outcomes', []),
                estimated_duration=self._estimate_scenario_duration(technique_type, scenario_type),
                difficulty_level=self._assess_difficulty_level(technique_type, user_needs)
            )

            scenario.validate()
            return scenario

        except Exception as e:
            logger.error(f"Error generating technique scenario: {e}")
            return self._create_fallback_scenario(technique_type, scenario_type)

    def _create_technique_steps(self, technique_type: TechniqueType,
                              template: dict[str, Any],
                              context: NarrativeContext) -> list[TechniqueStep]:
        """Create detailed technique steps with narrative integration."""
        steps = []
        base_steps = template.get('steps', [])

        for i, step_instruction in enumerate(base_steps, 1):
            # Generate narrative description for this step
            narrative_desc = self._generate_step_narrative(
                step_instruction, technique_type, context, i
            )

            # Generate character guidance
            character_guidance = self._generate_character_guidance(
                step_instruction, technique_type, i
            )

            step = TechniqueStep(
                step_number=i,
                instruction=step_instruction,
                narrative_description=narrative_desc,
                character_guidance=character_guidance,
                user_action_required=self._requires_user_action(step_instruction),
                expected_outcome=self._determine_step_outcome(step_instruction, technique_type),
                validation_criteria=self._create_validation_criteria(step_instruction)
            )

            steps.append(step)

        return steps

    def _generate_narrative_setup(self, technique_type: TechniqueType,
                                scenario_type: ScenarioType,
                                context: NarrativeContext,
                                user_needs: dict[str, Any]) -> str:
        """Generate narrative setup for the technique demonstration."""
        technique_template = self.technique_templates.get(technique_type, {})
        narrative_context = technique_template.get('narrative_context', 'peaceful setting')

        # Base narrative elements
        setup_elements = {
            'location': context.current_location_id or 'tranquil_garden',
            'atmosphere': self._determine_atmosphere(technique_type),
            'character_presence': self._determine_character_presence(scenario_type),
            'user_state': user_needs.get('emotional_state', 'seeking_calm'),
            'technique_context': narrative_context
        }

        # Generate contextual setup based on scenario type
        if scenario_type == ScenarioType.GUIDED_PRACTICE:
            setup = f"""
            You find yourself in a {setup_elements['location']} with a {setup_elements['atmosphere']} atmosphere.
            Your companion notices your {setup_elements['user_state']} and gently suggests trying a helpful technique together.
            The setting feels safe and supportive, perfect for learning and practicing new skills.
            """

        elif scenario_type == ScenarioType.CHARACTER_MODELING:
            setup = f"""
            In the {setup_elements['location']}, you observe your companion who seems to naturally handle
            challenging situations with grace. As you watch, they begin to demonstrate a technique they use
            when feeling {setup_elements['user_state']}, inviting you to learn through observation.
            """

        elif scenario_type == ScenarioType.INTERACTIVE_CHALLENGE:
            setup = f"""
            A situation arises in the {setup_elements['location']} that mirrors your own challenges with
            {setup_elements['user_state']}. Your companion suggests this is a perfect opportunity to
            practice a helpful technique together, turning the challenge into a learning experience.
            """

        else:  # REFLECTION_MOMENT
            setup = f"""
            In the quiet {setup_elements['location']}, you and your companion pause to reflect on recent
            experiences. The peaceful {setup_elements['atmosphere']} creates space for deeper understanding
            and learning about managing {setup_elements['user_state']}.
            """

        return setup.strip()

    def _generate_step_narrative(self, instruction: str, technique_type: TechniqueType,
                               context: NarrativeContext, step_number: int) -> str:
        """Generate narrative description for a technique step."""
        # Create contextual narrative based on the instruction and technique type
        narrative_elements = {
            'environment': context.current_location_id or 'peaceful_space',
            'step_focus': instruction.lower(),
            'sensory_details': self._get_sensory_details(technique_type, step_number)
        }

        if 'breathe' in instruction.lower():
            return f"In this {narrative_elements['environment']}, you focus on your breath, feeling the natural rhythm of breathing as {narrative_elements['sensory_details']}."

        elif 'notice' in instruction.lower() or 'observe' in instruction.lower():
            return f"Your awareness expands in the {narrative_elements['environment']}, taking in the rich details around you as {narrative_elements['sensory_details']}."

        elif 'think' in instruction.lower() or 'consider' in instruction.lower():
            return f"In the contemplative atmosphere of the {narrative_elements['environment']}, you turn your attention inward, exploring your thoughts with curiosity."

        else:
            return f"Within the supportive space of the {narrative_elements['environment']}, you engage with this step, allowing yourself to fully experience the process."

    def _generate_character_guidance(self, instruction: str, technique_type: TechniqueType,
                                   step_number: int) -> str:
        """Generate character guidance for a technique step."""
        technique_template = self.technique_templates.get(technique_type, {})
        guidance_style = technique_template.get('character_guidance', 'supportive_guide')

        if 'gentle' in guidance_style:
            tone = "speaks softly and encouragingly"
        elif 'wise' in guidance_style:
            tone = "offers thoughtful insights"
        elif 'observant' in guidance_style:
            tone = "draws attention to important details"
        else:
            tone = "provides supportive guidance"

        return f"Your companion {tone}, saying: '{instruction}. Take your time with this step, and remember there's no wrong way to practice.'"

    def _requires_user_action(self, instruction: str) -> bool:
        """Determine if a step requires active user participation."""
        action_keywords = ['breathe', 'notice', 'place', 'hold', 'repeat', 'practice', 'try', 'do']
        return any(keyword in instruction.lower() for keyword in action_keywords)

    def _determine_step_outcome(self, instruction: str, technique_type: TechniqueType) -> str:
        """Determine expected outcome for a technique step."""
        if 'breathe' in instruction.lower():
            return "Increased sense of calm and centeredness"
        elif 'notice' in instruction.lower():
            return "Enhanced present-moment awareness"
        elif 'think' in instruction.lower() or 'consider' in instruction.lower():
            return "Greater cognitive clarity and perspective"
        else:
            return "Progress toward technique mastery"

    def _create_validation_criteria(self, instruction: str) -> list[str]:
        """Create validation criteria for a technique step."""
        criteria = ["User demonstrates understanding of the step"]

        if 'breathe' in instruction.lower():
            criteria.extend([
                "User follows breathing rhythm",
                "User reports feeling more relaxed"
            ])
        elif 'notice' in instruction.lower():
            criteria.extend([
                "User identifies sensory details",
                "User demonstrates present-moment focus"
            ])
        elif 'think' in instruction.lower():
            criteria.extend([
                "User engages in cognitive process",
                "User shows evidence of reflection"
            ])

        return criteria

    def _determine_learning_objectives(self, technique_type: TechniqueType,
                                     user_needs: dict[str, Any]) -> list[LearningObjective]:
        """Determine learning objectives based on technique and user needs."""
        objectives = [LearningObjective.TECHNIQUE_UNDERSTANDING]

        # Add objectives based on technique type
        if technique_type in [TechniqueType.DEEP_BREATHING, TechniqueType.GROUNDING_5_4_3_2_1]:
            objectives.append(LearningObjective.EMOTIONAL_AWARENESS)

        if technique_type == TechniqueType.COGNITIVE_REFRAMING:
            objectives.append(LearningObjective.PRACTICAL_APPLICATION)

        # Add objectives based on user needs
        if user_needs.get('confidence_level', 0.5) < 0.5:
            objectives.append(LearningObjective.CONFIDENCE_BUILDING)

        if user_needs.get('skill_transfer', False):
            objectives.append(LearningObjective.SKILL_GENERALIZATION)

        return objectives

    def _generate_reflection_prompts(self, technique_type: TechniqueType,
                                   scenario_type: ScenarioType) -> list[str]:
        """Generate reflection prompts for the technique demonstration."""
        base_prompts = [
            "How did this technique feel for you?",
            "What did you notice about your experience?",
            "Which part of the technique was most helpful?"
        ]

        # Add technique-specific prompts
        if technique_type == TechniqueType.DEEP_BREATHING:
            base_prompts.extend([
                "How did your breathing change during the exercise?",
                "What physical sensations did you notice?"
            ])

        elif technique_type == TechniqueType.GROUNDING_5_4_3_2_1:
            base_prompts.extend([
                "Which senses were easiest to focus on?",
                "How did your awareness of the present moment change?"
            ])

        elif technique_type == TechniqueType.COGNITIVE_REFRAMING:
            base_prompts.extend([
                "How did your perspective on the situation change?",
                "What alternative thoughts felt most believable?"
            ])

        # Add scenario-specific prompts
        if scenario_type == ScenarioType.CHARACTER_MODELING:
            base_prompts.append("What did you learn from observing the demonstration?")

        elif scenario_type == ScenarioType.INTERACTIVE_CHALLENGE:
            base_prompts.append("How might you apply this technique in similar situations?")

        return base_prompts

    def _estimate_scenario_duration(self, technique_type: TechniqueType,
                                  scenario_type: ScenarioType) -> int:
        """Estimate duration for scenario completion in minutes."""
        base_duration = {
            TechniqueType.DEEP_BREATHING: 8,
            TechniqueType.GROUNDING_5_4_3_2_1: 10,
            TechniqueType.COGNITIVE_REFRAMING: 15,
            TechniqueType.PROGRESSIVE_MUSCLE_RELAXATION: 20,
            TechniqueType.MINDFUL_OBSERVATION: 12
        }

        scenario_multiplier = {
            ScenarioType.GUIDED_PRACTICE: 1.0,
            ScenarioType.CHARACTER_MODELING: 1.2,
            ScenarioType.INTERACTIVE_CHALLENGE: 1.5,
            ScenarioType.REFLECTION_MOMENT: 0.8
        }

        base = base_duration.get(technique_type, 10)
        multiplier = scenario_multiplier.get(scenario_type, 1.0)

        return int(base * multiplier)

    def _assess_difficulty_level(self, technique_type: TechniqueType,
                               user_needs: dict[str, Any]) -> int:
        """Assess difficulty level (1-5) based on technique and user needs."""
        base_difficulty = {
            TechniqueType.DEEP_BREATHING: 1,
            TechniqueType.GROUNDING_5_4_3_2_1: 2,
            TechniqueType.MINDFUL_OBSERVATION: 2,
            TechniqueType.COGNITIVE_REFRAMING: 4,
            TechniqueType.PROBLEM_SOLVING_STEPS: 4,
            TechniqueType.PROGRESSIVE_MUSCLE_RELAXATION: 3
        }

        difficulty = base_difficulty.get(technique_type, 2)

        # Adjust based on user experience
        experience_level = user_needs.get('experience_level', 'beginner')
        if experience_level == 'advanced':
            difficulty = max(1, difficulty - 1)
        elif experience_level == 'beginner':
            difficulty = min(5, difficulty + 1)

        return difficulty

    def _determine_atmosphere(self, technique_type: TechniqueType) -> str:
        """Determine appropriate atmosphere for technique demonstration."""
        atmosphere_map = {
            TechniqueType.DEEP_BREATHING: "calm and serene",
            TechniqueType.GROUNDING_5_4_3_2_1: "rich with sensory details",
            TechniqueType.COGNITIVE_REFRAMING: "thoughtful and contemplative",
            TechniqueType.MINDFUL_OBSERVATION: "peaceful and focused",
            TechniqueType.PROGRESSIVE_MUSCLE_RELAXATION: "deeply relaxing"
        }
        return atmosphere_map.get(technique_type, "supportive and safe")

    def _determine_character_presence(self, scenario_type: ScenarioType) -> str:
        """Determine character presence style for scenario type."""
        presence_map = {
            ScenarioType.GUIDED_PRACTICE: "actively guiding and supportive",
            ScenarioType.CHARACTER_MODELING: "demonstrating with natural expertise",
            ScenarioType.INTERACTIVE_CHALLENGE: "encouraging and collaborative",
            ScenarioType.REFLECTION_MOMENT: "quietly present and attentive"
        }
        return presence_map.get(scenario_type, "supportive and present")

    def _get_sensory_details(self, technique_type: TechniqueType, step_number: int) -> str:
        """Get appropriate sensory details for technique and step."""
        if technique_type == TechniqueType.DEEP_BREATHING:
            details = [
                "cool air enters your nostrils",
                "your chest gently rises and falls",
                "warm breath flows out naturally",
                "your body settles into rhythm"
            ]
        elif technique_type == TechniqueType.GROUNDING_5_4_3_2_1:
            details = [
                "colors and shapes come into focus",
                "textures become apparent under your touch",
                "sounds layer and separate in your awareness",
                "subtle scents drift into your consciousness",
                "tastes linger gently on your tongue"
            ]
        else:
            details = [
                "awareness expands naturally",
                "focus deepens gradually",
                "understanding emerges clearly",
                "insight develops organically"
            ]

        # Return appropriate detail for step number
        return details[min(step_number - 1, len(details) - 1)]

    def _create_fallback_scenario(self, technique_type: TechniqueType,
                                scenario_type: ScenarioType) -> NarrativeScenario:
        """Create a fallback scenario when generation fails."""
        return NarrativeScenario(
            title=f"Basic {technique_type.value.replace('_', ' ').title()} Practice",
            description="A simple technique demonstration to help you learn and practice",
            scenario_type=scenario_type,
            technique_type=technique_type,
            learning_objectives=[LearningObjective.TECHNIQUE_UNDERSTANDING],
            narrative_setup="In a peaceful setting, you have the opportunity to learn and practice a helpful technique.",
            character_role="supportive_guide",
            technique_steps=[
                TechniqueStep(
                    step_number=1,
                    instruction="Follow along with the basic technique",
                    narrative_description="Your guide demonstrates the technique step by step",
                    character_guidance="Your companion says: 'Let's practice this together, one step at a time.'"
                )
            ],
            reflection_prompts=["How did this practice feel for you?"],
            success_indicators=["Completed technique practice"],
            estimated_duration=10,
            difficulty_level=2
        )


class TechniqueIntegrator:
    """Integrates therapeutic techniques with story events and narrative flow."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the technique integrator."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.integration_patterns = self._initialize_integration_patterns()
        logger.info("TechniqueIntegrator initialized")

    def _initialize_integration_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize patterns for integrating techniques with story events."""
        return {
            "natural_opportunity": {
                "description": "Technique emerges naturally from story situation",
                "integration_style": "organic",
                "character_approach": "suggests technique as natural response",
                "user_engagement": "voluntary participation"
            },

            "teaching_moment": {
                "description": "Character explicitly teaches technique",
                "integration_style": "educational",
                "character_approach": "takes instructor role",
                "user_engagement": "guided learning"
            },

            "crisis_response": {
                "description": "Technique used to address immediate need",
                "integration_style": "responsive",
                "character_approach": "provides immediate support",
                "user_engagement": "collaborative coping"
            },

            "skill_building": {
                "description": "Technique practiced for future use",
                "integration_style": "preparatory",
                "character_approach": "builds user capability",
                "user_engagement": "active skill development"
            }
        }

    def integrate_technique_with_story(self, scenario: NarrativeScenario,
                                     context: NarrativeContext,
                                     session_state: SessionState) -> dict[str, Any]:
        """
        Integrate a therapeutic technique demonstration with the current story.

        Args:
            scenario: Technique demonstration scenario
            context: Current narrative context
            session_state: Current session state

        Returns:
            Dict[str, Any]: Integration plan with narrative elements
        """
        try:
            # Determine integration approach
            integration_approach = self._select_integration_approach(scenario, context, session_state)

            # Create narrative transitions
            story_transitions = self._create_story_transitions(scenario, context, integration_approach)

            # Generate character interactions
            character_interactions = self._generate_character_interactions(scenario, integration_approach)

            # Create user choice points
            choice_points = self._create_choice_points(scenario, integration_approach)

            # Plan technique progression
            technique_progression = self._plan_technique_progression(scenario, context)

            integration_plan = {
                "integration_approach": integration_approach,
                "story_transitions": story_transitions,
                "character_interactions": character_interactions,
                "choice_points": choice_points,
                "technique_progression": technique_progression,
                "narrative_continuity": self._ensure_narrative_continuity(scenario, context),
                "success_metrics": self._define_success_metrics(scenario)
            }

            return integration_plan

        except Exception as e:
            logger.error(f"Error integrating technique with story: {e}")
            return self._create_fallback_integration(scenario, context)

    def _select_integration_approach(self, scenario: NarrativeScenario,
                                   context: NarrativeContext,
                                   session_state: SessionState) -> str:
        """Select the most appropriate integration approach."""
        # Consider user's emotional state
        if session_state.emotional_state and session_state.emotional_state.intensity > 0.7:
            return "crisis_response"

        # Consider scenario type
        if scenario.scenario_type == ScenarioType.GUIDED_PRACTICE:
            return "teaching_moment"
        elif scenario.scenario_type == ScenarioType.CHARACTER_MODELING:
            return "natural_opportunity"
        elif scenario.scenario_type == ScenarioType.INTERACTIVE_CHALLENGE:
            return "skill_building"

        # Default approach
        return "natural_opportunity"

    def _create_story_transitions(self, scenario: NarrativeScenario,
                                context: NarrativeContext,
                                approach: str) -> dict[str, str]:
        """Create smooth transitions between story and technique demonstration."""
        current_events = context.recent_events[-3:] if context.recent_events else []

        transitions = {
            "setup_transition": self._generate_setup_transition(scenario, current_events, approach),
            "technique_introduction": self._generate_technique_introduction(scenario, approach),
            "practice_transition": self._generate_practice_transition(scenario, approach),
            "completion_transition": self._generate_completion_transition(scenario, approach),
            "story_continuation": self._generate_story_continuation(scenario, context, approach)
        }

        return transitions

    def _generate_setup_transition(self, scenario: NarrativeScenario,
                                 recent_events: list[str],
                                 approach: str) -> str:
        """Generate transition from current story to technique setup."""
        if approach == "natural_opportunity":
            return f"As the events unfold around you, your companion notices an opportunity to share something helpful. The situation naturally leads to exploring {scenario.technique_type.value.replace('_', ' ')}."

        elif approach == "teaching_moment":
            return f"Your companion pauses thoughtfully, recognizing this as a perfect moment to teach you about {scenario.technique_type.value.replace('_', ' ')}. 'This might be helpful to learn,' they suggest gently."

        elif approach == "crisis_response":
            return f"Sensing your current state, your companion immediately offers support. 'Let's try something together that can help right now,' they say, introducing {scenario.technique_type.value.replace('_', ' ')}."

        else:  # skill_building
            return f"'This seems like a good time to practice a useful skill,' your companion suggests, preparing to guide you through {scenario.technique_type.value.replace('_', ' ')}."

    def _generate_technique_introduction(self, scenario: NarrativeScenario, approach: str) -> str:
        """Generate introduction to the technique within the story."""
        technique_name = scenario.technique_type.value.replace('_', ' ').title()

        if approach == "natural_opportunity":
            return f"'{technique_name} is something I've found helpful in situations like this,' your companion shares naturally."

        elif approach == "teaching_moment":
            return f"'Let me show you {technique_name},' your companion says, taking on the role of a gentle teacher."

        elif approach == "crisis_response":
            return f"'We can use {technique_name} to help you feel more grounded right now,' your companion offers with immediate support."

        else:  # skill_building
            return f"'Learning {technique_name} will give you a valuable tool for the future,' your companion explains encouragingly."

    def _generate_character_interactions(self, scenario: NarrativeScenario, approach: str) -> list[dict[str, str]]:
        """Generate character interactions throughout the technique demonstration."""
        interactions = []

        # Introduction interaction
        interactions.append({
            "type": "introduction",
            "character_dialogue": self._generate_technique_introduction(scenario, approach),
            "character_action": "settles into a supportive, teaching presence",
            "narrative_context": "creates a safe space for learning"
        })

        # Step-by-step interactions
        for i, step in enumerate(scenario.technique_steps, 1):
            interactions.append({
                "type": f"step_{i}_guidance",
                "character_dialogue": step.character_guidance,
                "character_action": f"demonstrates or guides step {i}",
                "narrative_context": step.narrative_description
            })

        # Completion interaction
        interactions.append({
            "type": "completion",
            "character_dialogue": "You did wonderfully. How are you feeling now?",
            "character_action": "offers warm encouragement and checks in",
            "narrative_context": "creates space for reflection and integration"
        })

        return interactions

    def _create_choice_points(self, scenario: NarrativeScenario, approach: str) -> list[dict[str, Any]]:
        """Create meaningful choice points during technique demonstration."""
        choice_points = []

        # Initial participation choice
        choice_points.append({
            "choice_id": f"participate_{scenario.scenario_id}",
            "prompt": "Your companion offers to guide you through this technique. How do you respond?",
            "options": [
                {"id": "eager", "text": "I'd like to try this", "consequence": "enthusiastic_participation"},
                {"id": "cautious", "text": "I'm willing but a bit nervous", "consequence": "gentle_encouragement"},
                {"id": "reluctant", "text": "I'm not sure about this", "consequence": "extra_support"}
            ],
            "narrative_impact": "affects character's approach and pacing"
        })

        # Mid-technique choice
        if len(scenario.technique_steps) > 3:
            len(scenario.technique_steps) // 2
            choice_points.append({
                "choice_id": f"midpoint_{scenario.scenario_id}",
                "prompt": f"You're partway through the {scenario.technique_type.value.replace('_', ' ')}. How are you finding it?",
                "options": [
                    {"id": "comfortable", "text": "This feels good, let's continue", "consequence": "maintain_pace"},
                    {"id": "challenging", "text": "This is harder than expected", "consequence": "slow_down"},
                    {"id": "easy", "text": "This seems easy, can we go deeper?", "consequence": "increase_depth"}
                ],
                "narrative_impact": "adjusts technique difficulty and pacing"
            })

        # Application choice
        choice_points.append({
            "choice_id": f"application_{scenario.scenario_id}",
            "prompt": "Now that you've learned this technique, when might you use it?",
            "options": [
                {"id": "immediate", "text": "I can see using this right away", "consequence": "immediate_application"},
                {"id": "future", "text": "I'll remember this for later", "consequence": "future_planning"},
                {"id": "uncertain", "text": "I'm not sure when I'd use it", "consequence": "exploration_needed"}
            ],
            "narrative_impact": "influences follow-up support and practice opportunities"
        })

        return choice_points

    def _plan_technique_progression(self, scenario: NarrativeScenario,
                                  context: NarrativeContext) -> dict[str, Any]:
        """Plan the progression through technique steps."""
        return {
            "total_steps": len(scenario.technique_steps),
            "estimated_time_per_step": scenario.estimated_duration // len(scenario.technique_steps) if scenario.technique_steps else 1,
            "pacing_strategy": self._determine_pacing_strategy(scenario),
            "adaptation_points": self._identify_adaptation_points(scenario),
            "success_checkpoints": self._create_success_checkpoints(scenario),
            "fallback_options": self._create_fallback_options(scenario)
        }

    def _determine_pacing_strategy(self, scenario: NarrativeScenario) -> str:
        """Determine appropriate pacing for technique demonstration."""
        if scenario.difficulty_level <= 2:
            return "gentle_and_patient"
        elif scenario.difficulty_level >= 4:
            return "careful_and_thorough"
        else:
            return "steady_and_supportive"

    def _identify_adaptation_points(self, scenario: NarrativeScenario) -> list[int]:
        """Identify points where technique can be adapted based on user response."""
        adaptation_points = [1]  # Always adapt after first step

        if len(scenario.technique_steps) > 4:
            adaptation_points.append(len(scenario.technique_steps) // 2)  # Mid-point

        adaptation_points.append(len(scenario.technique_steps))  # End point

        return adaptation_points

    def _create_success_checkpoints(self, scenario: NarrativeScenario) -> list[dict[str, str]]:
        """Create checkpoints to measure technique learning success."""
        checkpoints = []

        for i, step in enumerate(scenario.technique_steps, 1):
            checkpoints.append({
                "step": i,
                "checkpoint": f"User demonstrates understanding of step {i}",
                "validation": f"User can {step.instruction.lower()}",
                "success_indicator": step.expected_outcome
            })

        # Overall completion checkpoint
        checkpoints.append({
            "step": "completion",
            "checkpoint": "User completes full technique",
            "validation": "User can perform technique independently",
            "success_indicator": "Increased confidence and skill mastery"
        })

        return checkpoints

    def _create_fallback_options(self, scenario: NarrativeScenario) -> list[dict[str, str]]:
        """Create fallback options if technique demonstration encounters issues."""
        return [
            {
                "trigger": "user_overwhelm",
                "action": "simplify_technique",
                "description": "Reduce technique to core elements"
            },
            {
                "trigger": "user_disengagement",
                "action": "increase_interaction",
                "description": "Add more character interaction and encouragement"
            },
            {
                "trigger": "technique_difficulty",
                "action": "provide_alternatives",
                "description": "Offer simpler alternative techniques"
            },
            {
                "trigger": "time_constraints",
                "action": "focus_essentials",
                "description": "Focus on most important technique elements"
            }
        ]

    def _ensure_narrative_continuity(self, scenario: NarrativeScenario,
                                   context: NarrativeContext) -> dict[str, str]:
        """Ensure technique demonstration maintains narrative continuity."""
        return {
            "location_consistency": f"Technique demonstration occurs in {context.current_location_id}",
            "character_consistency": "Character maintains established personality while teaching",
            "story_thread_maintenance": "Current story threads are acknowledged and will continue",
            "world_state_preservation": "World state remains consistent during technique practice",
            "emotional_continuity": "User's emotional journey is honored throughout demonstration"
        }

    def _define_success_metrics(self, scenario: NarrativeScenario) -> dict[str, Any]:
        """Define metrics for measuring technique demonstration success."""
        return {
            "completion_rate": "Percentage of technique steps completed",
            "engagement_level": "User participation and interaction quality",
            "learning_indicators": scenario.success_indicators,
            "skill_demonstration": "User's ability to perform technique elements",
            "confidence_building": "User's expressed confidence in using technique",
            "narrative_integration": "How well technique fits into story flow",
            "therapeutic_value": "Perceived helpfulness and relevance"
        }

    def _generate_practice_transition(self, scenario: NarrativeScenario, approach: str) -> str:
        """Generate transition into technique practice."""
        if approach == "natural_opportunity":
            return "As you begin to practice together, the technique feels like a natural part of your journey."
        elif approach == "teaching_moment":
            return "Your companion guides you step by step, creating a supportive learning environment."
        elif approach == "crisis_response":
            return "Together, you begin the technique, focusing on immediate relief and support."
        else:  # skill_building
            return "You start practicing the technique, building skills for future challenges."

    def _generate_completion_transition(self, scenario: NarrativeScenario, approach: str) -> str:
        """Generate transition after technique completion."""
        return f"Having completed the {scenario.technique_type.value.replace('_', ' ')}, you feel a sense of accomplishment and new understanding."

    def _generate_story_continuation(self, scenario: NarrativeScenario,
                                   context: NarrativeContext, approach: str) -> str:
        """Generate continuation back to main story."""
        return "With this new skill in your toolkit, you're ready to continue your journey with greater confidence and capability."

    def _create_fallback_integration(self, scenario: NarrativeScenario,
                                   context: NarrativeContext) -> dict[str, Any]:
        """Create fallback integration plan when main integration fails."""
        return {
            "integration_approach": "simple_teaching",
            "story_transitions": {
                "setup_transition": "Your companion offers to teach you a helpful technique.",
                "technique_introduction": f"They introduce {scenario.technique_type.value.replace('_', ' ')}.",
                "practice_transition": "You practice together step by step.",
                "completion_transition": "You complete the technique successfully.",
                "story_continuation": "You continue your journey with new skills."
            },
            "character_interactions": [
                {
                    "type": "simple_guidance",
                    "character_dialogue": "Let me show you this helpful technique.",
                    "character_action": "provides basic guidance",
                    "narrative_context": "supportive learning environment"
                }
            ],
            "choice_points": [
                {
                    "choice_id": "basic_participation",
                    "prompt": "Would you like to try this technique?",
                    "options": [
                        {"id": "yes", "text": "Yes, I'd like to try", "consequence": "proceed"},
                        {"id": "no", "text": "Maybe later", "consequence": "defer"}
                    ]
                }
            ],
            "technique_progression": {
                "total_steps": len(scenario.technique_steps),
                "pacing_strategy": "gentle_and_patient",
                "success_checkpoints": ["basic_completion"]
            }
        }


class ReflectionOpportunityGenerator:
    """Creates learning and reflection opportunities after technique demonstrations."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the reflection opportunity generator."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.reflection_frameworks = self._initialize_reflection_frameworks()
        logger.info("ReflectionOpportunityGenerator initialized")

    def _initialize_reflection_frameworks(self) -> dict[str, dict[str, Any]]:
        """Initialize frameworks for different types of reflection."""
        return {
            "experiential_reflection": {
                "focus": "personal experience and feelings",
                "question_types": ["What did you notice?", "How did it feel?", "What surprised you?"],
                "depth_level": "surface_to_moderate",
                "character_role": "curious_companion"
            },

            "learning_integration": {
                "focus": "skill acquisition and understanding",
                "question_types": ["What did you learn?", "How might you use this?", "What was most helpful?"],
                "depth_level": "moderate",
                "character_role": "supportive_teacher"
            },

            "application_planning": {
                "focus": "future use and skill transfer",
                "question_types": ["When might you use this?", "How could you adapt it?", "What situations would benefit?"],
                "depth_level": "moderate_to_deep",
                "character_role": "strategic_guide"
            },

            "metacognitive_reflection": {
                "focus": "thinking about thinking and learning process",
                "question_types": ["How did you learn this?", "What helped you understand?", "How do you learn best?"],
                "depth_level": "deep",
                "character_role": "reflective_mentor"
            }
        }

    def generate_reflection_opportunity(self, scenario: NarrativeScenario,
                                      user_experience: dict[str, Any],
                                      context: NarrativeContext) -> ReflectionOpportunity:
        """
        Generate a reflection opportunity based on technique demonstration experience.

        Args:
            scenario: Completed technique demonstration scenario
            user_experience: User's experience data from the demonstration
            context: Current narrative context

        Returns:
            ReflectionOpportunity: Generated reflection opportunity
        """
        try:
            # Select appropriate reflection framework
            framework = self._select_reflection_framework(scenario, user_experience)

            # Generate guiding questions
            guiding_questions = self._generate_guiding_questions(scenario, framework, user_experience)

            # Identify learning points
            learning_points = self._identify_learning_points(scenario, user_experience)

            # Create narrative integration
            narrative_integration = self._create_narrative_integration(scenario, context, framework)

            # Generate character facilitation
            character_facilitation = self._generate_character_facilitation(framework, scenario)

            # Determine expected insights
            expected_insights = self._determine_expected_insights(scenario, user_experience)

            # Plan follow-up actions
            follow_up_actions = self._plan_follow_up_actions(scenario, user_experience)

            reflection_opportunity = ReflectionOpportunity(
                trigger_event=f"Completed {scenario.technique_type.value.replace('_', ' ')} demonstration",
                reflection_type=framework,
                guiding_questions=guiding_questions,
                learning_points=learning_points,
                narrative_integration=narrative_integration,
                character_facilitation=character_facilitation,
                expected_insights=expected_insights,
                follow_up_actions=follow_up_actions
            )

            reflection_opportunity.validate()
            return reflection_opportunity

        except Exception as e:
            logger.error(f"Error generating reflection opportunity: {e}")
            return self._create_fallback_reflection(scenario)

    def _select_reflection_framework(self, scenario: NarrativeScenario,
                                   user_experience: dict[str, Any]) -> str:
        """Select the most appropriate reflection framework."""
        # Consider user's engagement level
        user_experience.get('engagement_level', 'moderate')

        # Consider scenario complexity
        if scenario.difficulty_level <= 2:
            return "experiential_reflection"
        elif scenario.difficulty_level >= 4:
            return "metacognitive_reflection"

        # Consider user's experience with technique
        if user_experience.get('first_time', True):
            return "learning_integration"
        else:
            return "application_planning"

    def _generate_guiding_questions(self, scenario: NarrativeScenario,
                                  framework: str,
                                  user_experience: dict[str, Any]) -> list[str]:
        """Generate guiding questions for reflection."""
        framework_data = self.reflection_frameworks.get(framework, {})
        base_questions = framework_data.get("question_types", [])

        # Customize questions for specific technique
        technique_specific = self._get_technique_specific_questions(scenario.technique_type)

        # Customize based on user experience
        experience_specific = self._get_experience_specific_questions(user_experience)

        # Combine and prioritize questions
        all_questions = base_questions + technique_specific + experience_specific

        # Select most relevant questions (limit to 4-6)
        return self._prioritize_questions(all_questions, scenario, user_experience)[:6]

    def _get_technique_specific_questions(self, technique_type: TechniqueType) -> list[str]:
        """Get questions specific to the technique type."""
        technique_questions = {
            TechniqueType.DEEP_BREATHING: [
                "How did your breathing change during the exercise?",
                "What physical sensations did you notice?",
                "How might breathing exercises help you in daily life?"
            ],

            TechniqueType.GROUNDING_5_4_3_2_1: [
                "Which senses were easiest to focus on?",
                "How did your awareness of the present moment change?",
                "When might grounding techniques be most helpful for you?"
            ],

            TechniqueType.COGNITIVE_REFRAMING: [
                "How did your perspective on the situation change?",
                "What alternative thoughts felt most believable?",
                "How might you challenge negative thoughts in the future?"
            ],

            TechniqueType.MINDFUL_OBSERVATION: [
                "What did you notice that you hadn't seen before?",
                "How did focused attention change your experience?",
                "When might mindful observation be useful for you?"
            ]
        }

        return technique_questions.get(technique_type, [])

    def _get_experience_specific_questions(self, user_experience: dict[str, Any]) -> list[str]:
        """Get questions based on user's specific experience."""
        questions = []

        if user_experience.get('found_challenging', False):
            questions.extend([
                "What made this technique challenging for you?",
                "How did you work through the difficult parts?",
                "What would make it easier next time?"
            ])

        if user_experience.get('found_easy', False):
            questions.extend([
                "What made this technique feel natural for you?",
                "How might you build on this success?",
                "What other techniques might you be ready to try?"
            ])

        if user_experience.get('emotional_response', False):
            questions.extend([
                "What emotions came up during the practice?",
                "How did you handle those feelings?",
                "What did you learn about your emotional responses?"
            ])

        return questions

    def _prioritize_questions(self, questions: list[str],
                            scenario: NarrativeScenario,
                            user_experience: dict[str, Any]) -> list[str]:
        """Prioritize questions based on scenario and experience."""
        # Remove duplicates while preserving order
        unique_questions = []
        seen = set()
        for q in questions:
            if q not in seen:
                unique_questions.append(q)
                seen.add(q)

        # Prioritize based on learning objectives
        prioritized = []

        # Always include basic experience question
        experience_questions = [q for q in unique_questions if "feel" in q.lower() or "experience" in q.lower()]
        if experience_questions:
            prioritized.append(experience_questions[0])

        # Include technique-specific questions
        technique_questions = [q for q in unique_questions if scenario.technique_type.value.replace('_', ' ') in q.lower()]
        prioritized.extend(technique_questions[:2])

        # Include application questions
        application_questions = [q for q in unique_questions if "use" in q.lower() or "apply" in q.lower()]
        prioritized.extend(application_questions[:2])

        # Fill remaining slots with other questions
        remaining = [q for q in unique_questions if q not in prioritized]
        prioritized.extend(remaining[:6-len(prioritized)])

        return prioritized

    def _identify_learning_points(self, scenario: NarrativeScenario,
                                user_experience: dict[str, Any]) -> list[str]:
        """Identify key learning points from the technique demonstration."""
        learning_points = []

        # Core technique learning points
        learning_points.append(f"Learned the {scenario.technique_type.value.replace('_', ' ')} technique")
        learning_points.append("Experienced guided practice in a supportive environment")

        # Add points based on learning objectives
        for objective in scenario.learning_objectives:
            if objective == LearningObjective.TECHNIQUE_UNDERSTANDING:
                learning_points.append("Gained understanding of technique steps and purpose")
            elif objective == LearningObjective.PRACTICAL_APPLICATION:
                learning_points.append("Practiced applying technique in realistic context")
            elif objective == LearningObjective.EMOTIONAL_AWARENESS:
                learning_points.append("Increased awareness of emotional responses and regulation")
            elif objective == LearningObjective.CONFIDENCE_BUILDING:
                learning_points.append("Built confidence in ability to use coping techniques")

        # Add experience-specific learning points
        if user_experience.get('completed_all_steps', False):
            learning_points.append("Successfully completed all technique steps")

        if user_experience.get('adapted_technique', False):
            learning_points.append("Learned to adapt technique to personal needs")

        return learning_points[:5]  # Limit to most important points

    def _create_narrative_integration(self, scenario: NarrativeScenario,
                                    context: NarrativeContext,
                                    framework: str) -> str:
        """Create narrative integration for the reflection opportunity."""
        location = context.current_location_id or "peaceful_space"

        if framework == "experiential_reflection":
            return f"In the quiet of the {location}, you and your companion sit together, taking time to reflect on what you just experienced."

        elif framework == "learning_integration":
            return f"Your companion creates a thoughtful space in the {location} to help you process what you've learned and how it might serve you."

        elif framework == "application_planning":
            return f"Looking ahead from your position in the {location}, you and your companion explore how this new skill might fit into your life's journey."

        else:  # metacognitive_reflection
            return f"In the contemplative atmosphere of the {location}, your companion invites you to explore not just what you learned, but how you learned it."

    def _generate_character_facilitation(self, framework: str, scenario: NarrativeScenario) -> str:
        """Generate character facilitation approach for reflection."""
        framework_data = self.reflection_frameworks.get(framework, {})
        character_role = framework_data.get("character_role", "supportive_companion")

        if character_role == "curious_companion":
            return "Your companion asks questions with genuine curiosity, creating space for you to explore your experience without judgment."

        elif character_role == "supportive_teacher":
            return "Taking on a gentle teaching role, your companion helps you identify and integrate the learning from your practice."

        elif character_role == "strategic_guide":
            return "Your companion guides you in thinking strategically about how to apply your new skills in various life situations."

        else:  # reflective_mentor
            return "With the wisdom of a mentor, your companion helps you reflect deeply on your learning process and personal growth."

    def _determine_expected_insights(self, scenario: NarrativeScenario,
                                   user_experience: dict[str, Any]) -> list[str]:
        """Determine expected insights from reflection."""
        insights = []

        # Technique-specific insights
        if scenario.technique_type == TechniqueType.DEEP_BREATHING:
            insights.extend([
                "Understanding the connection between breath and emotional state",
                "Recognition of body's natural ability to self-regulate",
                "Awareness of how simple techniques can have powerful effects"
            ])

        elif scenario.technique_type == TechniqueType.GROUNDING_5_4_3_2_1:
            insights.extend([
                "Appreciation for the power of present-moment awareness",
                "Understanding how sensory focus can interrupt overwhelming thoughts",
                "Recognition of the richness of immediate experience"
            ])

        elif scenario.technique_type == TechniqueType.COGNITIVE_REFRAMING:
            insights.extend([
                "Awareness that thoughts are not facts",
                "Understanding the relationship between thoughts and emotions",
                "Recognition of personal power to change perspective"
            ])

        # Experience-based insights
        if user_experience.get('initial_skepticism', False):
            insights.append("Discovery that techniques can be more helpful than initially expected")

        if user_experience.get('found_challenging', False):
            insights.append("Understanding that skill development takes practice and patience")

        # General therapeutic insights
        insights.extend([
            "Recognition of personal capacity for growth and learning",
            "Understanding the value of guided practice and support",
            "Awareness of the importance of self-care and coping skills"
        ])

        return insights[:4]  # Limit to most relevant insights

    def _plan_follow_up_actions(self, scenario: NarrativeScenario,
                              user_experience: dict[str, Any]) -> list[str]:
        """Plan follow-up actions based on reflection."""
        actions = []

        # Always include practice recommendation
        actions.append(f"Practice the {scenario.technique_type.value.replace('_', ' ')} technique regularly")

        # Add technique-specific actions
        if scenario.technique_type == TechniqueType.DEEP_BREATHING:
            actions.extend([
                "Try breathing exercises during stressful moments",
                "Notice your natural breathing patterns throughout the day"
            ])

        elif scenario.technique_type == TechniqueType.GROUNDING_5_4_3_2_1:
            actions.extend([
                "Use grounding when feeling overwhelmed or anxious",
                "Practice mindful observation in different environments"
            ])

        elif scenario.technique_type == TechniqueType.COGNITIVE_REFRAMING:
            actions.extend([
                "Notice and question negative thought patterns",
                "Practice finding alternative perspectives in challenging situations"
            ])

        # Add experience-based actions
        if user_experience.get('wants_more_practice', False):
            actions.append("Seek additional opportunities to practice this technique")

        if user_experience.get('interested_in_similar', False):
            actions.append("Explore related techniques and coping strategies")

        # Add integration actions
        actions.extend([
            "Reflect on when this technique might be most helpful",
            "Share your learning with trusted friends or family if appropriate"
        ])

        return actions[:5]  # Limit to most actionable items

    def _create_fallback_reflection(self, scenario: NarrativeScenario) -> ReflectionOpportunity:
        """Create fallback reflection opportunity when generation fails."""
        return ReflectionOpportunity(
            trigger_event=f"Completed {scenario.technique_type.value.replace('_', ' ')} practice",
            reflection_type="basic_reflection",
            guiding_questions=[
                "How did that technique feel for you?",
                "What did you notice during the practice?",
                "When might you use this technique again?"
            ],
            learning_points=[
                "Practiced a new coping technique",
                "Experienced guided learning",
                "Gained a new tool for self-care"
            ],
            narrative_integration="You and your companion take a moment to reflect on the practice you just completed.",
            character_facilitation="Your companion asks gentle questions to help you process your experience.",
            expected_insights=[
                "Recognition of personal learning capacity",
                "Understanding the value of coping techniques"
            ],
            follow_up_actions=[
                "Practice the technique when needed",
                "Reflect on its helpfulness over time"
            ]
        )


class TherapeuticTechniqueDemo:
    """Main class for therapeutic technique demonstration system."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the therapeutic technique demonstration system."""
        self.scenario_generator = NarrativeScenarioGenerator(llm_client)
        self.technique_integrator = TechniqueIntegrator(llm_client)
        self.reflection_generator = ReflectionOpportunityGenerator(llm_client)
        self.llm_client = llm_client or TherapeuticLLMClient()

        logger.info("TherapeuticTechniqueDemo system initialized")

    def create_technique_demonstration(self, technique_type: TechniqueType,
                                     context: NarrativeContext,
                                     session_state: SessionState,
                                     user_preferences: dict[str, Any] = None) -> dict[str, Any]:
        """
        Create a complete therapeutic technique demonstration.

        Args:
            technique_type: Type of therapeutic technique to demonstrate
            context: Current narrative context
            session_state: Current session state
            user_preferences: User preferences for demonstration style

        Returns:
            Dict[str, Any]: Complete technique demonstration package
        """
        try:
            user_preferences = user_preferences or {}

            # Determine scenario type based on context and preferences
            scenario_type = self._determine_scenario_type(context, session_state, user_preferences)

            # Generate technique scenario
            scenario = self.scenario_generator.generate_technique_scenario(
                technique_type=technique_type,
                scenario_type=scenario_type,
                context=context,
                user_needs=self._extract_user_needs(session_state, user_preferences)
            )

            # Create integration plan
            integration_plan = self.technique_integrator.integrate_technique_with_story(
                scenario=scenario,
                context=context,
                session_state=session_state
            )

            # Prepare reflection opportunity template
            reflection_template = self._prepare_reflection_template(scenario, context)

            demonstration_package = {
                "scenario": scenario,
                "integration_plan": integration_plan,
                "reflection_template": reflection_template,
                "execution_guidance": self._create_execution_guidance(scenario, integration_plan),
                "success_metrics": self._define_demonstration_metrics(scenario),
                "adaptation_options": self._create_adaptation_options(scenario),
                "created_at": datetime.now().isoformat()
            }

            return demonstration_package

        except Exception as e:
            logger.error(f"Error creating technique demonstration: {e}")
            return self._create_fallback_demonstration(technique_type, context)

    def execute_technique_step(self, demonstration_package: dict[str, Any],
                             step_number: int,
                             user_response: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a specific step of the technique demonstration.

        Args:
            demonstration_package: Complete demonstration package
            step_number: Step number to execute (1-based)
            user_response: User's response to previous step

        Returns:
            Dict[str, Any]: Step execution results
        """
        try:
            scenario = demonstration_package["scenario"]
            integration_plan = demonstration_package["integration_plan"]

            if step_number > len(scenario.technique_steps):
                raise ValueError(f"Step {step_number} exceeds available steps ({len(scenario.technique_steps)})")

            current_step = scenario.technique_steps[step_number - 1]

            # Process user response from previous step
            if step_number > 1 and user_response:
                self._process_user_response(user_response, demonstration_package)

            # Execute current step
            step_execution = {
                "step_number": step_number,
                "step_instruction": current_step.instruction,
                "narrative_description": current_step.narrative_description,
                "character_guidance": current_step.character_guidance,
                "user_action_required": current_step.user_action_required,
                "expected_outcome": current_step.expected_outcome,
                "validation_criteria": current_step.validation_criteria,
                "character_interaction": self._get_character_interaction(integration_plan, step_number),
                "choice_points": self._get_step_choice_points(integration_plan, step_number),
                "adaptation_triggers": self._get_adaptation_triggers(current_step),
                "next_step_preview": self._get_next_step_preview(scenario, step_number)
            }

            return step_execution

        except Exception as e:
            logger.error(f"Error executing technique step: {e}")
            return self._create_fallback_step_execution(step_number)

    def generate_reflection_opportunity(self, demonstration_package: dict[str, Any],
                                      user_experience: dict[str, Any],
                                      context: NarrativeContext) -> ReflectionOpportunity:
        """
        Generate reflection opportunity after technique demonstration.

        Args:
            demonstration_package: Completed demonstration package
            user_experience: User's experience data
            context: Current narrative context

        Returns:
            ReflectionOpportunity: Generated reflection opportunity
        """
        scenario = demonstration_package["scenario"]
        return self.reflection_generator.generate_reflection_opportunity(
            scenario=scenario,
            user_experience=user_experience,
            context=context
        )

    def _determine_scenario_type(self, context: NarrativeContext,
                               session_state: SessionState,
                               user_preferences: dict[str, Any]) -> ScenarioType:
        """Determine the most appropriate scenario type."""
        # Check user preferences first
        preferred_style = user_preferences.get('learning_style', 'guided')

        if preferred_style == 'observational':
            return ScenarioType.CHARACTER_MODELING
        elif preferred_style == 'interactive':
            return ScenarioType.INTERACTIVE_CHALLENGE
        elif preferred_style == 'reflective':
            return ScenarioType.REFLECTION_MOMENT

        # Consider emotional state
        if session_state.emotional_state and session_state.emotional_state.intensity > 0.7:
            return ScenarioType.GUIDED_PRACTICE  # More supportive for high intensity

        # Default to guided practice
        return ScenarioType.GUIDED_PRACTICE

    def _extract_user_needs(self, session_state: SessionState,
                          user_preferences: dict[str, Any]) -> dict[str, Any]:
        """Extract user needs from session state and preferences."""
        needs = {
            'emotional_state': 'neutral',
            'experience_level': 'beginner',
            'confidence_level': 0.5,
            'skill_transfer': False
        }

        # Extract from session state
        if session_state.emotional_state:
            needs['emotional_state'] = session_state.emotional_state.primary_emotion.value
            needs['confidence_level'] = session_state.emotional_state.confidence_level

        # Extract from therapeutic progress
        if session_state.therapeutic_progress:
            completed_count = len(session_state.therapeutic_progress.completed_interventions)
            if completed_count > 5:
                needs['experience_level'] = 'intermediate'
            elif completed_count > 10:
                needs['experience_level'] = 'advanced'

        # Merge with user preferences
        needs.update(user_preferences)

        return needs

    def _prepare_reflection_template(self, scenario: NarrativeScenario,
                                   context: NarrativeContext) -> dict[str, Any]:
        """Prepare template for post-demonstration reflection."""
        return {
            "scenario_id": scenario.scenario_id,
            "technique_type": scenario.technique_type.value,
            "reflection_prompts": scenario.reflection_prompts,
            "learning_objectives": [obj.value for obj in scenario.learning_objectives],
            "success_indicators": scenario.success_indicators,
            "context_location": context.current_location_id
        }

    def _create_execution_guidance(self, scenario: NarrativeScenario,
                                 integration_plan: dict[str, Any]) -> dict[str, Any]:
        """Create guidance for executing the demonstration."""
        return {
            "total_steps": len(scenario.technique_steps),
            "estimated_duration": scenario.estimated_duration,
            "difficulty_level": scenario.difficulty_level,
            "pacing_strategy": integration_plan["technique_progression"]["pacing_strategy"],
            "adaptation_points": integration_plan["technique_progression"]["adaptation_points"],
            "success_checkpoints": integration_plan["technique_progression"]["success_checkpoints"],
            "character_role": scenario.character_role,
            "narrative_continuity": integration_plan["narrative_continuity"]
        }

    def _define_demonstration_metrics(self, scenario: NarrativeScenario) -> dict[str, Any]:
        """Define metrics for measuring demonstration success."""
        return {
            "completion_metrics": {
                "steps_completed": 0,
                "total_steps": len(scenario.technique_steps),
                "completion_percentage": 0.0
            },
            "engagement_metrics": {
                "user_participation": "not_measured",
                "question_responses": 0,
                "choice_interactions": 0
            },
            "learning_metrics": {
                "objectives_met": [],
                "skills_demonstrated": [],
                "confidence_indicators": []
            },
            "therapeutic_metrics": {
                "technique_understanding": "not_assessed",
                "practical_application": "not_assessed",
                "emotional_response": "not_assessed"
            }
        }

    def _create_adaptation_options(self, scenario: NarrativeScenario) -> list[dict[str, Any]]:
        """Create options for adapting the demonstration based on user response."""
        return [
            {
                "trigger": "user_struggling",
                "adaptation": "simplify_steps",
                "description": "Break down complex steps into smaller parts",
                "implementation": "Provide additional guidance and support"
            },
            {
                "trigger": "user_disengaged",
                "adaptation": "increase_interaction",
                "description": "Add more character interaction and user choices",
                "implementation": "Create additional dialogue and engagement points"
            },
            {
                "trigger": "user_advanced",
                "adaptation": "add_complexity",
                "description": "Introduce variations or advanced applications",
                "implementation": "Offer deeper exploration of technique principles"
            },
            {
                "trigger": "time_constraints",
                "adaptation": "focus_essentials",
                "description": "Focus on core technique elements",
                "implementation": "Prioritize most important steps and concepts"
            }
        ]

    def _process_user_response(self, user_response: dict[str, Any],
                             demonstration_package: dict[str, Any]) -> None:
        """Process user response and update demonstration state."""
        # Update metrics based on response
        metrics = demonstration_package.get("success_metrics", {})

        if "engagement_level" in user_response:
            metrics["engagement_metrics"]["user_participation"] = user_response["engagement_level"]

        if "questions_answered" in user_response:
            metrics["engagement_metrics"]["question_responses"] += user_response["questions_answered"]

        if "choices_made" in user_response:
            metrics["engagement_metrics"]["choice_interactions"] += user_response["choices_made"]

        # Update completion metrics
        if user_response.get("step_completed", False):
            metrics["completion_metrics"]["steps_completed"] += 1
            total_steps = metrics["completion_metrics"]["total_steps"]
            completed = metrics["completion_metrics"]["steps_completed"]
            metrics["completion_metrics"]["completion_percentage"] = (completed / total_steps) * 100

    def _get_character_interaction(self, integration_plan: dict[str, Any],
                                 step_number: int) -> dict[str, str]:
        """Get character interaction for specific step."""
        interactions = integration_plan.get("character_interactions", [])

        # Find interaction for this step
        for interaction in interactions:
            if f"step_{step_number}" in interaction.get("type", ""):
                return interaction

        # Return generic interaction if specific not found
        return {
            "type": f"step_{step_number}_guidance",
            "character_dialogue": "Let's continue with the next step of this technique.",
            "character_action": "provides supportive guidance",
            "narrative_context": "maintains supportive presence"
        }

    def _get_step_choice_points(self, integration_plan: dict[str, Any],
                              step_number: int) -> list[dict[str, Any]]:
        """Get choice points relevant to current step."""
        all_choice_points = integration_plan.get("choice_points", [])

        # Filter choice points relevant to current step
        relevant_choices = []
        for choice in all_choice_points:
            if f"step_{step_number}" in choice.get("choice_id", "") or choice.get("step_number") == step_number:
                relevant_choices.append(choice)

        return relevant_choices

    def _get_adaptation_triggers(self, current_step: TechniqueStep) -> list[str]:
        """Get adaptation triggers for current step."""
        triggers = ["user_confusion", "user_resistance", "user_overwhelm"]

        if current_step.user_action_required:
            triggers.append("user_inaction")

        if "breathe" in current_step.instruction.lower():
            triggers.append("breathing_difficulty")

        if "notice" in current_step.instruction.lower():
            triggers.append("attention_difficulty")

        return triggers

    def _get_next_step_preview(self, scenario: NarrativeScenario,
                             current_step_number: int) -> str | None:
        """Get preview of next step if available."""
        if current_step_number < len(scenario.technique_steps):
            next_step = scenario.technique_steps[current_step_number]
            return f"Next, we'll {next_step.instruction.lower()}"
        else:
            return "This completes the technique demonstration."

    def _create_fallback_step_execution(self, step_number: int) -> dict[str, Any]:
        """Create fallback step execution when main execution fails."""
        return {
            "step_number": step_number,
            "step_instruction": f"Continue with step {step_number} of the technique",
            "narrative_description": "Your companion guides you through this step with patience and support",
            "character_guidance": f"Your companion says: 'Let's work on step {step_number} together.'",
            "user_action_required": True,
            "expected_outcome": "Progress in technique learning",
            "validation_criteria": ["User attempts the step"],
            "character_interaction": {
                "type": "basic_guidance",
                "character_dialogue": "Take your time with this step.",
                "character_action": "provides basic support",
                "narrative_context": "supportive environment"
            },
            "choice_points": [],
            "adaptation_triggers": ["user_confusion"],
            "next_step_preview": "We'll continue with the next part of the technique."
        }

    def _create_fallback_demonstration(self, technique_type: TechniqueType,
                                     context: NarrativeContext) -> dict[str, Any]:
        """Create fallback demonstration when main creation fails."""
        fallback_scenario = NarrativeScenario(
            title=f"Basic {technique_type.value.replace('_', ' ').title()} Practice",
            description="A simple technique demonstration",
            technique_type=technique_type,
            narrative_setup="Your companion offers to teach you a helpful technique.",
            technique_steps=[
                TechniqueStep(
                    step_number=1,
                    instruction="Follow the basic technique steps",
                    narrative_description="Your companion demonstrates the technique",
                    character_guidance="Let's practice this together."
                )
            ],
            reflection_prompts=["How did this feel for you?"],
            estimated_duration=10
        )

        return {
            "scenario": fallback_scenario,
            "integration_plan": {
                "integration_approach": "simple_teaching",
                "story_transitions": {"setup_transition": "Your companion offers to teach you something helpful."},
                "character_interactions": [{"type": "basic_guidance", "character_dialogue": "Let's try this technique."}],
                "choice_points": [],
                "technique_progression": {"total_steps": 1, "pacing_strategy": "gentle"}
            },
            "reflection_template": {
                "technique_type": technique_type.value,
                "reflection_prompts": ["How did this feel?"]
            },
            "execution_guidance": {
                "total_steps": 1,
                "estimated_duration": 10,
                "difficulty_level": 1
            },
            "success_metrics": self._define_demonstration_metrics(fallback_scenario),
            "adaptation_options": [],
            "created_at": datetime.now().isoformat()
        }


# Export main classes and enums
__all__ = [
    'TherapeuticTechniqueDemo',
    'NarrativeScenarioGenerator',
    'TechniqueIntegrator',
    'ReflectionOpportunityGenerator',
    'TechniqueType',
    'ScenarioType',
    'LearningObjective',
    'NarrativeScenario',
    'TechniqueStep',
    'ReflectionOpportunity'
]
