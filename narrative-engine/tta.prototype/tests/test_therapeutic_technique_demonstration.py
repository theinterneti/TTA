"""
Unit Tests for Therapeutic Technique Demonstration System

This module contains comprehensive unit tests for the therapeutic technique demonstration
system, including scenario generation, technique integration, and reflection opportunities.
"""

import sys
import unittest
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

from data_models import (
    NarrativeContext,
    SessionState,
)
from therapeutic_technique_demonstration import (
    LearningObjective,
    NarrativeScenario,
    NarrativeScenarioGenerator,
    ReflectionOpportunity,
    ReflectionOpportunityGenerator,
    ScenarioType,
    TechniqueIntegrator,
    TechniqueStep,
    TechniqueType,
    TherapeuticTechniqueDemo,
)


class TestNarrativeScenarioGenerator(unittest.TestCase):
    """Test cases for NarrativeScenarioGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = NarrativeScenarioGenerator()

        # Create test context
        self.context = NarrativeContext(
            session_id="test_session",
            current_location_id="peaceful_garden",
            recent_events=["User expressed anxiety", "Character offered support"]
        )

        # Create test user needs
        self.user_needs = {
            'emotional_state': 'anxious',
            'experience_level': 'beginner',
            'confidence_level': 0.4
        }

    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertIsInstance(self.generator.technique_templates, dict)
        self.assertIsInstance(self.generator.scenario_templates, dict)

        # Check that all technique types have templates
        for technique_type in [TechniqueType.DEEP_BREATHING, TechniqueType.GROUNDING_5_4_3_2_1]:
            self.assertIn(technique_type, self.generator.technique_templates)

    def test_generate_deep_breathing_scenario(self):
        """Test generating deep breathing technique scenario."""
        scenario = self.generator.generate_technique_scenario(
            technique_type=TechniqueType.DEEP_BREATHING,
            scenario_type=ScenarioType.GUIDED_PRACTICE,
            context=self.context,
            user_needs=self.user_needs
        )

        self.assertIsInstance(scenario, NarrativeScenario)
        self.assertEqual(scenario.technique_type, TechniqueType.DEEP_BREATHING)
        self.assertEqual(scenario.scenario_type, ScenarioType.GUIDED_PRACTICE)
        self.assertGreater(len(scenario.technique_steps), 0)
        self.assertGreater(len(scenario.reflection_prompts), 0)
        self.assertGreater(scenario.estimated_duration, 0)

        # Validate scenario
        self.assertTrue(scenario.validate())

    def test_generate_grounding_scenario(self):
        """Test generating grounding technique scenario."""
        scenario = self.generator.generate_technique_scenario(
            technique_type=TechniqueType.GROUNDING_5_4_3_2_1,
            scenario_type=ScenarioType.CHARACTER_MODELING,
            context=self.context,
            user_needs=self.user_needs
        )

        self.assertIsInstance(scenario, NarrativeScenario)
        self.assertEqual(scenario.technique_type, TechniqueType.GROUNDING_5_4_3_2_1)
        self.assertEqual(scenario.scenario_type, ScenarioType.CHARACTER_MODELING)
        self.assertTrue(scenario.validate())

    def test_create_technique_steps(self):
        """Test creation of technique steps."""
        technique_template = self.generator.technique_templates[TechniqueType.DEEP_BREATHING]
        steps = self.generator._create_technique_steps(
            TechniqueType.DEEP_BREATHING,
            technique_template,
            self.context
        )

        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)

        for i, step in enumerate(steps, 1):
            self.assertIsInstance(step, TechniqueStep)
            self.assertEqual(step.step_number, i)
            self.assertTrue(step.instruction.strip())
            self.assertTrue(step.narrative_description.strip())
            self.assertTrue(step.character_guidance.strip())
            self.assertTrue(step.validate())

    def test_generate_narrative_setup(self):
        """Test narrative setup generation."""
        setup = self.generator._generate_narrative_setup(
            TechniqueType.DEEP_BREATHING,
            ScenarioType.GUIDED_PRACTICE,
            self.context,
            self.user_needs
        )

        self.assertIsInstance(setup, str)
        self.assertGreater(len(setup.strip()), 0)
        self.assertIn("peaceful_garden", setup)

    def test_determine_learning_objectives(self):
        """Test learning objectives determination."""
        objectives = self.generator._determine_learning_objectives(
            TechniqueType.DEEP_BREATHING,
            self.user_needs
        )

        self.assertIsInstance(objectives, list)
        self.assertGreater(len(objectives), 0)
        self.assertIn(LearningObjective.TECHNIQUE_UNDERSTANDING, objectives)

        for objective in objectives:
            self.assertIsInstance(objective, LearningObjective)

    def test_estimate_scenario_duration(self):
        """Test scenario duration estimation."""
        duration = self.generator._estimate_scenario_duration(
            TechniqueType.DEEP_BREATHING,
            ScenarioType.GUIDED_PRACTICE
        )

        self.assertIsInstance(duration, int)
        self.assertGreater(duration, 0)
        self.assertLess(duration, 60)  # Should be reasonable duration

    def test_assess_difficulty_level(self):
        """Test difficulty level assessment."""
        difficulty = self.generator._assess_difficulty_level(
            TechniqueType.DEEP_BREATHING,
            self.user_needs
        )

        self.assertIsInstance(difficulty, int)
        self.assertGreaterEqual(difficulty, 1)
        self.assertLessEqual(difficulty, 5)


class TestTechniqueIntegrator(unittest.TestCase):
    """Test cases for TechniqueIntegrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.integrator = TechniqueIntegrator()

        # Create test scenario
        self.scenario = NarrativeScenario(
            title="Deep Breathing Practice",
            description="A calming breathing exercise",
            technique_type=TechniqueType.DEEP_BREATHING,
            scenario_type=ScenarioType.GUIDED_PRACTICE,
            technique_steps=[
                TechniqueStep(
                    step_number=1,
                    instruction="Find a comfortable position",
                    narrative_description="You settle into a comfortable position",
                    character_guidance="Your companion says: 'Find a position that feels right for you.'"
                )
            ]
        )

        # Create test context
        self.context = NarrativeContext(
            session_id="test_session",
            current_location_id="peaceful_garden"
        )

        # Create test session state
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user",
            current_scenario_id="test_scenario"
        )

    def test_integrator_initialization(self):
        """Test integrator initialization."""
        self.assertIsInstance(self.integrator.integration_patterns, dict)

        # Check that all integration patterns are defined
        expected_patterns = ["natural_opportunity", "teaching_moment", "crisis_response", "skill_building"]
        for pattern in expected_patterns:
            self.assertIn(pattern, self.integrator.integration_patterns)

    def test_integrate_technique_with_story(self):
        """Test technique integration with story."""
        integration_plan = self.integrator.integrate_technique_with_story(
            scenario=self.scenario,
            context=self.context,
            session_state=self.session_state
        )

        self.assertIsInstance(integration_plan, dict)

        # Check required components
        required_keys = [
            "integration_approach", "story_transitions", "character_interactions",
            "choice_points", "technique_progression", "narrative_continuity", "success_metrics"
        ]
        for key in required_keys:
            self.assertIn(key, integration_plan)

    def test_select_integration_approach(self):
        """Test integration approach selection."""
        approach = self.integrator._select_integration_approach(
            self.scenario, self.context, self.session_state
        )

        self.assertIsInstance(approach, str)
        self.assertIn(approach, self.integrator.integration_patterns.keys())

    def test_create_story_transitions(self):
        """Test story transitions creation."""
        transitions = self.integrator._create_story_transitions(
            self.scenario, self.context, "teaching_moment"
        )

        self.assertIsInstance(transitions, dict)

        expected_transitions = [
            "setup_transition", "technique_introduction", "practice_transition",
            "completion_transition", "story_continuation"
        ]
        for transition in expected_transitions:
            self.assertIn(transition, transitions)
            self.assertIsInstance(transitions[transition], str)
            self.assertGreater(len(transitions[transition].strip()), 0)

    def test_generate_character_interactions(self):
        """Test character interactions generation."""
        interactions = self.integrator._generate_character_interactions(
            self.scenario, "teaching_moment"
        )

        self.assertIsInstance(interactions, list)
        self.assertGreater(len(interactions), 0)

        for interaction in interactions:
            self.assertIsInstance(interaction, dict)
            self.assertIn("type", interaction)
            self.assertIn("character_dialogue", interaction)
            self.assertIn("character_action", interaction)
            self.assertIn("narrative_context", interaction)

    def test_create_choice_points(self):
        """Test choice points creation."""
        choice_points = self.integrator._create_choice_points(
            self.scenario, "teaching_moment"
        )

        self.assertIsInstance(choice_points, list)
        self.assertGreater(len(choice_points), 0)

        for choice_point in choice_points:
            self.assertIsInstance(choice_point, dict)
            self.assertIn("choice_id", choice_point)
            self.assertIn("prompt", choice_point)
            self.assertIn("options", choice_point)
            self.assertIsInstance(choice_point["options"], list)
            self.assertGreater(len(choice_point["options"]), 0)


class TestReflectionOpportunityGenerator(unittest.TestCase):
    """Test cases for ReflectionOpportunityGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReflectionOpportunityGenerator()

        # Create test scenario
        self.scenario = NarrativeScenario(
            title="Deep Breathing Practice",
            technique_type=TechniqueType.DEEP_BREATHING,
            learning_objectives=[LearningObjective.TECHNIQUE_UNDERSTANDING],
            reflection_prompts=["How did this feel?"]
        )

        # Create test user experience
        self.user_experience = {
            'engagement_level': 'high',
            'completed_all_steps': True,
            'found_challenging': False,
            'emotional_response': True
        }

        # Create test context
        self.context = NarrativeContext(
            session_id="test_session",
            current_location_id="peaceful_garden"
        )

    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertIsInstance(self.generator.reflection_frameworks, dict)

        expected_frameworks = [
            "experiential_reflection", "learning_integration",
            "application_planning", "metacognitive_reflection"
        ]
        for framework in expected_frameworks:
            self.assertIn(framework, self.generator.reflection_frameworks)

    def test_generate_reflection_opportunity(self):
        """Test reflection opportunity generation."""
        reflection = self.generator.generate_reflection_opportunity(
            scenario=self.scenario,
            user_experience=self.user_experience,
            context=self.context
        )

        self.assertIsInstance(reflection, ReflectionOpportunity)
        self.assertTrue(reflection.validate())
        self.assertGreater(len(reflection.guiding_questions), 0)
        self.assertGreater(len(reflection.learning_points), 0)
        self.assertTrue(reflection.narrative_integration.strip())
        self.assertTrue(reflection.character_facilitation.strip())

    def test_select_reflection_framework(self):
        """Test reflection framework selection."""
        framework = self.generator._select_reflection_framework(
            self.scenario, self.user_experience
        )

        self.assertIsInstance(framework, str)
        self.assertIn(framework, self.generator.reflection_frameworks.keys())

    def test_generate_guiding_questions(self):
        """Test guiding questions generation."""
        questions = self.generator._generate_guiding_questions(
            self.scenario, "experiential_reflection", self.user_experience
        )

        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)
        self.assertLessEqual(len(questions), 6)  # Should limit to 6 questions

        for question in questions:
            self.assertIsInstance(question, str)
            self.assertGreater(len(question.strip()), 0)

    def test_identify_learning_points(self):
        """Test learning points identification."""
        learning_points = self.generator._identify_learning_points(
            self.scenario, self.user_experience
        )

        self.assertIsInstance(learning_points, list)
        self.assertGreater(len(learning_points), 0)
        self.assertLessEqual(len(learning_points), 5)  # Should limit to 5 points

        for point in learning_points:
            self.assertIsInstance(point, str)
            self.assertGreater(len(point.strip()), 0)

    def test_determine_expected_insights(self):
        """Test expected insights determination."""
        insights = self.generator._determine_expected_insights(
            self.scenario, self.user_experience
        )

        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        self.assertLessEqual(len(insights), 4)  # Should limit to 4 insights

        for insight in insights:
            self.assertIsInstance(insight, str)
            self.assertGreater(len(insight.strip()), 0)

    def test_plan_follow_up_actions(self):
        """Test follow-up actions planning."""
        actions = self.generator._plan_follow_up_actions(
            self.scenario, self.user_experience
        )

        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
        self.assertLessEqual(len(actions), 5)  # Should limit to 5 actions

        for action in actions:
            self.assertIsInstance(action, str)
            self.assertGreater(len(action.strip()), 0)


class TestTherapeuticTechniqueDemo(unittest.TestCase):
    """Test cases for TherapeuticTechniqueDemo main class."""

    def setUp(self):
        """Set up test fixtures."""
        self.demo_system = TherapeuticTechniqueDemo()

        # Create test context
        self.context = NarrativeContext(
            session_id="test_session",
            current_location_id="peaceful_garden"
        )

        # Create test session state
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user",
            current_scenario_id="test_scenario"
        )

        # Create test user preferences
        self.user_preferences = {
            'learning_style': 'guided',
            'experience_level': 'beginner'
        }

    def test_system_initialization(self):
        """Test system initialization."""
        self.assertIsInstance(self.demo_system.scenario_generator, NarrativeScenarioGenerator)
        self.assertIsInstance(self.demo_system.technique_integrator, TechniqueIntegrator)
        self.assertIsInstance(self.demo_system.reflection_generator, ReflectionOpportunityGenerator)

    def test_create_technique_demonstration(self):
        """Test complete technique demonstration creation."""
        demonstration = self.demo_system.create_technique_demonstration(
            technique_type=TechniqueType.DEEP_BREATHING,
            context=self.context,
            session_state=self.session_state,
            user_preferences=self.user_preferences
        )

        self.assertIsInstance(demonstration, dict)

        # Check required components
        required_keys = [
            "scenario", "integration_plan", "reflection_template",
            "execution_guidance", "success_metrics", "adaptation_options"
        ]
        for key in required_keys:
            self.assertIn(key, demonstration)

        # Validate scenario
        scenario = demonstration["scenario"]
        self.assertIsInstance(scenario, NarrativeScenario)
        self.assertTrue(scenario.validate())

    def test_execute_technique_step(self):
        """Test technique step execution."""
        # First create a demonstration
        demonstration = self.demo_system.create_technique_demonstration(
            technique_type=TechniqueType.DEEP_BREATHING,
            context=self.context,
            session_state=self.session_state
        )

        # Execute first step
        step_execution = self.demo_system.execute_technique_step(
            demonstration_package=demonstration,
            step_number=1,
            user_response={}
        )

        self.assertIsInstance(step_execution, dict)

        # Check required components
        required_keys = [
            "step_number", "step_instruction", "narrative_description",
            "character_guidance", "user_action_required", "expected_outcome"
        ]
        for key in required_keys:
            self.assertIn(key, step_execution)

        self.assertEqual(step_execution["step_number"], 1)

    def test_generate_reflection_opportunity(self):
        """Test reflection opportunity generation."""
        # Create demonstration
        demonstration = self.demo_system.create_technique_demonstration(
            technique_type=TechniqueType.DEEP_BREATHING,
            context=self.context,
            session_state=self.session_state
        )

        # Create user experience
        user_experience = {
            'engagement_level': 'high',
            'completed_all_steps': True
        }

        # Generate reflection
        reflection = self.demo_system.generate_reflection_opportunity(
            demonstration_package=demonstration,
            user_experience=user_experience,
            context=self.context
        )

        self.assertIsInstance(reflection, ReflectionOpportunity)
        self.assertTrue(reflection.validate())

    def test_determine_scenario_type(self):
        """Test scenario type determination."""
        scenario_type = self.demo_system._determine_scenario_type(
            self.context, self.session_state, self.user_preferences
        )

        self.assertIsInstance(scenario_type, ScenarioType)

    def test_extract_user_needs(self):
        """Test user needs extraction."""
        needs = self.demo_system._extract_user_needs(
            self.session_state, self.user_preferences
        )

        self.assertIsInstance(needs, dict)

        expected_keys = ['emotional_state', 'experience_level', 'confidence_level', 'skill_transfer']
        for key in expected_keys:
            self.assertIn(key, needs)


class TestDataModels(unittest.TestCase):
    """Test cases for data models used in technique demonstration."""

    def test_technique_step_validation(self):
        """Test TechniqueStep validation."""
        # Valid step
        step = TechniqueStep(
            step_number=1,
            instruction="Take a deep breath",
            narrative_description="You breathe deeply",
            character_guidance="Your companion guides you"
        )
        self.assertTrue(step.validate())

        # Invalid step - empty instruction
        invalid_step = TechniqueStep(
            step_number=1,
            instruction="",
            narrative_description="Description",
            character_guidance="Guidance"
        )
        with self.assertRaises(Exception):
            invalid_step.validate()

        # Invalid step - negative step number
        invalid_step2 = TechniqueStep(
            step_number=0,
            instruction="Instruction",
            narrative_description="Description",
            character_guidance="Guidance"
        )
        with self.assertRaises(Exception):
            invalid_step2.validate()

    def test_narrative_scenario_validation(self):
        """Test NarrativeScenario validation."""
        # Valid scenario
        scenario = NarrativeScenario(
            title="Test Scenario",
            description="A test scenario",
            narrative_setup="Test setup",
            technique_steps=[
                TechniqueStep(
                    step_number=1,
                    instruction="Test instruction",
                    narrative_description="Test description",
                    character_guidance="Test guidance"
                )
            ]
        )
        self.assertTrue(scenario.validate())

        # Invalid scenario - empty title
        invalid_scenario = NarrativeScenario(
            title="",
            description="Description",
            narrative_setup="Setup"
        )
        with self.assertRaises(Exception):
            invalid_scenario.validate()

    def test_reflection_opportunity_validation(self):
        """Test ReflectionOpportunity validation."""
        # Valid reflection opportunity
        reflection = ReflectionOpportunity(
            trigger_event="Completed technique",
            guiding_questions=["How did it feel?"]
        )
        self.assertTrue(reflection.validate())

        # Invalid reflection - empty trigger event
        invalid_reflection = ReflectionOpportunity(
            trigger_event="",
            guiding_questions=["Question"]
        )
        with self.assertRaises(Exception):
            invalid_reflection.validate()

        # Invalid reflection - no guiding questions
        invalid_reflection2 = ReflectionOpportunity(
            trigger_event="Event",
            guiding_questions=[]
        )
        with self.assertRaises(Exception):
            invalid_reflection2.validate()


if __name__ == '__main__':
    unittest.main()
