"""
Therapeutic Dialogue System for TTA Prototype

This module implements the Character Management Agent for therapeutic dialogue consistency,
character-specific therapeutic intervention delivery, and character voice maintenance
during therapeutic moments.

Classes:
    CharacterManagementAgent: Main agent for character-driven therapeutic dialogue
    TherapeuticDialogueGenerator: Generates character-specific therapeutic content
    CharacterVoiceManager: Maintains character voice consistency
    TherapeuticInterventionDelivery: Delivers interventions through character personas
"""

import logging

# Import system components
import sys
from dataclasses import dataclass, field
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
    from character_development_system import CharacterDevelopmentSystem, Interaction
    from data_models import (
        CharacterState,
        DialogueContext,
        EmotionalState,
        InterventionType,
        TherapeuticOpportunity,
        ValidationError,
    )
    from relationship_evolution import RelationshipEvolutionEngine, RelationshipType
except ImportError:
    # Fallback for when running as part of package
    from ..models.data_models import (
        CharacterState,
        EmotionalState,
        InterventionType,
        ValidationError,
    )
    from .character_development_system import CharacterDevelopmentSystem, Interaction
    from .relationship_evolution import RelationshipEvolutionEngine

logger = logging.getLogger(__name__)


class DialogueType(Enum):
    """Types of therapeutic dialogue."""
    ASSESSMENT = "assessment"
    INTERVENTION = "intervention"
    SUPPORT = "support"
    CHALLENGE = "challenge"
    REFLECTION = "reflection"
    CRISIS = "crisis"
    CELEBRATION = "celebration"
    TRANSITION = "transition"


@dataclass
class TherapeuticDialogueRequest:
    """Request for therapeutic dialogue generation."""
    character_id: str
    dialogue_type: DialogueType
    therapeutic_context: dict[str, Any] = field(default_factory=dict)
    user_emotional_state: EmotionalState | None = None
    intervention_type: InterventionType | None = None
    specific_goals: list[str] = field(default_factory=list)
    relationship_context: dict[str, float] = field(default_factory=dict)
    narrative_context: str = ""
    urgency_level: float = 0.5  # 0.0 to 1.0

    def validate(self) -> bool:
        """Validate dialogue request."""
        if not self.character_id.strip():
            raise ValidationError("Character ID cannot be empty")
        if not 0.0 <= self.urgency_level <= 1.0:
            raise ValidationError("Urgency level must be between 0.0 and 1.0")
        return True


@dataclass
class TherapeuticDialogueResponse:
    """Response containing therapeutic dialogue."""
    character_id: str
    dialogue_content: str
    dialogue_type: DialogueType
    therapeutic_value: float = 0.0  # 0.0 to 1.0
    emotional_impact: float = 0.0  # -1.0 to 1.0
    character_consistency_score: float = 1.0  # 0.0 to 1.0
    intervention_delivered: InterventionType | None = None
    follow_up_suggestions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate dialogue response."""
        if not self.dialogue_content.strip():
            raise ValidationError("Dialogue content cannot be empty")
        if not 0.0 <= self.therapeutic_value <= 1.0:
            raise ValidationError("Therapeutic value must be between 0.0 and 1.0")
        if not -1.0 <= self.emotional_impact <= 1.0:
            raise ValidationError("Emotional impact must be between -1.0 and 1.0")
        if not 0.0 <= self.character_consistency_score <= 1.0:
            raise ValidationError("Character consistency score must be between 0.0 and 1.0")
        return True


class CharacterVoiceManager:
    """Manages character voice consistency across therapeutic interactions."""

    def __init__(self):
        self.voice_templates = self._initialize_voice_templates()
        self.therapeutic_adaptations = self._initialize_therapeutic_adaptations()

    def _initialize_voice_templates(self) -> dict[str, dict[str, list[str]]]:
        """Initialize character voice templates for different roles."""
        return {
            "therapist": {
                "formal_high": [
                    "I understand that this is a challenging situation for you.",
                    "Let's explore what this experience means to you.",
                    "I'd like to help you examine this from different perspectives.",
                    "What thoughts come to mind when you consider this?"
                ],
                "formal_medium": [
                    "That sounds really difficult to deal with.",
                    "I can see why that would be concerning for you.",
                    "Let's work together to understand this better.",
                    "How are you feeling about this situation?"
                ],
                "casual_high": [
                    "I hear you - that's really tough to go through.",
                    "It makes sense that you'd feel that way about this.",
                    "Let's figure out how to help you with this.",
                    "What's going through your mind right now?"
                ],
                "casual_medium": [
                    "That sounds really hard.",
                    "I can understand why you'd feel that way.",
                    "Let's talk about what might help.",
                    "How are you doing with all of this?"
                ]
            },
            "mentor": {
                "formal_high": [
                    "In my experience, situations like this often teach us valuable lessons.",
                    "Consider this an opportunity for growth and self-discovery.",
                    "I've seen many people overcome similar challenges successfully.",
                    "What wisdom might you gain from this experience?"
                ],
                "formal_medium": [
                    "I've been through something similar myself.",
                    "This kind of challenge can actually make you stronger.",
                    "Let me share what I've learned about situations like this.",
                    "What do you think you might learn from this?"
                ],
                "casual_high": [
                    "You know, I've been where you are before.",
                    "These tough times often lead to the biggest breakthroughs.",
                    "I remember when I faced something similar.",
                    "What do you think this experience is trying to teach you?"
                ],
                "casual_medium": [
                    "I get it - I've been there too.",
                    "Sometimes the hardest times teach us the most.",
                    "I went through something like this once.",
                    "What might you take away from this?"
                ]
            },
            "companion": {
                "formal_high": [
                    "I want you to know that you're not alone in this journey.",
                    "Your feelings are completely valid and understandable.",
                    "I'm here to support you through whatever comes next.",
                    "What would feel most helpful to you right now?"
                ],
                "formal_medium": [
                    "You don't have to go through this alone.",
                    "It's okay to feel the way you're feeling.",
                    "I'm here for you, whatever you need.",
                    "What kind of support would help you most?"
                ],
                "casual_high": [
                    "Hey, you've got this - and you've got me too.",
                    "It's totally normal to feel this way about everything.",
                    "I'm right here with you through all of this.",
                    "What would make you feel better right now?"
                ],
                "casual_medium": [
                    "You're not alone in this.",
                    "It's okay to feel however you're feeling.",
                    "I'm here for you.",
                    "What do you need right now?"
                ]
            }
        }

    def _initialize_therapeutic_adaptations(self) -> dict[InterventionType, dict[str, str]]:
        """Initialize therapeutic adaptations for different intervention types."""
        return {
            InterventionType.COGNITIVE_RESTRUCTURING: {
                "therapist": "Let's examine the thoughts behind these feelings and see if there might be other ways to look at this situation.",
                "mentor": "Sometimes our first thoughts about a situation aren't the whole story. What other perspectives might be worth considering?",
                "companion": "I wonder if there might be different ways to think about what happened. What feels true to you?"
            },
            InterventionType.MINDFULNESS: {
                "therapist": "Let's take a moment to ground ourselves in the present. Notice your breathing and the sensations in your body right now.",
                "mentor": "I've found that staying present in moments like these can be incredibly powerful. Try focusing on what you can sense around you.",
                "companion": "Want to try something with me? Let's just breathe together for a moment and notice what's happening right now."
            },
            InterventionType.EMOTIONAL_REGULATION: {
                "therapist": "These intense emotions are information. Let's explore what they're telling you and how you might work with them.",
                "mentor": "Strong emotions like these are part of being human. I've learned that acknowledging them is the first step to managing them.",
                "companion": "These feelings are really intense, aren't they? It's okay to feel them fully while also taking care of yourself."
            },
            InterventionType.COPING_SKILLS: {
                "therapist": "Let's identify some specific strategies that might help you navigate this situation more effectively.",
                "mentor": "Over the years, I've developed some approaches that might be helpful for you in situations like this.",
                "companion": "Let's think about what usually helps you feel better when things get tough like this."
            }
        }

    def generate_character_voice(self, character_state: CharacterState,
                                dialogue_content: str,
                                intervention_type: InterventionType | None = None) -> str:
        """Generate dialogue that maintains character voice consistency."""
        # Determine voice category
        role = character_state.therapeutic_role
        formality = character_state.dialogue_style.formality_level
        empathy = character_state.dialogue_style.empathy_level

        # Select appropriate voice template
        voice_key = self._get_voice_key(formality, empathy)
        self.voice_templates.get(role, {}).get(voice_key, [])

        # Apply therapeutic adaptation if needed
        if intervention_type and intervention_type in self.therapeutic_adaptations:
            adaptation = self.therapeutic_adaptations[intervention_type].get(role, "")
            if adaptation:
                # Blend the adaptation with the original content
                adapted_content = f"{adaptation} {dialogue_content}"
                return self._apply_character_style(adapted_content, character_state)

        # Apply character style to content
        return self._apply_character_style(dialogue_content, character_state)

    def _get_voice_key(self, formality: float, empathy: float) -> str:
        """Get voice template key based on character traits."""
        formality_level = "formal" if formality > 0.6 else "casual"
        empathy_level = "high" if empathy > 0.7 else "medium"
        return f"{formality_level}_{empathy_level}"

    def _apply_character_style(self, content: str, character_state: CharacterState) -> str:
        """Apply character-specific style modifications to dialogue."""
        style = character_state.dialogue_style

        # Apply formality adjustments
        if style.formality_level > 0.8:
            # Very formal - add professional language
            content = content.replace("you're", "you are")
            content = content.replace("can't", "cannot")
            content = content.replace("won't", "will not")
        elif style.formality_level < 0.3:
            # Very casual - add contractions and informal language
            content = content.replace("you are", "you're")
            content = content.replace("cannot", "can't")
            content = content.replace("will not", "won't")

        # Apply directness adjustments
        if style.directness < 0.3:
            # Indirect - add softening language
            if not any(phrase in content.lower() for phrase in ["perhaps", "maybe", "might", "could"]):
                content = f"Perhaps {content.lower()}"
        elif style.directness > 0.8:
            # Very direct - remove hedging language
            content = content.replace("perhaps ", "")
            content = content.replace("maybe ", "")
            content = content.replace("I think ", "")

        # Apply humor if appropriate
        if style.humor_usage > 0.6 and character_state.current_mood in ["cheerful", "content"]:
            # Add light humor where appropriate (simplified implementation)
            if "difficult" in content.lower():
                content += " Though I suppose we've both seen worse days, haven't we?"

        return content

    def validate_voice_consistency(self, character_state: CharacterState,
                                  dialogue_content: str,
                                  previous_dialogues: list[str] = None) -> tuple[float, list[str]]:
        """Validate that dialogue maintains character voice consistency."""
        issues = []
        consistency_score = 1.0

        # Check formality consistency
        formality_score = self._check_formality_consistency(
            dialogue_content, character_state.dialogue_style.formality_level
        )
        if formality_score < 0.7:
            issues.append(f"Formality inconsistency: expected {character_state.dialogue_style.formality_level:.2f}")
            consistency_score *= formality_score

        # Check empathy consistency
        empathy_score = self._check_empathy_consistency(
            dialogue_content, character_state.dialogue_style.empathy_level
        )
        if empathy_score < 0.7:
            issues.append(f"Empathy inconsistency: expected {character_state.dialogue_style.empathy_level:.2f}")
            consistency_score *= empathy_score

        # Check therapeutic role consistency
        role_score = self._check_role_consistency(
            dialogue_content, character_state.therapeutic_role
        )
        if role_score < 0.7:
            issues.append(f"Role inconsistency: expected {character_state.therapeutic_role}")
            consistency_score *= role_score

        return consistency_score, issues

    def _check_formality_consistency(self, dialogue: str, expected_formality: float) -> float:
        """Check formality consistency in dialogue."""
        formal_indicators = ["cannot", "will not", "shall", "would you", "I understand"]
        casual_indicators = ["can't", "won't", "gonna", "wanna", "yeah", "hey"]

        formal_count = sum(1 for indicator in formal_indicators if indicator in dialogue.lower())
        casual_count = sum(1 for indicator in casual_indicators if indicator in dialogue.lower())

        if expected_formality > 0.7:
            # Should be formal
            return 1.0 if formal_count >= casual_count else 0.5
        elif expected_formality < 0.3:
            # Should be casual
            return 1.0 if casual_count >= formal_count else 0.5
        else:
            # Mixed is okay
            return 1.0

    def _check_empathy_consistency(self, dialogue: str, expected_empathy: float) -> float:
        """Check empathy consistency in dialogue."""
        empathy_indicators = [
            "understand", "feel", "difficult", "challenging", "support",
            "here for you", "not alone", "valid", "okay to"
        ]

        empathy_count = sum(1 for indicator in empathy_indicators if indicator in dialogue.lower())

        if expected_empathy > 0.8:
            return 1.0 if empathy_count >= 2 else 0.6
        elif expected_empathy > 0.5:
            return 1.0 if empathy_count >= 1 else 0.8
        else:
            return 1.0  # Low empathy is harder to detect

    def _check_role_consistency(self, dialogue: str, role: str) -> float:
        """Check therapeutic role consistency in dialogue."""
        role_indicators = {
            "therapist": ["explore", "examine", "understand", "perspective", "thoughts", "feelings"],
            "mentor": ["experience", "learn", "grow", "wisdom", "journey", "overcome"],
            "companion": ["together", "support", "here", "not alone", "with you", "care"]
        }

        expected_indicators = role_indicators.get(role, [])
        if not expected_indicators:
            return 1.0

        indicator_count = sum(1 for indicator in expected_indicators if indicator in dialogue.lower())
        return 1.0 if indicator_count >= 1 else 0.7


class TherapeuticDialogueGenerator:
    """Generates character-specific therapeutic dialogue content."""

    def __init__(self):
        self.intervention_templates = self._initialize_intervention_templates()
        self.emotional_response_templates = self._initialize_emotional_response_templates()

    def _initialize_intervention_templates(self) -> dict[InterventionType, dict[str, list[str]]]:
        """Initialize templates for different therapeutic interventions."""
        return {
            InterventionType.COGNITIVE_RESTRUCTURING: {
                "introduction": [
                    "I notice you're having some strong thoughts about this situation.",
                    "Let's take a closer look at how you're thinking about what happened.",
                    "Sometimes our first thoughts about something aren't the complete picture."
                ],
                "exploration": [
                    "What evidence supports this thought? What evidence might challenge it?",
                    "If a good friend were in this exact situation, what would you tell them?",
                    "Are there other ways to interpret what happened?"
                ],
                "reframing": [
                    "What if we considered this from a different angle?",
                    "Here's another way to think about this situation.",
                    "Let's explore a more balanced perspective on this."
                ]
            },
            InterventionType.MINDFULNESS: {
                "introduction": [
                    "Let's take a moment to ground ourselves in the present.",
                    "I'd like to guide you through a brief mindfulness exercise.",
                    "Sometimes it helps to pause and notice what's happening right now."
                ],
                "guidance": [
                    "Notice your breathing - you don't need to change it, just observe it.",
                    "Feel your feet on the ground and your body in this space.",
                    "What do you notice around you right now? What can you see, hear, or feel?"
                ],
                "integration": [
                    "How does it feel to be present in this moment?",
                    "This is a skill you can use whenever you need to find your center.",
                    "Remember, you can always return to your breath as an anchor."
                ]
            },
            InterventionType.EMOTIONAL_REGULATION: {
                "validation": [
                    "These feelings you're experiencing are completely understandable.",
                    "It makes perfect sense that you would feel this way given what you've been through.",
                    "Your emotions are valid and they're giving you important information."
                ],
                "normalization": [
                    "Many people experience similar emotions in situations like this.",
                    "What you're feeling is a normal human response to a difficult situation.",
                    "These intense emotions show how much this situation matters to you."
                ],
                "coping": [
                    "Let's explore some ways to work with these feelings rather than against them.",
                    "What has helped you manage difficult emotions in the past?",
                    "There are some techniques that might help you navigate these feelings."
                ]
            },
            InterventionType.COPING_SKILLS: {
                "assessment": [
                    "What strategies have you used before when facing challenges like this?",
                    "Let's think about what resources and strengths you have available.",
                    "What has worked for you in similar situations in the past?"
                ],
                "skill_building": [
                    "Here's a technique that many people find helpful in situations like this.",
                    "Let me teach you a strategy that you can use whenever you need it.",
                    "This is a skill that gets stronger with practice."
                ],
                "practice": [
                    "Would you like to try this technique together right now?",
                    "Let's practice this so you'll feel confident using it on your own.",
                    "The more you use this skill, the more natural it will become."
                ]
            }
        }

    def _initialize_emotional_response_templates(self) -> dict[str, dict[str, list[str]]]:
        """Initialize templates for responding to different emotional states."""
        return {
            "anxious": {
                "acknowledgment": [
                    "I can see that you're feeling really anxious about this.",
                    "This anxiety you're experiencing is telling us something important.",
                    "I notice the worry in your voice - that must be exhausting."
                ],
                "support": [
                    "Anxiety can feel overwhelming, but you don't have to face it alone.",
                    "Let's work together to help you feel more grounded and secure.",
                    "There are ways to manage this anxiety that we can explore together."
                ]
            },
            "depressed": {
                "acknowledgment": [
                    "I can hear the heaviness in what you're sharing with me.",
                    "It sounds like you're carrying a lot of sadness right now.",
                    "This depression is clearly affecting many areas of your life."
                ],
                "support": [
                    "Even in this darkness, you're not alone - I'm here with you.",
                    "Small steps forward are still steps forward, even when everything feels heavy.",
                    "Your willingness to be here and talk about this shows incredible strength."
                ]
            },
            "angry": {
                "acknowledgment": [
                    "I can feel the intensity of your anger about this situation.",
                    "This anger is telling us that something important to you has been threatened.",
                    "Your frustration is completely understandable given what you've experienced."
                ],
                "support": [
                    "Let's find healthy ways to channel this energy and address what's bothering you.",
                    "Anger can be a powerful motivator for positive change when we work with it skillfully.",
                    "Your anger is valid - now let's figure out what to do with it constructively."
                ]
            }
        }

    def generate_therapeutic_dialogue(self, request: TherapeuticDialogueRequest,
                                    character_state: CharacterState) -> str:
        """Generate therapeutic dialogue based on request and character state."""
        dialogue_type = request.dialogue_type
        intervention_type = request.intervention_type

        # Start with base dialogue based on type
        if dialogue_type == DialogueType.INTERVENTION and intervention_type:
            base_dialogue = self._generate_intervention_dialogue(intervention_type, request)
        elif dialogue_type == DialogueType.SUPPORT:
            base_dialogue = self._generate_support_dialogue(request)
        elif dialogue_type == DialogueType.ASSESSMENT:
            base_dialogue = self._generate_assessment_dialogue(request)
        elif dialogue_type == DialogueType.REFLECTION:
            base_dialogue = self._generate_reflection_dialogue(request)
        elif dialogue_type == DialogueType.CRISIS:
            base_dialogue = self._generate_crisis_dialogue(request)
        else:
            base_dialogue = self._generate_general_dialogue(request)

        # Enhance with character-specific elements
        enhanced_dialogue = self._enhance_with_character_context(
            base_dialogue, character_state, request
        )

        return enhanced_dialogue

    def _generate_intervention_dialogue(self, intervention_type: InterventionType,
                                      request: TherapeuticDialogueRequest) -> str:
        """Generate dialogue for specific therapeutic interventions."""
        templates = self.intervention_templates.get(intervention_type, {})

        if not templates:
            return "Let's work together to address what you're experiencing."

        # Select appropriate template based on urgency and context
        if request.urgency_level > 0.7:
            # High urgency - direct approach
            if "guidance" in templates:
                return templates["guidance"][0]
            elif "coping" in templates:
                return templates["coping"][0]
        else:
            # Normal approach - start with introduction
            if "introduction" in templates:
                return templates["introduction"][0]

        # Fallback to first available template
        first_category = list(templates.keys())[0]
        return templates[first_category][0]

    def _generate_support_dialogue(self, request: TherapeuticDialogueRequest) -> str:
        """Generate supportive dialogue."""
        if request.user_emotional_state:
            emotion = request.user_emotional_state.primary_emotion.value
            templates = self.emotional_response_templates.get(emotion, {})

            if templates and "support" in templates:
                return templates["support"][0]

        # Generic support
        return "I want you to know that I'm here for you, and we'll work through this together."

    def _generate_assessment_dialogue(self, request: TherapeuticDialogueRequest) -> str:
        """Generate assessment dialogue."""
        assessment_questions = [
            "How are you feeling about everything that's been happening?",
            "What's been on your mind lately?",
            "Can you tell me more about what you're experiencing?",
            "What would be most helpful for us to focus on today?"
        ]

        # Select based on context
        if "anxiety" in request.narrative_context.lower():
            return "I'd like to understand more about the anxiety you've been experiencing. Can you describe what that feels like for you?"
        elif "relationship" in request.narrative_context.lower():
            return "Tell me about what's been happening in your relationships lately."
        else:
            return assessment_questions[0]

    def _generate_reflection_dialogue(self, request: TherapeuticDialogueRequest) -> str:
        """Generate reflective dialogue."""
        reflection_prompts = [
            "What insights are you gaining from this experience?",
            "How do you think you've grown through this process?",
            "What would you tell someone else who was going through something similar?",
            "What have you learned about yourself through this journey?"
        ]

        return reflection_prompts[0]

    def _generate_crisis_dialogue(self, request: TherapeuticDialogueRequest) -> str:
        """Generate crisis intervention dialogue."""
        return "I can see that you're in a lot of pain right now. Your safety and wellbeing are my primary concern. Let's focus on getting you the support you need."

    def _generate_general_dialogue(self, request: TherapeuticDialogueRequest) -> str:
        """Generate general therapeutic dialogue."""
        return "I'm here to listen and support you. What would be most helpful for us to talk about?"

    def _enhance_with_character_context(self, base_dialogue: str, character_state: CharacterState,
                                      request: TherapeuticDialogueRequest) -> str:
        """Enhance dialogue with character-specific context."""
        # Add character memories if relevant
        relevant_memories = [m for m in character_state.memory_fragments
                           if any(tag in request.narrative_context.lower()
                                 for tag in m.tags)]

        if relevant_memories and len(relevant_memories) > 0:
            memory = relevant_memories[0]  # Use most relevant memory
            if memory.emotional_weight > 0.5:
                base_dialogue += " I remember when we talked about something similar before, and I could see how much it meant to you."

        # Add relationship context
        if request.relationship_context:
            avg_relationship = sum(request.relationship_context.values()) / len(request.relationship_context)
            if avg_relationship > 0.6:
                base_dialogue += " I feel like we've built a good connection, and I hope you feel comfortable sharing with me."
            elif avg_relationship < -0.2:
                base_dialogue = "I know things have been difficult between us, but I want you to know that I'm committed to helping you. " + base_dialogue

        return base_dialogue


class TherapeuticInterventionDelivery:
    """Delivers therapeutic interventions through character personas."""

    def __init__(self):
        self.intervention_strategies = self._initialize_intervention_strategies()
        self.delivery_adaptations = self._initialize_delivery_adaptations()

    def _initialize_intervention_strategies(self) -> dict[str, dict[InterventionType, str]]:
        """Initialize intervention delivery strategies by character role."""
        return {
            "therapist": {
                InterventionType.COGNITIVE_RESTRUCTURING: "systematic_exploration",
                InterventionType.MINDFULNESS: "guided_practice",
                InterventionType.EMOTIONAL_REGULATION: "psychoeducation",
                InterventionType.COPING_SKILLS: "skill_teaching"
            },
            "mentor": {
                InterventionType.COGNITIVE_RESTRUCTURING: "wisdom_sharing",
                InterventionType.MINDFULNESS: "experiential_guidance",
                InterventionType.EMOTIONAL_REGULATION: "normalization",
                InterventionType.COPING_SKILLS: "experience_based"
            },
            "companion": {
                InterventionType.COGNITIVE_RESTRUCTURING: "gentle_questioning",
                InterventionType.MINDFULNESS: "collaborative_practice",
                InterventionType.EMOTIONAL_REGULATION: "emotional_support",
                InterventionType.COPING_SKILLS: "mutual_exploration"
            }
        }

    def _initialize_delivery_adaptations(self) -> dict[str, dict[str, str]]:
        """Initialize delivery adaptations for different strategies."""
        return {
            "systematic_exploration": {
                "introduction": "Let's systematically examine this situation together.",
                "process": "We'll look at the evidence, consider alternatives, and develop a more balanced perspective.",
                "conclusion": "This process of examining our thoughts is a skill you can use in many situations."
            },
            "wisdom_sharing": {
                "introduction": "In my experience, situations like this often have hidden lessons.",
                "process": "Let me share what I've learned about reframing difficult experiences.",
                "conclusion": "The wisdom you gain from this will serve you well in the future."
            },
            "gentle_questioning": {
                "introduction": "I wonder if we might look at this from a different angle together.",
                "process": "What do you think might be another way to see this situation?",
                "conclusion": "You have the wisdom within you to find new perspectives."
            }
        }

    def deliver_intervention(self, intervention_type: InterventionType,
                           character_state: CharacterState,
                           therapeutic_context: dict[str, Any]) -> TherapeuticDialogueResponse:
        """Deliver a therapeutic intervention through the character's persona."""
        role = character_state.therapeutic_role

        # Get intervention strategy for this character role
        strategies = self.intervention_strategies.get(role, {})
        strategy = strategies.get(intervention_type, "general_support")

        # Generate intervention dialogue
        dialogue_content = self._generate_intervention_content(
            intervention_type, strategy, character_state, therapeutic_context
        )

        # Calculate therapeutic value
        therapeutic_value = self._calculate_intervention_value(
            intervention_type, character_state, therapeutic_context
        )

        # Calculate emotional impact
        emotional_impact = self._calculate_emotional_impact(
            intervention_type, character_state, therapeutic_context
        )

        return TherapeuticDialogueResponse(
            character_id=character_state.character_id,
            dialogue_content=dialogue_content,
            dialogue_type=DialogueType.INTERVENTION,
            therapeutic_value=therapeutic_value,
            emotional_impact=emotional_impact,
            intervention_delivered=intervention_type,
            metadata={
                "strategy": strategy,
                "character_role": role,
                "intervention_type": intervention_type.value
            }
        )

    def _generate_intervention_content(self, intervention_type: InterventionType,
                                     strategy: str, character_state: CharacterState,
                                     therapeutic_context: dict[str, Any]) -> str:
        """Generate intervention content based on strategy and character."""
        adaptations = self.delivery_adaptations.get(strategy, {})

        if not adaptations:
            return self._generate_fallback_intervention(intervention_type, character_state)

        # Build intervention dialogue
        introduction = adaptations.get("introduction", "")
        process = adaptations.get("process", "")

        # Customize based on intervention type
        if intervention_type == InterventionType.MINDFULNESS:
            content = f"{introduction} {process} Let's start by taking three deep breaths together."
        elif intervention_type == InterventionType.COGNITIVE_RESTRUCTURING:
            content = f"{introduction} {process} What thoughts are going through your mind about this situation?"
        elif intervention_type == InterventionType.EMOTIONAL_REGULATION:
            content = f"{introduction} {process} These feelings you're experiencing are completely normal and manageable."
        else:
            content = f"{introduction} {process}"

        return content

    def _generate_fallback_intervention(self, intervention_type: InterventionType,
                                      character_state: CharacterState) -> str:
        """Generate fallback intervention content."""
        role = character_state.therapeutic_role

        if role == "therapist":
            return f"Let's work together on some {intervention_type.value.replace('_', ' ')} techniques that might be helpful for you."
        elif role == "mentor":
            return f"I'd like to share some insights about {intervention_type.value.replace('_', ' ')} that I've found valuable."
        else:
            return f"Let's explore some {intervention_type.value.replace('_', ' ')} approaches together."

    def _calculate_intervention_value(self, intervention_type: InterventionType,
                                    character_state: CharacterState,
                                    therapeutic_context: dict[str, Any]) -> float:
        """Calculate therapeutic value of the intervention."""
        base_value = 0.6  # Base therapeutic value

        # Adjust based on character empathy
        empathy_bonus = character_state.dialogue_style.empathy_level * 0.2

        # Adjust based on character role appropriateness
        role_bonus = 0.0
        if character_state.therapeutic_role == "therapist":
            role_bonus = 0.2
        elif character_state.therapeutic_role == "mentor":
            role_bonus = 0.15
        elif character_state.therapeutic_role == "companion":
            role_bonus = 0.1

        # Adjust based on intervention type appropriateness
        intervention_bonus = 0.0
        if intervention_type in [InterventionType.COGNITIVE_RESTRUCTURING, InterventionType.EMOTIONAL_REGULATION]:
            intervention_bonus = 0.1

        total_value = base_value + empathy_bonus + role_bonus + intervention_bonus
        return min(total_value, 1.0)

    def _calculate_emotional_impact(self, intervention_type: InterventionType,
                                  character_state: CharacterState,
                                  therapeutic_context: dict[str, Any]) -> float:
        """Calculate emotional impact of the intervention."""
        # Most therapeutic interventions have positive emotional impact
        base_impact = 0.3

        # Adjust based on character warmth and empathy
        empathy_impact = character_state.dialogue_style.empathy_level * 0.3

        # Adjust based on intervention type
        if intervention_type == InterventionType.MINDFULNESS:
            type_impact = 0.2  # Calming effect
        elif intervention_type == InterventionType.EMOTIONAL_REGULATION:
            type_impact = 0.4  # Strong positive impact
        elif intervention_type == InterventionType.COGNITIVE_RESTRUCTURING:
            type_impact = 0.1  # Can be challenging initially
        else:
            type_impact = 0.2

        total_impact = base_impact + empathy_impact + type_impact
        return min(total_impact, 1.0)


class CharacterManagementAgent:
    """Main agent for character-driven therapeutic dialogue consistency."""

    def __init__(self):
        self.character_system = CharacterDevelopmentSystem()
        self.relationship_engine = RelationshipEvolutionEngine()
        self.voice_manager = CharacterVoiceManager()
        self.dialogue_generator = TherapeuticDialogueGenerator()
        self.intervention_delivery = TherapeuticInterventionDelivery()

        logger.info("CharacterManagementAgent initialized")

    def generate_therapeutic_dialogue(self, request: TherapeuticDialogueRequest) -> TherapeuticDialogueResponse:
        """Generate therapeutic dialogue maintaining character consistency."""
        try:
            request.validate()

            # Get character state
            character_state = self.character_system.get_character_state(request.character_id)
            if not character_state:
                return self._generate_error_response(request, "Character not found")

            # Generate base dialogue content
            if request.dialogue_type == DialogueType.INTERVENTION and request.intervention_type:
                # Use intervention delivery system
                response = self.intervention_delivery.deliver_intervention(
                    request.intervention_type, character_state, request.therapeutic_context
                )
            else:
                # Use general dialogue generator
                dialogue_content = self.dialogue_generator.generate_therapeutic_dialogue(
                    request, character_state
                )

                response = TherapeuticDialogueResponse(
                    character_id=request.character_id,
                    dialogue_content=dialogue_content,
                    dialogue_type=request.dialogue_type,
                    therapeutic_value=0.5,  # Default value
                    emotional_impact=0.3    # Default value
                )

            # Apply character voice consistency
            response.dialogue_content = self.voice_manager.generate_character_voice(
                character_state, response.dialogue_content, request.intervention_type
            )

            # Validate voice consistency
            consistency_score, issues = self.voice_manager.validate_voice_consistency(
                character_state, response.dialogue_content
            )
            response.character_consistency_score = consistency_score

            if issues:
                response.metadata["consistency_issues"] = issues

            # Update character state based on interaction
            self._update_character_from_dialogue(character_state, request, response)

            response.validate()
            logger.info(f"Generated therapeutic dialogue for {request.character_id}")
            return response

        except Exception as e:
            logger.error(f"Error generating therapeutic dialogue: {e}")
            return self._generate_error_response(request, str(e))

    def _update_character_from_dialogue(self, character_state: CharacterState,
                                      request: TherapeuticDialogueRequest,
                                      response: TherapeuticDialogueResponse) -> None:
        """Update character state based on dialogue interaction."""
        # Create interaction record
        interaction = Interaction(
            participants=[request.character_id, "user"],
            interaction_type="therapeutic" if request.dialogue_type == DialogueType.INTERVENTION else "dialogue",
            content=response.dialogue_content[:100],  # Truncate for storage
            emotional_impact=response.emotional_impact,
            therapeutic_value=response.therapeutic_value
        )

        # Update character through development system
        self.character_system.update_character_from_interaction(request.character_id, interaction)

        # Update relationship if context provided
        if request.relationship_context:
            self.relationship_engine.update_relationship_from_interaction(
                request.character_id, "user", interaction
            )

    def _generate_error_response(self, request: TherapeuticDialogueRequest, error_message: str) -> TherapeuticDialogueResponse:
        """Generate error response for failed dialogue generation."""
        return TherapeuticDialogueResponse(
            character_id=request.character_id,
            dialogue_content="I'm here to support you, though I'm having some difficulty finding the right words right now.",
            dialogue_type=request.dialogue_type,
            therapeutic_value=0.2,
            emotional_impact=0.1,
            character_consistency_score=0.5,
            metadata={"error": error_message}
        )

    def get_character_dialogue_context(self, character_id: str, session_context: dict[str, Any]) -> dict[str, Any]:
        """Get comprehensive dialogue context for a character."""
        character_state = self.character_system.get_character_state(character_id)
        if not character_state:
            return {"error": "Character not found"}

        # Get character development summary
        development_summary = self.character_system.get_character_development_summary(character_id)

        # Get relationship analysis if user context provided
        relationship_analysis = {}
        if "user_id" in session_context:
            relationship_analysis = self.relationship_engine.get_relationship_analysis(
                character_id, session_context["user_id"]
            )

        return {
            "character_state": {
                "name": character_state.name,
                "therapeutic_role": character_state.therapeutic_role,
                "current_mood": character_state.current_mood,
                "personality_traits": character_state.personality_traits,
                "dialogue_style": {
                    "formality_level": character_state.dialogue_style.formality_level,
                    "empathy_level": character_state.dialogue_style.empathy_level,
                    "directness": character_state.dialogue_style.directness,
                    "therapeutic_approach": character_state.dialogue_style.therapeutic_approach
                }
            },
            "development_summary": development_summary,
            "relationship_analysis": relationship_analysis,
            "recent_memories": [
                {"content": m.content, "emotional_weight": m.emotional_weight}
                for m in character_state.memory_fragments[-3:]  # Last 3 memories
            ]
        }


# Utility functions for testing and validation
def create_test_therapeutic_dialogue_system() -> CharacterManagementAgent:
    """Create a test therapeutic dialogue system."""
    agent = CharacterManagementAgent()

    # Create test character
    agent.character_system.create_character(
        character_id="test_therapist",
        name="Dr. Sarah Thompson",
        personality_traits={
            "empathy": 0.9,
            "patience": 0.8,
            "wisdom": 0.7,
            "supportiveness": 0.9
        },
        therapeutic_role="therapist"
    )

    return agent


def validate_therapeutic_dialogue_system() -> bool:
    """Validate the therapeutic dialogue system functionality."""
    try:
        # Create system
        agent = create_test_therapeutic_dialogue_system()

        # Test dialogue generation
        request = TherapeuticDialogueRequest(
            character_id="test_therapist",
            dialogue_type=DialogueType.INTERVENTION,
            intervention_type=InterventionType.MINDFULNESS,
            narrative_context="User is feeling anxious about upcoming presentation"
        )

        response = agent.generate_therapeutic_dialogue(request)
        assert response.validate()
        assert response.therapeutic_value > 0.0
        assert response.character_consistency_score > 0.5

        # Test dialogue context
        context = agent.get_character_dialogue_context("test_therapist", {"user_id": "test_user"})
        assert "character_state" in context
        assert "development_summary" in context

        logger.info("Therapeutic dialogue system validation successful")
        return True

    except Exception as e:
        logger.error(f"Therapeutic dialogue system validation failed: {e}")
        return False


if __name__ == "__main__":
    # Run validation
    validate_therapeutic_dialogue_system()
