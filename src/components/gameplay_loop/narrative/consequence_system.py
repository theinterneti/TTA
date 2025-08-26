"""
Consequence System for Therapeutic Narrative Engine

This module provides comprehensive consequence generation, learning opportunity framing,
and causality explanation for therapeutic text adventures.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from src.components.gameplay_loop.models.core import (
    UserChoice, ConsequenceSet, ConsequenceType, TherapeuticOutcome, ChoiceType
)
from src.components.gameplay_loop.services.session_state import SessionState
from .events import EventBus, EventType, create_consequence_event


logger = logging.getLogger(__name__)


class ConsequenceFraming(str, Enum):
    """How consequences are framed for therapeutic learning."""
    LEARNING_OPPORTUNITY = "learning_opportunity"
    NATURAL_OUTCOME = "natural_outcome"
    SKILL_PRACTICE = "skill_practice"
    GROWTH_MOMENT = "growth_moment"
    REFLECTION_PROMPT = "reflection_prompt"
    POSITIVE_REINFORCEMENT = "positive_reinforcement"


class ConsequenceSeverity(str, Enum):
    """Severity levels for consequences."""
    MINIMAL = "minimal"
    MILD = "mild"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    MAJOR = "major"


class LearningOpportunityType(str, Enum):
    """Types of learning opportunities from consequences."""
    EMOTIONAL_REGULATION = "emotional_regulation"
    COMMUNICATION_SKILLS = "communication_skills"
    PROBLEM_SOLVING = "problem_solving"
    SELF_AWARENESS = "self_awareness"
    RELATIONSHIP_BUILDING = "relationship_building"
    COPING_STRATEGIES = "coping_strategies"
    BOUNDARY_SETTING = "boundary_setting"
    CONFLICT_RESOLUTION = "conflict_resolution"


@dataclass
class ConsequencePattern:
    """Pattern of consequences from repeated choice types."""
    pattern_id: str = field(default_factory=lambda: str(uuid4()))
    choice_pattern: str = ""
    consequence_theme: str = ""
    frequency: int = 0
    therapeutic_significance: float = 0.0
    learning_opportunities: List[LearningOpportunityType] = field(default_factory=list)
    recommended_interventions: List[str] = field(default_factory=list)


@dataclass
class CausalityExplanation:
    """Explanation of causal relationships between choices and outcomes."""
    explanation_id: str = field(default_factory=lambda: str(uuid4()))
    choice_id: str = ""
    consequence_id: str = ""
    causal_chain: List[str] = field(default_factory=list)
    therapeutic_insight: str = ""
    learning_points: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ConsequenceGenerationContext:
    """Context for generating consequences."""
    choice: UserChoice
    session_state: SessionState
    previous_consequences: List[ConsequenceSet] = field(default_factory=list)
    therapeutic_goals: List[str] = field(default_factory=list)
    user_progress: Dict[str, float] = field(default_factory=dict)
    narrative_context: Dict[str, Any] = field(default_factory=dict)
    safety_constraints: List[str] = field(default_factory=list)


class ConsequenceSystem:
    """Main system for generating and managing consequences."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Consequence generation rules
        self.consequence_templates = self._load_consequence_templates()
        self.learning_frameworks = self._load_learning_frameworks()
        self.therapeutic_mappings = self._load_therapeutic_mappings()
        
        # Pattern tracking
        self.choice_patterns: Dict[str, ConsequencePattern] = {}
        self.causality_explanations: Dict[str, CausalityExplanation] = {}
        
        # Metrics
        self.metrics = {
            "consequences_generated": 0,
            "learning_opportunities_created": 0,
            "positive_reinforcements": 0,
            "pattern_recognitions": 0,
            "causality_explanations": 0
        }
    
    def _load_consequence_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load consequence generation templates."""
        return {
            # Positive choice consequences
            "positive_communication": {
                "immediate": [
                    "The person responds warmly to your honest communication",
                    "You feel a sense of relief after expressing yourself clearly",
                    "The conversation flows more naturally after your openness"
                ],
                "therapeutic_outcomes": [
                    {"skill": "communication", "improvement": 0.1},
                    {"skill": "self_expression", "improvement": 0.05}
                ],
                "learning_opportunities": [LearningOpportunityType.COMMUNICATION_SKILLS]
            },
            
            "healthy_boundary": {
                "immediate": [
                    "You feel empowered after setting a clear boundary",
                    "Others respect your decision and give you space",
                    "The situation becomes less stressful once you've established limits"
                ],
                "therapeutic_outcomes": [
                    {"skill": "boundary_setting", "improvement": 0.15},
                    {"skill": "self_advocacy", "improvement": 0.1}
                ],
                "learning_opportunities": [LearningOpportunityType.BOUNDARY_SETTING]
            },
            
            "emotional_regulation": {
                "immediate": [
                    "Taking a moment to breathe helps you feel more centered",
                    "You notice your emotions without being overwhelmed by them",
                    "The pause gives you clarity about what you really need"
                ],
                "therapeutic_outcomes": [
                    {"skill": "emotional_regulation", "improvement": 0.12},
                    {"skill": "mindfulness", "improvement": 0.08}
                ],
                "learning_opportunities": [LearningOpportunityType.EMOTIONAL_REGULATION]
            },
            
            # Challenging choice consequences (framed as learning)
            "avoidance_behavior": {
                "immediate": [
                    "The immediate relief of avoiding the situation feels good",
                    "However, you notice a lingering sense of unfinished business",
                    "The problem remains, and you realize it might grow if left unaddressed"
                ],
                "learning_framing": "This is a common response - avoidance can provide temporary relief but often prevents us from building confidence and problem-solving skills.",
                "therapeutic_outcomes": [
                    {"skill": "avoidance_awareness", "improvement": 0.05}
                ],
                "learning_opportunities": [LearningOpportunityType.PROBLEM_SOLVING, LearningOpportunityType.SELF_AWARENESS]
            },
            
            "reactive_response": {
                "immediate": [
                    "Your quick reaction feels justified in the moment",
                    "You notice the other person's surprise at your intensity",
                    "Afterward, you wonder if there might have been another way to respond"
                ],
                "learning_framing": "Strong emotions can lead to quick reactions. This is natural, and recognizing it is the first step toward developing more intentional responses.",
                "therapeutic_outcomes": [
                    {"skill": "emotional_awareness", "improvement": 0.08}
                ],
                "learning_opportunities": [LearningOpportunityType.EMOTIONAL_REGULATION, LearningOpportunityType.SELF_AWARENESS]
            }
        }
    
    def _load_learning_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Load therapeutic learning frameworks."""
        return {
            "cognitive_behavioral": {
                "focus": "thoughts_feelings_behaviors",
                "consequence_framing": "Notice how your thoughts influenced your feelings and actions",
                "learning_prompts": [
                    "What thoughts went through your mind before making this choice?",
                    "How did those thoughts affect how you felt?",
                    "What would you think differently next time?"
                ]
            },
            
            "dialectical_behavioral": {
                "focus": "distress_tolerance_emotion_regulation",
                "consequence_framing": "This situation offered a chance to practice emotional skills",
                "learning_prompts": [
                    "What emotions did you notice in this situation?",
                    "How did you cope with those emotions?",
                    "What skills could help you navigate similar situations?"
                ]
            },
            
            "mindfulness_based": {
                "focus": "present_moment_awareness",
                "consequence_framing": "Each moment offers an opportunity for awareness and choice",
                "learning_prompts": [
                    "What did you notice about your experience in this moment?",
                    "How present were you with your feelings and sensations?",
                    "What would mindful awareness look like in this situation?"
                ]
            }
        }
    
    def _load_therapeutic_mappings(self) -> Dict[str, List[str]]:
        """Load mappings between choice types and therapeutic goals."""
        return {
            "communication_choices": [
                "improve_communication_skills",
                "build_relationships",
                "increase_self_expression"
            ],
            "emotional_choices": [
                "emotional_regulation",
                "stress_management",
                "anxiety_reduction"
            ],
            "behavioral_choices": [
                "behavior_change",
                "habit_formation",
                "goal_achievement"
            ],
            "social_choices": [
                "social_skills",
                "relationship_building",
                "conflict_resolution"
            ]
        }
    
    async def generate_consequences(self, context: ConsequenceGenerationContext) -> ConsequenceSet:
        """Generate consequences for a user choice."""
        start_time = datetime.utcnow()
        
        try:
            # Analyze choice for consequence generation
            choice_analysis = await self._analyze_choice(context)
            
            # Generate immediate consequences
            immediate_consequences = await self._generate_immediate_consequences(
                context, choice_analysis
            )
            
            # Generate therapeutic outcomes
            therapeutic_outcomes = await self._generate_therapeutic_outcomes(
                context, choice_analysis
            )
            
            # Create learning opportunities
            learning_opportunities = await self._create_learning_opportunities(
                context, choice_analysis
            )
            
            # Frame consequences therapeutically
            framed_consequences = await self._frame_consequences_therapeutically(
                immediate_consequences, context, choice_analysis
            )
            
            # Create consequence set
            consequence_set = ConsequenceSet(
                choice_id=context.choice.choice_id,
                consequences=framed_consequences,
                consequence_type=self._determine_consequence_type(choice_analysis),
                therapeutic_outcomes=therapeutic_outcomes,
                learning_opportunities=learning_opportunities,
                narrative_impact=choice_analysis.get("narrative_impact", {}),
                character_changes=choice_analysis.get("character_changes", {}),
                emotional_impact=choice_analysis.get("emotional_impact", {}),
                created_at=datetime.utcnow()
            )
            
            # Update patterns and metrics
            await self._update_choice_patterns(context, consequence_set)
            self.metrics["consequences_generated"] += 1
            self.metrics["learning_opportunities_created"] += len(learning_opportunities)
            
            # Publish consequence event
            await self._publish_consequence_event(context, consequence_set)
            
            processing_time = datetime.utcnow() - start_time
            logger.debug(f"Generated consequences for choice {context.choice.choice_id} in {processing_time.total_seconds():.3f}s")
            
            return consequence_set
            
        except Exception as e:
            logger.error(f"Failed to generate consequences for choice {context.choice.choice_id}: {e}")
            # Return minimal consequence set
            return ConsequenceSet(
                choice_id=context.choice.choice_id,
                consequences=[{"type": "error", "description": "Unable to generate consequences"}],
                consequence_type=ConsequenceType.IMMEDIATE
            )
    
    async def _analyze_choice(self, context: ConsequenceGenerationContext) -> Dict[str, Any]:
        """Analyze choice for consequence generation."""
        choice = context.choice
        
        analysis = {
            "choice_type": choice.choice_type,
            "therapeutic_relevance": choice.therapeutic_relevance,
            "emotional_weight": choice.emotional_weight,
            "difficulty_level": choice.difficulty_level,
            "alignment_with_goals": 0.0,
            "pattern_match": None,
            "consequence_severity": ConsequenceSeverity.MILD,
            "framing_approach": ConsequenceFraming.NATURAL_OUTCOME
        }
        
        # Analyze alignment with therapeutic goals
        if context.therapeutic_goals:
            alignment_scores = []
            for goal in context.therapeutic_goals:
                # Simple keyword matching - could be enhanced with NLP
                choice_text = choice.text.lower()
                if any(keyword in choice_text for keyword in self._get_goal_keywords(goal)):
                    alignment_scores.append(0.8)
                else:
                    alignment_scores.append(0.2)
            analysis["alignment_with_goals"] = sum(alignment_scores) / len(alignment_scores)
        
        # Determine consequence severity
        if choice.emotional_weight > 0.7:
            analysis["consequence_severity"] = ConsequenceSeverity.SIGNIFICANT
        elif choice.emotional_weight > 0.5:
            analysis["consequence_severity"] = ConsequenceSeverity.MODERATE
        else:
            analysis["consequence_severity"] = ConsequenceSeverity.MILD
        
        # Determine framing approach
        if analysis["alignment_with_goals"] > 0.6:
            analysis["framing_approach"] = ConsequenceFraming.POSITIVE_REINFORCEMENT
        elif choice.therapeutic_relevance > 0.5:
            analysis["framing_approach"] = ConsequenceFraming.LEARNING_OPPORTUNITY
        else:
            analysis["framing_approach"] = ConsequenceFraming.NATURAL_OUTCOME
        
        return analysis
    
    def _get_goal_keywords(self, goal: str) -> List[str]:
        """Get keywords associated with therapeutic goals."""
        goal_keywords = {
            "anxiety_management": ["calm", "breathe", "relax", "worry", "anxiety"],
            "depression_support": ["mood", "energy", "hope", "positive", "motivation"],
            "communication_skills": ["talk", "express", "listen", "communicate", "share"],
            "emotional_regulation": ["feel", "emotion", "control", "manage", "cope"],
            "relationship_building": ["friend", "connect", "relationship", "trust", "support"],
            "self_esteem": ["confident", "worth", "value", "proud", "capable"],
            "stress_management": ["stress", "pressure", "overwhelm", "manage", "balance"]
        }
        return goal_keywords.get(goal, [])
    
    async def _generate_immediate_consequences(self, context: ConsequenceGenerationContext, 
                                            analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate immediate consequences based on choice analysis."""
        consequences = []
        
        # Get template based on choice characteristics
        template_key = self._select_consequence_template(context.choice, analysis)
        template = self.consequence_templates.get(template_key, {})
        
        if template and "immediate" in template:
            # Select appropriate immediate consequences
            immediate_options = template["immediate"]
            selected = immediate_options[:2]  # Take first 2 for now
            
            for consequence_text in selected:
                consequences.append({
                    "type": "immediate",
                    "description": consequence_text,
                    "severity": analysis["consequence_severity"].value,
                    "therapeutic_relevance": analysis["alignment_with_goals"]
                })
        else:
            # Generate generic consequence
            consequences.append({
                "type": "immediate",
                "description": f"Your choice to {context.choice.text.lower()} has immediate effects on the situation.",
                "severity": analysis["consequence_severity"].value,
                "therapeutic_relevance": analysis["alignment_with_goals"]
            })
        
        return consequences
    
    def _select_consequence_template(self, choice: UserChoice, analysis: Dict[str, Any]) -> str:
        """Select appropriate consequence template based on choice."""
        choice_text = choice.text.lower()
        
        # Simple keyword-based template selection
        if any(word in choice_text for word in ["communicate", "talk", "express", "share"]):
            return "positive_communication"
        elif any(word in choice_text for word in ["boundary", "limit", "no", "stop"]):
            return "healthy_boundary"
        elif any(word in choice_text for word in ["breathe", "calm", "pause", "mindful"]):
            return "emotional_regulation"
        elif any(word in choice_text for word in ["avoid", "ignore", "skip", "later"]):
            return "avoidance_behavior"
        elif any(word in choice_text for word in ["angry", "frustrated", "react", "snap"]):
            return "reactive_response"
        else:
            return "positive_communication"  # Default template

    async def _generate_therapeutic_outcomes(self, context: ConsequenceGenerationContext,
                                           analysis: Dict[str, Any]) -> List[TherapeuticOutcome]:
        """Generate therapeutic outcomes from consequences."""
        outcomes = []

        # Get template-based outcomes
        template_key = self._select_consequence_template(context.choice, analysis)
        template = self.consequence_templates.get(template_key, {})

        if template and "therapeutic_outcomes" in template:
            for outcome_data in template["therapeutic_outcomes"]:
                outcome = TherapeuticOutcome(
                    outcome_id=str(uuid4()),
                    outcome_type=outcome_data["skill"],
                    therapeutic_value=outcome_data["improvement"],
                    description=f"Improved {outcome_data['skill']} through choice experience",
                    measurement_criteria=f"Skill practice in {outcome_data['skill']}",
                    achieved_at=datetime.utcnow()
                )
                outcomes.append(outcome)

        return outcomes

    async def _create_learning_opportunities(self, context: ConsequenceGenerationContext,
                                           analysis: Dict[str, Any]) -> List[str]:
        """Create learning opportunities from consequences."""
        opportunities = []

        # Get template-based learning opportunities
        template_key = self._select_consequence_template(context.choice, analysis)
        template = self.consequence_templates.get(template_key, {})

        if template and "learning_opportunities" in template:
            for opportunity_type in template["learning_opportunities"]:
                opportunities.append(self._format_learning_opportunity(opportunity_type, context))

        # Add framework-specific learning prompts
        framework = self._select_therapeutic_framework(context)
        if framework in self.learning_frameworks:
            framework_data = self.learning_frameworks[framework]
            if "learning_prompts" in framework_data:
                opportunities.extend(framework_data["learning_prompts"][:2])  # Add 2 prompts

        return opportunities

    def _format_learning_opportunity(self, opportunity_type: LearningOpportunityType,
                                   context: ConsequenceGenerationContext) -> str:
        """Format learning opportunity as user-friendly text."""
        opportunity_formats = {
            LearningOpportunityType.EMOTIONAL_REGULATION:
                "This situation offers a chance to practice recognizing and managing emotions.",
            LearningOpportunityType.COMMUNICATION_SKILLS:
                "This is an opportunity to practice expressing yourself clearly and listening actively.",
            LearningOpportunityType.PROBLEM_SOLVING:
                "This challenge can help you develop problem-solving strategies.",
            LearningOpportunityType.SELF_AWARENESS:
                "This moment offers insight into your patterns and reactions.",
            LearningOpportunityType.RELATIONSHIP_BUILDING:
                "This interaction can strengthen your connection with others.",
            LearningOpportunityType.COPING_STRATEGIES:
                "This situation allows you to practice healthy coping techniques.",
            LearningOpportunityType.BOUNDARY_SETTING:
                "This is a chance to practice setting healthy boundaries.",
            LearningOpportunityType.CONFLICT_RESOLUTION:
                "This conflict offers an opportunity to practice resolution skills."
        }
        return opportunity_formats.get(opportunity_type, "This situation offers a learning opportunity.")

    def _select_therapeutic_framework(self, context: ConsequenceGenerationContext) -> str:
        """Select appropriate therapeutic framework for the user."""
        # Simple selection based on therapeutic goals
        goals = context.therapeutic_goals

        if any("anxiety" in goal or "stress" in goal for goal in goals):
            return "cognitive_behavioral"
        elif any("emotion" in goal or "regulation" in goal for goal in goals):
            return "dialectical_behavioral"
        elif any("mindfulness" in goal or "awareness" in goal for goal in goals):
            return "mindfulness_based"
        else:
            return "cognitive_behavioral"  # Default

    async def _frame_consequences_therapeutically(self, consequences: List[Dict[str, Any]],
                                                context: ConsequenceGenerationContext,
                                                analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Frame consequences in a therapeutically beneficial way."""
        framed_consequences = []

        framing_approach = analysis["framing_approach"]

        for consequence in consequences:
            framed_consequence = consequence.copy()

            # Add therapeutic framing
            if framing_approach == ConsequenceFraming.LEARNING_OPPORTUNITY:
                framed_consequence["therapeutic_frame"] = self._create_learning_frame(consequence, context)
            elif framing_approach == ConsequenceFraming.POSITIVE_REINFORCEMENT:
                framed_consequence["therapeutic_frame"] = self._create_reinforcement_frame(consequence, context)
            elif framing_approach == ConsequenceFraming.GROWTH_MOMENT:
                framed_consequence["therapeutic_frame"] = self._create_growth_frame(consequence, context)
            else:
                framed_consequence["therapeutic_frame"] = "This outcome reflects the natural result of your choice."

            # Add reflection prompts
            framed_consequence["reflection_prompts"] = self._generate_reflection_prompts(consequence, context)

            framed_consequences.append(framed_consequence)

        return framed_consequences

    def _create_learning_frame(self, consequence: Dict[str, Any],
                             context: ConsequenceGenerationContext) -> str:
        """Create learning-focused therapeutic frame."""
        template_key = self._select_consequence_template(context.choice, {})
        template = self.consequence_templates.get(template_key, {})

        if template and "learning_framing" in template:
            return template["learning_framing"]
        else:
            return "Every choice is an opportunity to learn something new about yourself and develop your skills."

    def _create_reinforcement_frame(self, consequence: Dict[str, Any],
                                  context: ConsequenceGenerationContext) -> str:
        """Create positive reinforcement frame."""
        return "This positive outcome shows your growing skills and healthy choices. Well done!"

    def _create_growth_frame(self, consequence: Dict[str, Any],
                           context: ConsequenceGenerationContext) -> str:
        """Create growth-focused frame."""
        return "This experience contributes to your personal growth and understanding."

    def _generate_reflection_prompts(self, consequence: Dict[str, Any],
                                   context: ConsequenceGenerationContext) -> List[str]:
        """Generate reflection prompts for the consequence."""
        prompts = [
            "How do you feel about this outcome?",
            "What did you learn from this experience?",
            "What might you do differently next time?"
        ]

        # Add choice-specific prompts
        if "communication" in context.choice.text.lower():
            prompts.append("How did your communication style affect the outcome?")
        elif "emotional" in context.choice.text.lower():
            prompts.append("What emotions did you notice during this choice?")

        return prompts[:3]  # Return max 3 prompts

    def _determine_consequence_type(self, analysis: Dict[str, Any]) -> ConsequenceType:
        """Determine the type of consequence based on analysis."""
        if analysis["therapeutic_relevance"] > 0.7:
            return ConsequenceType.THERAPEUTIC
        elif analysis["emotional_weight"] > 0.6:
            return ConsequenceType.SHORT_TERM
        else:
            return ConsequenceType.IMMEDIATE

    async def _update_choice_patterns(self, context: ConsequenceGenerationContext,
                                    consequence_set: ConsequenceSet) -> None:
        """Update choice patterns for pattern recognition."""
        user_id = context.session_state.user_id
        choice_type = context.choice.choice_type.value

        pattern_key = f"{user_id}_{choice_type}"

        if pattern_key not in self.choice_patterns:
            self.choice_patterns[pattern_key] = ConsequencePattern(
                choice_pattern=choice_type,
                consequence_theme="developing",
                frequency=0
            )

        pattern = self.choice_patterns[pattern_key]
        pattern.frequency += 1

        # Update therapeutic significance
        if consequence_set.therapeutic_outcomes:
            avg_therapeutic_value = sum(
                outcome.therapeutic_value for outcome in consequence_set.therapeutic_outcomes
            ) / len(consequence_set.therapeutic_outcomes)
            pattern.therapeutic_significance = (
                pattern.therapeutic_significance * 0.8 + avg_therapeutic_value * 0.2
            )

        # Update learning opportunities
        if consequence_set.learning_opportunities:
            for opportunity in consequence_set.learning_opportunities:
                # Extract learning type from opportunity text (simplified)
                if "emotional" in opportunity.lower():
                    if LearningOpportunityType.EMOTIONAL_REGULATION not in pattern.learning_opportunities:
                        pattern.learning_opportunities.append(LearningOpportunityType.EMOTIONAL_REGULATION)
                elif "communication" in opportunity.lower():
                    if LearningOpportunityType.COMMUNICATION_SKILLS not in pattern.learning_opportunities:
                        pattern.learning_opportunities.append(LearningOpportunityType.COMMUNICATION_SKILLS)

        self.metrics["pattern_recognitions"] += 1

    async def _publish_consequence_event(self, context: ConsequenceGenerationContext,
                                       consequence_set: ConsequenceSet) -> None:
        """Publish consequence generation event."""
        event = create_consequence_event(
            EventType.CONSEQUENCE_APPLIED,
            context.session_state.session_id,
            context.session_state.user_id,
            consequence_set.consequence_id,
            {
                "choice_id": context.choice.choice_id,
                "consequence_type": consequence_set.consequence_type.value,
                "therapeutic_outcomes_count": len(consequence_set.therapeutic_outcomes),
                "learning_opportunities_count": len(consequence_set.learning_opportunities)
            }
        )
        await self.event_bus.publish(event)

    async def explain_causality(self, choice_id: str, consequence_id: str,
                              context: ConsequenceGenerationContext) -> CausalityExplanation:
        """Generate explanation of causal relationship between choice and consequence."""
        explanation = CausalityExplanation(
            choice_id=choice_id,
            consequence_id=consequence_id
        )

        # Build causal chain
        choice = context.choice
        causal_chain = [
            f"You chose to: {choice.text}",
            "This choice reflected your values and current emotional state",
            "The choice led to specific reactions from others and the environment",
            "These reactions created the consequences you experienced"
        ]

        # Add therapeutic insight
        therapeutic_insight = self._generate_therapeutic_insight(choice, context)

        # Generate learning points
        learning_points = [
            "Choices reflect our internal state and values",
            "Every choice has natural consequences in relationships and situations",
            "Understanding these connections helps us make more intentional choices",
            "Each experience builds our wisdom for future decisions"
        ]

        explanation.causal_chain = causal_chain
        explanation.therapeutic_insight = therapeutic_insight
        explanation.learning_points = learning_points
        explanation.confidence = 0.8  # High confidence for rule-based explanations

        self.metrics["causality_explanations"] += 1

        return explanation

    def _generate_therapeutic_insight(self, choice: UserChoice,
                                    context: ConsequenceGenerationContext) -> str:
        """Generate therapeutic insight from choice-consequence relationship."""
        insights = [
            "This experience shows how our choices shape our relationships and environment.",
            "Notice how your internal state influenced your choice and its outcomes.",
            "This pattern of choice and consequence is common in similar situations.",
            "Your growing awareness of these connections is a sign of personal growth."
        ]

        # Select insight based on choice characteristics
        if choice.therapeutic_relevance > 0.7:
            return insights[3]  # Growth-focused
        elif choice.emotional_weight > 0.6:
            return insights[1]  # Emotion-focused
        else:
            return insights[0]  # General relationship-focused

    async def recognize_patterns(self, user_id: str, session_count: int = 10) -> List[ConsequencePattern]:
        """Recognize patterns in user's choice-consequence history."""
        user_patterns = [
            pattern for pattern_key, pattern in self.choice_patterns.items()
            if pattern_key.startswith(user_id)
        ]

        # Filter patterns with sufficient frequency
        significant_patterns = [
            pattern for pattern in user_patterns
            if pattern.frequency >= 3  # At least 3 occurrences
        ]

        # Sort by therapeutic significance
        significant_patterns.sort(key=lambda p: p.therapeutic_significance, reverse=True)

        return significant_patterns[:5]  # Return top 5 patterns

    def get_metrics(self) -> Dict[str, Any]:
        """Get consequence system metrics."""
        return {
            **self.metrics,
            "active_patterns": len(self.choice_patterns),
            "causality_explanations_stored": len(self.causality_explanations)
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of consequence system."""
        return {
            "status": "healthy",
            "templates_loaded": len(self.consequence_templates),
            "frameworks_loaded": len(self.learning_frameworks),
            "patterns_tracked": len(self.choice_patterns),
            "metrics": self.get_metrics()
        }
