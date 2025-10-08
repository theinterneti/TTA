"""
TTA Single-Player Storytelling Experience Testing Framework

This module provides comprehensive testing infrastructure for evaluating
AI models in TTA's single-player storytelling experience with focus on
user enjoyment and game-first presentation.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import redis.asyncio as aioredis
import yaml
from neo4j import AsyncGraphDatabase

from src.player_experience.models.character import Character, CharacterCreationData
from src.player_experience.services.privacy_service import DataPrivacyService

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result for a specific model and scenario."""

    test_id: str
    model_name: str
    scenario_name: str
    profile_name: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None

    # Evaluation scores (1-10)
    narrative_quality_score: float | None = None
    user_engagement_score: float | None = None
    therapeutic_integration_score: float | None = None
    technical_performance_score: float | None = None
    overall_score: float | None = None

    # Detailed metrics
    response_times: list[float] = field(default_factory=list)
    error_count: int = 0
    session_continuity_score: float | None = None
    choice_meaningfulness_score: float | None = None

    # Qualitative feedback
    narrative_examples: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    notes: str = ""

    # Raw data
    conversation_log: list[dict[str, Any]] = field(default_factory=list)
    character_state_changes: list[dict[str, Any]] = field(default_factory=list)
    therapeutic_interventions: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ModelConfiguration:
    """Configuration for a specific AI model."""

    name: str
    provider: str
    model_id: str
    api_base: str | None = None
    api_key: str | None = None
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    enabled: bool = True
    strengths: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)


@dataclass
class TestProfile:
    """Anonymized test profile for consistent testing."""

    name: str
    demographics: dict[str, Any]
    therapeutic_profile: dict[str, Any]
    preferences: dict[str, Any]
    character_template: CharacterCreationData | None = None


@dataclass
class TestScenario:
    """Test scenario configuration."""

    name: str
    duration_minutes: int
    steps: list[str]
    evaluation_focus: list[str]
    sessions: int = 1
    choice_points: int | None = None
    trigger_conditions: list[str] | None = None


class SinglePlayerTestFramework:
    """Main testing framework for single-player storytelling experience."""

    def __init__(self, config_path: str = "testing/model_testing_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.privacy_service = DataPrivacyService()
        self.results: list[TestResult] = []
        self.models: dict[str, ModelConfiguration] = {}
        self.profiles: dict[str, TestProfile] = {}
        self.scenarios: dict[str, TestScenario] = {}

        # Initialize components
        self._initialize_models()
        self._initialize_profiles()
        self._initialize_scenarios()

        # Database connections
        self.redis: aioredis.Redis | None = None
        self.neo4j_driver = None

    def _load_config(self) -> dict[str, Any]:
        """Load testing configuration from YAML file."""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise

    def _initialize_models(self):
        """Initialize model configurations from config."""
        models_config = self.config.get("models", {})

        # Local models
        for model_key, model_config in models_config.get("local", {}).items():
            if model_config.get("enabled", False):
                self.models[model_key] = ModelConfiguration(**model_config)

        # OpenRouter models
        openrouter_config = models_config.get("openrouter", {})
        api_key = openrouter_config.get("api_key")
        base_url = openrouter_config.get("base_url")

        for model_key, model_config in openrouter_config.items():
            if isinstance(model_config, dict) and model_config.get("enabled", False):
                config = model_config.copy()
                config["api_key"] = api_key
                config["api_base"] = base_url
                self.models[model_key] = ModelConfiguration(**config)

    def _initialize_profiles(self):
        """Initialize test profiles from config."""
        profiles_config = self.config.get("test_profiles", {})

        for profile_key, profile_config in profiles_config.items():
            self.profiles[profile_key] = TestProfile(
                name=profile_config["name"],
                demographics=profile_config["demographics"],
                therapeutic_profile=profile_config["therapeutic_profile"],
                preferences=profile_config["preferences"],
            )

    def _initialize_scenarios(self):
        """Initialize test scenarios from config."""
        scenarios_config = self.config.get("test_scenarios", {})

        for scenario_key, scenario_config in scenarios_config.items():
            self.scenarios[scenario_key] = TestScenario(**scenario_config)

    async def initialize_connections(self):
        """Initialize database connections."""
        try:
            # Redis connection
            redis_url = "redis://localhost:6379"
            self.redis = await aioredis.from_url(redis_url)

            # Neo4j connection
            neo4j_url = "bolt://localhost:7687"
            self.neo4j_driver = AsyncGraphDatabase.driver(
                neo4j_url, auth=("neo4j", "password")
            )

            logger.info("Database connections initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise

    async def cleanup_connections(self):
        """Cleanup database connections."""
        if self.redis:
            await self.redis.close()
        if self.neo4j_driver:
            await self.neo4j_driver.close()

    async def run_comprehensive_test(self) -> dict[str, Any]:
        """Run comprehensive testing across all models, profiles, and scenarios."""
        logger.info("Starting comprehensive single-player storytelling test")

        await self.initialize_connections()

        try:
            total_tests = len(self.models) * len(self.profiles) * len(self.scenarios)
            completed_tests = 0

            for model_key, model in self.models.items():
                for profile_key, profile in self.profiles.items():
                    for scenario_key, scenario in self.scenarios.items():
                        logger.info(
                            f"Running test: {model.name} + {profile.name} + {scenario.name}"
                        )

                        result = await self._run_single_test(model, profile, scenario)
                        self.results.append(result)

                        completed_tests += 1
                        progress = (completed_tests / total_tests) * 100
                        logger.info(
                            f"Test progress: {progress:.1f}% ({completed_tests}/{total_tests})"
                        )

            # Generate comprehensive analysis
            analysis = await self._generate_analysis()

            # Save results
            await self._save_results(analysis)

            logger.info("Comprehensive testing completed successfully")
            return analysis

        finally:
            await self.cleanup_connections()

    async def _run_single_test(
        self, model: ModelConfiguration, profile: TestProfile, scenario: TestScenario
    ) -> TestResult:
        """Run a single test with specific model, profile, and scenario."""
        test_id = str(uuid.uuid4())
        start_time = datetime.now()

        result = TestResult(
            test_id=test_id,
            model_name=model.name,
            scenario_name=scenario.name,
            profile_name=profile.name,
            start_time=start_time,
        )

        try:
            # Create anonymized character for testing
            character = await self._create_test_character(profile)

            # Execute scenario steps
            for step in scenario.steps:
                step_result = await self._execute_scenario_step(
                    step, model, character, profile, scenario
                )

                # Record step results
                result.conversation_log.extend(step_result.get("conversations", []))
                result.response_times.extend(step_result.get("response_times", []))
                result.error_count += step_result.get("errors", 0)

            # Calculate evaluation scores
            await self._evaluate_test_result(result, model, profile, scenario)

            result.end_time = datetime.now()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()

            logger.info(
                f"Test completed: {test_id} - Overall Score: {result.overall_score:.2f}"
            )

        except Exception as e:
            logger.error(f"Test failed: {test_id} - {str(e)}")
            result.error_count += 1
            result.notes = f"Test failed with error: {str(e)}"
            result.end_time = datetime.now()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()

        return result

    async def _create_test_character(self, profile: TestProfile) -> Character:
        """Create an anonymized test character based on profile."""
        # Use privacy service to ensure anonymization
        anonymous_id = self.privacy_service.anonymization_service.anonymize_user_id(
            f"test_user_{profile.name}"
        )

        # Create character based on profile template
        character_data = CharacterCreationData(
            name=f"TestChar_{anonymous_id[:8]}",
            appearance=self._generate_appearance_from_profile(profile),
            background=self._generate_background_from_profile(profile),
            therapeutic_profile=self._generate_therapeutic_profile_from_profile(
                profile
            ),
        )

        # This would integrate with the actual character creation system
        # For now, return a mock character
        character = Character(
            character_id=str(uuid.uuid4()),
            player_id=anonymous_id,
            name=character_data.name,
            appearance=character_data.appearance,
            background=character_data.background,
            therapeutic_profile=character_data.therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        return character

    async def _execute_scenario_step(
        self,
        step: str,
        model: ModelConfiguration,
        character: Character,
        profile: TestProfile,
        scenario: TestScenario,
    ) -> dict[str, Any]:
        """Execute a single scenario step."""
        step_start = time.time()
        step_result = {"conversations": [], "response_times": [], "errors": 0}

        try:
            # This would integrate with the actual narrative engine
            # For now, simulate the step execution

            if step == "character_creation":
                # Test character creation flow
                response_time = await self._simulate_character_creation(
                    model, character
                )
                step_result["response_times"].append(response_time)

            elif step == "first_session_tutorial":
                # Test tutorial experience
                response_time = await self._simulate_tutorial_session(
                    model, character, profile
                )
                step_result["response_times"].append(response_time)

            elif step == "session_continuity":
                # Test session continuation
                response_time = await self._simulate_session_continuation(
                    model, character
                )
                step_result["response_times"].append(response_time)

            # Add more step implementations as needed

        except Exception as e:
            logger.error(f"Step execution failed: {step} - {str(e)}")
            step_result["errors"] += 1

        return step_result

    async def _simulate_character_creation(
        self, model: ModelConfiguration, character: Character
    ) -> float:
        """Simulate character creation process and measure response time."""
        start_time = time.time()

        # Simulate API call to model for character creation guidance
        await asyncio.sleep(0.5)  # Simulate processing time

        return time.time() - start_time

    async def _simulate_tutorial_session(
        self, model: ModelConfiguration, character: Character, profile: TestProfile
    ) -> float:
        """Simulate tutorial session and measure response time."""
        start_time = time.time()

        # Simulate narrative generation for tutorial
        await asyncio.sleep(1.0)  # Simulate processing time

        return time.time() - start_time

    async def _simulate_session_continuation(
        self, model: ModelConfiguration, character: Character
    ) -> float:
        """Simulate session continuation and measure response time."""
        start_time = time.time()

        # Simulate narrative continuation
        await asyncio.sleep(0.8)  # Simulate processing time

        return time.time() - start_time

    async def _evaluate_test_result(
        self,
        result: TestResult,
        model: ModelConfiguration,
        profile: TestProfile,
        scenario: TestScenario,
    ):
        """Evaluate test result and calculate scores."""
        evaluation_config = self.config.get("evaluation", {})
        dimensions = evaluation_config.get("dimensions", {})

        # Calculate narrative quality score
        result.narrative_quality_score = await self._calculate_narrative_quality_score(
            result, model, scenario
        )

        # Calculate user engagement score
        result.user_engagement_score = await self._calculate_user_engagement_score(
            result, profile, scenario
        )

        # Calculate therapeutic integration score
        result.therapeutic_integration_score = (
            await self._calculate_therapeutic_integration_score(result, profile)
        )

        # Calculate technical performance score
        result.technical_performance_score = (
            await self._calculate_technical_performance_score(result)
        )

        # Calculate weighted overall score
        weights = {
            "narrative_quality": dimensions.get("narrative_quality", {}).get(
                "weight", 0.4
            ),
            "user_engagement": dimensions.get("user_engagement", {}).get("weight", 0.3),
            "therapeutic_integration": dimensions.get(
                "therapeutic_integration", {}
            ).get("weight", 0.2),
            "technical_performance": dimensions.get("technical_performance", {}).get(
                "weight", 0.1
            ),
        }

        result.overall_score = (
            result.narrative_quality_score * weights["narrative_quality"]
            + result.user_engagement_score * weights["user_engagement"]
            + result.therapeutic_integration_score * weights["therapeutic_integration"]
            + result.technical_performance_score * weights["technical_performance"]
        )

    async def _calculate_narrative_quality_score(
        self, result: TestResult, model: ModelConfiguration, scenario: TestScenario
    ) -> float:
        """Calculate narrative quality score based on creativity, consistency, etc."""
        # This would integrate with actual narrative analysis
        # For now, simulate based on model strengths and scenario performance

        base_score = 7.0  # Default baseline

        # Adjust based on model strengths
        if "creative_storytelling" in model.strengths:
            base_score += 0.5
        if "narrative_coherence" in model.strengths:
            base_score += 0.5
        if "character_consistency" in model.strengths:
            base_score += 0.3

        # Adjust based on response times (faster = potentially less thoughtful)
        avg_response_time = (
            sum(result.response_times) / len(result.response_times)
            if result.response_times
            else 1.0
        )
        if avg_response_time < 0.5:
            base_score -= 0.2  # Too fast might indicate shallow responses
        elif avg_response_time > 3.0:
            base_score -= 0.3  # Too slow affects user experience

        # Adjust for errors
        if result.error_count > 0:
            base_score -= result.error_count * 0.5

        return max(1.0, min(10.0, base_score))

    async def _calculate_user_engagement_score(
        self, result: TestResult, profile: TestProfile, scenario: TestScenario
    ) -> float:
        """Calculate user engagement score based on fun factor, immersion, etc."""
        base_score = 7.0

        # Adjust based on profile preferences alignment
        preferences = profile.preferences

        if scenario.name == "New Player Onboarding Journey":
            if preferences.get("pacing") == "moderate":
                base_score += 0.3
            if preferences.get("interaction_frequency") == "high":
                base_score += 0.2

        elif scenario.name == "Character Development Journey":
            if "character_development" in preferences.get("narrative_style", ""):
                base_score += 0.5

        # Adjust for technical issues
        if result.error_count > 0:
            base_score -= result.error_count * 0.4

        return max(1.0, min(10.0, base_score))

    async def _calculate_therapeutic_integration_score(
        self, result: TestResult, profile: TestProfile
    ) -> float:
        """Calculate therapeutic integration score focusing on subtlety."""
        base_score = 7.5  # Start high as this is critical

        # Therapeutic integration should be subtle and natural
        therapeutic_profile = profile.therapeutic_profile

        # Adjust based on intensity preferences
        preferred_intensity = therapeutic_profile.get("preferred_intensity", "medium")
        if preferred_intensity == "low":
            base_score += 0.3  # Reward subtlety for low-intensity preferences
        elif preferred_intensity == "high":
            base_score += 0.1  # Still reward but less for high-intensity

        # Penalize for errors in therapeutic scenarios
        if result.error_count > 0:
            base_score -= (
                result.error_count * 0.6
            )  # Higher penalty for therapeutic errors

        return max(1.0, min(10.0, base_score))

    async def _calculate_technical_performance_score(self, result: TestResult) -> float:
        """Calculate technical performance score based on response times, errors, etc."""
        base_score = 8.0

        # Response time scoring
        if result.response_times:
            avg_response_time = sum(result.response_times) / len(result.response_times)
            if avg_response_time <= 1.0:
                base_score += 1.0  # Excellent response time
            elif avg_response_time <= 2.0:
                base_score += 0.5  # Good response time
            elif avg_response_time <= 3.0:
                base_score += 0.0  # Acceptable response time
            else:
                base_score -= 1.0  # Poor response time

        # Error penalty
        base_score -= result.error_count * 1.0

        return max(1.0, min(10.0, base_score))

    def _generate_appearance_from_profile(self, profile: TestProfile):
        """Generate character appearance based on profile."""
        # This would create appropriate appearance based on profile demographics
        # For now, return a basic appearance structure
        return {
            "description": f"A character representing {profile.demographics.get('age_range', 'adult')} demographic",
            "avatar_url": None,
        }

    def _generate_background_from_profile(self, profile: TestProfile):
        """Generate character background based on profile."""
        therapeutic_profile = profile.therapeutic_profile
        return {
            "personality_traits": ["curious", "thoughtful"],
            "core_values": ["growth", "authenticity"],
            "life_experiences": therapeutic_profile.get("comfort_zones", []),
            "goals": ["personal_development", "meaningful_connections"],
        }

    def _generate_therapeutic_profile_from_profile(self, profile: TestProfile):
        """Generate therapeutic profile based on test profile."""
        therapeutic_config = profile.therapeutic_profile
        return {
            "primary_concerns": therapeutic_config.get("primary_concerns", []),
            "preferred_intensity": therapeutic_config.get(
                "preferred_intensity", "medium"
            ),
            "comfort_zones": therapeutic_config.get("comfort_zones", []),
            "challenge_areas": therapeutic_config.get("challenge_areas", []),
            "therapeutic_goals": [],
            "readiness_level": 0.7,
        }

    async def _generate_analysis(self) -> dict[str, Any]:
        """Generate comprehensive analysis of all test results."""
        if not self.results:
            return {"error": "No test results available for analysis"}

        analysis = {
            "summary": self._generate_summary_statistics(),
            "model_comparison": self._generate_model_comparison(),
            "profile_analysis": self._generate_profile_analysis(),
            "scenario_analysis": self._generate_scenario_analysis(),
            "recommendations": self._generate_recommendations(),
            "detailed_results": [
                self._serialize_result(result) for result in self.results
            ],
        }

        return analysis

    def _generate_summary_statistics(self) -> dict[str, Any]:
        """Generate summary statistics across all tests."""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.error_count == 0])

        # Calculate average scores
        overall_scores = [
            r.overall_score for r in self.results if r.overall_score is not None
        ]
        narrative_scores = [
            r.narrative_quality_score
            for r in self.results
            if r.narrative_quality_score is not None
        ]
        engagement_scores = [
            r.user_engagement_score
            for r in self.results
            if r.user_engagement_score is not None
        ]
        therapeutic_scores = [
            r.therapeutic_integration_score
            for r in self.results
            if r.therapeutic_integration_score is not None
        ]
        technical_scores = [
            r.technical_performance_score
            for r in self.results
            if r.technical_performance_score is not None
        ]

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "average_scores": {
                "overall": sum(overall_scores) / len(overall_scores)
                if overall_scores
                else 0,
                "narrative_quality": sum(narrative_scores) / len(narrative_scores)
                if narrative_scores
                else 0,
                "user_engagement": sum(engagement_scores) / len(engagement_scores)
                if engagement_scores
                else 0,
                "therapeutic_integration": sum(therapeutic_scores)
                / len(therapeutic_scores)
                if therapeutic_scores
                else 0,
                "technical_performance": sum(technical_scores) / len(technical_scores)
                if technical_scores
                else 0,
            },
            "total_duration_hours": sum([r.duration_seconds or 0 for r in self.results])
            / 3600,
        }

    def _generate_model_comparison(self) -> dict[str, Any]:
        """Generate detailed model comparison analysis."""
        model_results = {}

        for result in self.results:
            model_name = result.model_name
            if model_name not in model_results:
                model_results[model_name] = []
            model_results[model_name].append(result)

        comparison = {}
        for model_name, results in model_results.items():
            scores = {
                "overall": [
                    r.overall_score for r in results if r.overall_score is not None
                ],
                "narrative_quality": [
                    r.narrative_quality_score
                    for r in results
                    if r.narrative_quality_score is not None
                ],
                "user_engagement": [
                    r.user_engagement_score
                    for r in results
                    if r.user_engagement_score is not None
                ],
                "therapeutic_integration": [
                    r.therapeutic_integration_score
                    for r in results
                    if r.therapeutic_integration_score is not None
                ],
                "technical_performance": [
                    r.technical_performance_score
                    for r in results
                    if r.technical_performance_score is not None
                ],
            }

            comparison[model_name] = {
                "test_count": len(results),
                "success_rate": len([r for r in results if r.error_count == 0])
                / len(results),
                "average_scores": {
                    dimension: sum(score_list) / len(score_list) if score_list else 0
                    for dimension, score_list in scores.items()
                },
                "average_response_time": sum(
                    [
                        sum(r.response_times) / len(r.response_times)
                        if r.response_times
                        else 0
                        for r in results
                    ]
                )
                / len(results),
                "total_errors": sum([r.error_count for r in results]),
                "strengths": self._identify_model_strengths(results),
                "weaknesses": self._identify_model_weaknesses(results),
            }

        return comparison

    def _identify_model_strengths(self, results: list[TestResult]) -> list[str]:
        """Identify strengths of a model based on test results."""
        strengths = []

        # Calculate average scores
        avg_narrative = sum(
            [r.narrative_quality_score for r in results if r.narrative_quality_score]
        ) / len(results)
        avg_engagement = sum(
            [r.user_engagement_score for r in results if r.user_engagement_score]
        ) / len(results)
        avg_therapeutic = sum(
            [
                r.therapeutic_integration_score
                for r in results
                if r.therapeutic_integration_score
            ]
        ) / len(results)
        avg_technical = sum(
            [
                r.technical_performance_score
                for r in results
                if r.technical_performance_score
            ]
        ) / len(results)

        if avg_narrative >= 8.0:
            strengths.append("Excellent narrative quality")
        if avg_engagement >= 8.0:
            strengths.append("High user engagement")
        if avg_therapeutic >= 8.0:
            strengths.append("Subtle therapeutic integration")
        if avg_technical >= 8.0:
            strengths.append("Strong technical performance")

        # Check response times
        avg_response_time = sum(
            [
                sum(r.response_times) / len(r.response_times) if r.response_times else 0
                for r in results
            ]
        ) / len(results)

        if avg_response_time <= 1.0:
            strengths.append("Fast response times")

        return strengths

    def _identify_model_weaknesses(self, results: list[TestResult]) -> list[str]:
        """Identify weaknesses of a model based on test results."""
        weaknesses = []

        # Calculate average scores
        avg_narrative = sum(
            [r.narrative_quality_score for r in results if r.narrative_quality_score]
        ) / len(results)
        avg_engagement = sum(
            [r.user_engagement_score for r in results if r.user_engagement_score]
        ) / len(results)
        avg_therapeutic = sum(
            [
                r.therapeutic_integration_score
                for r in results
                if r.therapeutic_integration_score
            ]
        ) / len(results)
        avg_technical = sum(
            [
                r.technical_performance_score
                for r in results
                if r.technical_performance_score
            ]
        ) / len(results)

        if avg_narrative < 6.0:
            weaknesses.append("Poor narrative quality")
        if avg_engagement < 6.0:
            weaknesses.append("Low user engagement")
        if avg_therapeutic < 6.0:
            weaknesses.append("Inadequate therapeutic integration")
        if avg_technical < 6.0:
            weaknesses.append("Technical performance issues")

        # Check error rates
        total_errors = sum([r.error_count for r in results])
        if total_errors > len(results) * 0.1:  # More than 10% error rate
            weaknesses.append("High error rate")

        return weaknesses

    def _generate_profile_analysis(self) -> dict[str, Any]:
        """Generate analysis by test profile."""
        profile_results = {}

        for result in self.results:
            profile_name = result.profile_name
            if profile_name not in profile_results:
                profile_results[profile_name] = []
            profile_results[profile_name].append(result)

        analysis = {}
        for profile_name, results in profile_results.items():
            avg_overall = sum(
                [r.overall_score for r in results if r.overall_score]
            ) / len(results)
            best_model = max(results, key=lambda r: r.overall_score or 0)

            analysis[profile_name] = {
                "test_count": len(results),
                "average_overall_score": avg_overall,
                "best_performing_model": best_model.model_name,
                "best_model_score": best_model.overall_score,
                "profile_specific_insights": self._generate_profile_insights(
                    profile_name, results
                ),
            }

        return analysis

    def _generate_scenario_analysis(self) -> dict[str, Any]:
        """Generate analysis by test scenario."""
        scenario_results = {}

        for result in self.results:
            scenario_name = result.scenario_name
            if scenario_name not in scenario_results:
                scenario_results[scenario_name] = []
            scenario_results[scenario_name].append(result)

        analysis = {}
        for scenario_name, results in scenario_results.items():
            avg_overall = sum(
                [r.overall_score for r in results if r.overall_score]
            ) / len(results)
            best_model = max(results, key=lambda r: r.overall_score or 0)

            analysis[scenario_name] = {
                "test_count": len(results),
                "average_overall_score": avg_overall,
                "best_performing_model": best_model.model_name,
                "best_model_score": best_model.overall_score,
                "scenario_specific_challenges": self._identify_scenario_challenges(
                    scenario_name, results
                ),
            }

        return analysis

    def _generate_profile_insights(
        self, profile_name: str, results: list[TestResult]
    ) -> list[str]:
        """Generate insights specific to a test profile."""
        insights = []

        # Analyze performance patterns for this profile
        avg_engagement = sum(
            [r.user_engagement_score for r in results if r.user_engagement_score]
        ) / len(results)
        avg_therapeutic = sum(
            [
                r.therapeutic_integration_score
                for r in results
                if r.therapeutic_integration_score
            ]
        ) / len(results)

        if "anxiety" in profile_name.lower():
            if avg_therapeutic >= 8.0:
                insights.append(
                    "Models handle anxiety-related content with appropriate sensitivity"
                )
            else:
                insights.append(
                    "Models may need improvement in anxiety-sensitive scenarios"
                )

        if "gaming_enthusiast" in profile_name.lower():
            if avg_engagement >= 8.0:
                insights.append("Models successfully engage gaming-oriented users")
            else:
                insights.append("Models may not fully leverage gaming preferences")

        return insights

    def _identify_scenario_challenges(
        self, scenario_name: str, results: list[TestResult]
    ) -> list[str]:
        """Identify challenges specific to a scenario."""
        challenges = []

        error_rate = sum([r.error_count for r in results]) / len(results)
        if error_rate > 0.5:
            challenges.append("High error rate in this scenario")

        avg_response_time = sum(
            [
                sum(r.response_times) / len(r.response_times) if r.response_times else 0
                for r in results
            ]
        ) / len(results)

        if avg_response_time > 2.0:
            challenges.append("Slow response times for this scenario type")

        return challenges

    def _generate_recommendations(self) -> dict[str, Any]:
        """Generate recommendations based on test results."""
        if not self.results:
            return {}

        # Find best overall model
        best_result = max(self.results, key=lambda r: r.overall_score or 0)

        # Calculate model rankings
        model_scores = {}
        for result in self.results:
            model_name = result.model_name
            if model_name not in model_scores:
                model_scores[model_name] = []
            if result.overall_score is not None:
                model_scores[model_name].append(result.overall_score)

        model_rankings = {}
        for model_name, scores in model_scores.items():
            model_rankings[model_name] = sum(scores) / len(scores) if scores else 0

        sorted_models = sorted(model_rankings.items(), key=lambda x: x[1], reverse=True)

        recommendations = {
            "primary_recommendation": {
                "model": best_result.model_name,
                "overall_score": best_result.overall_score,
                "rationale": f"Achieved highest overall score of {best_result.overall_score:.2f}",
            },
            "model_rankings": [
                {"model": model, "average_score": score, "rank": i + 1}
                for i, (model, score) in enumerate(sorted_models)
            ],
            "use_case_recommendations": self._generate_use_case_recommendations(),
            "implementation_guidelines": self._generate_implementation_guidelines(),
            "areas_for_improvement": self._identify_improvement_areas(),
        }

        return recommendations

    def _generate_use_case_recommendations(self) -> dict[str, str]:
        """Generate model recommendations for specific use cases."""
        recommendations = {}

        # Find best model for each dimension
        best_narrative = max(self.results, key=lambda r: r.narrative_quality_score or 0)
        best_engagement = max(self.results, key=lambda r: r.user_engagement_score or 0)
        best_therapeutic = max(
            self.results, key=lambda r: r.therapeutic_integration_score or 0
        )
        best_technical = max(
            self.results, key=lambda r: r.technical_performance_score or 0
        )

        recommendations["creative_storytelling"] = best_narrative.model_name
        recommendations["user_engagement"] = best_engagement.model_name
        recommendations["therapeutic_integration"] = best_therapeutic.model_name
        recommendations["technical_performance"] = best_technical.model_name

        return recommendations

    def _generate_implementation_guidelines(self) -> list[str]:
        """Generate implementation guidelines based on test results."""
        guidelines = []

        # Analyze response times
        all_response_times = []
        for result in self.results:
            all_response_times.extend(result.response_times)

        if all_response_times:
            avg_response_time = sum(all_response_times) / len(all_response_times)
            if avg_response_time > 2.0:
                guidelines.append(
                    "Consider implementing response caching for improved performance"
                )
            if avg_response_time < 0.5:
                guidelines.append("Fast response times indicate good model efficiency")

        # Analyze error patterns
        total_errors = sum([r.error_count for r in self.results])
        if total_errors > 0:
            guidelines.append("Implement robust error handling and fallback mechanisms")

        # Therapeutic integration insights
        therapeutic_scores = [
            r.therapeutic_integration_score
            for r in self.results
            if r.therapeutic_integration_score
        ]
        if therapeutic_scores:
            avg_therapeutic = sum(therapeutic_scores) / len(therapeutic_scores)
            if avg_therapeutic < 7.0:
                guidelines.append(
                    "Focus on improving subtlety of therapeutic integration"
                )

        return guidelines

    def _identify_improvement_areas(self) -> list[str]:
        """Identify areas needing improvement across all models."""
        areas = []

        # Calculate overall averages
        narrative_scores = [
            r.narrative_quality_score for r in self.results if r.narrative_quality_score
        ]
        engagement_scores = [
            r.user_engagement_score for r in self.results if r.user_engagement_score
        ]
        therapeutic_scores = [
            r.therapeutic_integration_score
            for r in self.results
            if r.therapeutic_integration_score
        ]
        technical_scores = [
            r.technical_performance_score
            for r in self.results
            if r.technical_performance_score
        ]

        target_score = 7.5  # Target threshold

        if (
            narrative_scores
            and sum(narrative_scores) / len(narrative_scores) < target_score
        ):
            areas.append("Narrative quality and creativity")
        if (
            engagement_scores
            and sum(engagement_scores) / len(engagement_scores) < target_score
        ):
            areas.append("User engagement and fun factor")
        if (
            therapeutic_scores
            and sum(therapeutic_scores) / len(therapeutic_scores) < target_score
        ):
            areas.append("Therapeutic integration subtlety")
        if (
            technical_scores
            and sum(technical_scores) / len(technical_scores) < target_score
        ):
            areas.append("Technical performance and reliability")

        return areas

    def _serialize_result(self, result: TestResult) -> dict[str, Any]:
        """Serialize a test result for JSON export."""
        return {
            "test_id": result.test_id,
            "model_name": result.model_name,
            "scenario_name": result.scenario_name,
            "profile_name": result.profile_name,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "duration_seconds": result.duration_seconds,
            "scores": {
                "narrative_quality": result.narrative_quality_score,
                "user_engagement": result.user_engagement_score,
                "therapeutic_integration": result.therapeutic_integration_score,
                "technical_performance": result.technical_performance_score,
                "overall": result.overall_score,
            },
            "metrics": {
                "average_response_time": sum(result.response_times)
                / len(result.response_times)
                if result.response_times
                else 0,
                "error_count": result.error_count,
                "session_continuity_score": result.session_continuity_score,
                "choice_meaningfulness_score": result.choice_meaningfulness_score,
            },
            "qualitative": {
                "strengths": result.strengths,
                "weaknesses": result.weaknesses,
                "notes": result.notes,
                "narrative_examples": result.narrative_examples[:3],  # Limit examples
            },
        }

    async def _save_results(self, analysis: dict[str, Any]):
        """Save test results and analysis to files."""
        results_dir = Path(
            self.config.get("testing", {}).get(
                "results_storage_path", "./testing/results"
            )
        )
        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save comprehensive analysis
        analysis_file = results_dir / f"comprehensive_analysis_{timestamp}.json"
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        # Save raw results
        raw_results_file = results_dir / f"raw_results_{timestamp}.json"
        raw_results = [self._serialize_result(result) for result in self.results]
        with open(raw_results_file, "w") as f:
            json.dump(raw_results, f, indent=2, default=str)

        logger.info(f"Results saved to {results_dir}")
        logger.info(f"Analysis file: {analysis_file}")
        logger.info(f"Raw results file: {raw_results_file}")


# Example usage and testing entry point
async def main():
    """Main entry point for running comprehensive tests."""
    framework = SinglePlayerTestFramework()

    try:
        analysis = await framework.run_comprehensive_test()

        print("\n" + "=" * 80)
        print("TTA SINGLE-PLAYER STORYTELLING EXPERIENCE TEST RESULTS")
        print("=" * 80)

        summary = analysis.get("summary", {})
        print("\nSUMMARY:")
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        print(
            f"Average Overall Score: {summary.get('average_scores', {}).get('overall', 0):.2f}/10"
        )

        recommendations = analysis.get("recommendations", {})
        primary_rec = recommendations.get("primary_recommendation", {})
        print("\nPRIMARY RECOMMENDATION:")
        print(f"Best Model: {primary_rec.get('model', 'N/A')}")
        print(f"Score: {primary_rec.get('overall_score', 0):.2f}/10")

        print("\nDetailed results saved to: testing/results/")

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
