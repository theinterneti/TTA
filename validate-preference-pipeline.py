#!/usr/bin/env python3
"""
TTA Player Preference Configuration and AI Processing Pipeline Validation

This focused validation examines:
1. Current AI processing pipeline in enhanced_api_server.py
2. Player preference configuration opportunities
3. AI logic pre-processing enhancement recommendations
4. Integration points for personalized therapeutic experiences
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PreferencePipelineValidator:
    """Validates current AI pipeline and identifies preference integration opportunities."""

    def __init__(self):
        self.validation_results = {}
        self.recommendations = []

    def run_validation(self) -> dict[str, Any]:
        """Run comprehensive preference pipeline validation."""
        logger.info("🚀 TTA PREFERENCE PIPELINE VALIDATION")
        logger.info("=" * 50)

        # Phase 1: Environment Configuration Analysis
        logger.info("\n🔧 PHASE 1: ENVIRONMENT CONFIGURATION ANALYSIS")
        env_results = self._analyze_environment_configuration()
        self.validation_results["environment_config"] = env_results

        # Phase 2: Current AI Pipeline Analysis
        logger.info("\n🧠 PHASE 2: CURRENT AI PIPELINE ANALYSIS")
        pipeline_results = self._analyze_current_ai_pipeline()
        self.validation_results["current_pipeline"] = pipeline_results

        # Phase 3: Player Preference Integration Opportunities
        logger.info("\n👤 PHASE 3: PREFERENCE INTEGRATION OPPORTUNITIES")
        integration_results = self._identify_integration_opportunities()
        self.validation_results["integration_opportunities"] = integration_results

        # Phase 4: AI Logic Pre-Processing Enhancement
        logger.info("\n⚡ PHASE 4: PRE-PROCESSING ENHANCEMENT ANALYSIS")
        preprocessing_results = self._analyze_preprocessing_enhancements()
        self.validation_results["preprocessing_enhancements"] = preprocessing_results

        # Phase 5: Generate Recommendations
        logger.info("\n📋 PHASE 5: GENERATING RECOMMENDATIONS")
        self._generate_recommendations()

        # Generate final report
        self._generate_final_report()

        return self.validation_results

    def _analyze_environment_configuration(self) -> dict[str, Any]:
        """Analyze current environment configuration for player preferences."""
        results = {
            "env_file_exists": False,
            "therapeutic_settings": {},
            "model_preferences": {},
            "feature_flags": {},
            "missing_configurations": [],
        }

        # Check if .env file exists
        env_path = ".env"
        if os.path.exists(env_path):
            results["env_file_exists"] = True
            logger.info("✅ .env file found")

            # Read and analyze .env file
            with open(env_path) as f:
                env_content = f.read()

            # Extract therapeutic settings
            therapeutic_patterns = {
                "DEFAULT_THERAPEUTIC_INTENSITY": r"DEFAULT_THERAPEUTIC_INTENSITY=(\w+)",
                "THERAPEUTIC_SAFETY_THRESHOLD": r"THERAPEUTIC_SAFETY_THRESHOLD=([\d.]+)",
                "SESSION_TIMEOUT_MINUTES": r"SESSION_TIMEOUT_MINUTES=(\d+)",
                "MAX_CONCURRENT_SESSIONS": r"MAX_CONCURRENT_SESSIONS=(\d+)",
            }

            for setting, pattern in therapeutic_patterns.items():
                match = re.search(pattern, env_content)
                if match:
                    results["therapeutic_settings"][setting] = match.group(1)
                    logger.info(f"✅ Found {setting}: {match.group(1)}")
                else:
                    results["missing_configurations"].append(setting)
                    logger.warning(f"⚠️ Missing {setting}")

            # Extract model preferences
            model_patterns = {
                "OPENROUTER_PREFER_FREE_MODELS": r"OPENROUTER_PREFER_FREE_MODELS=(\w+)",
                "OPENROUTER_MAX_COST_PER_TOKEN": r"OPENROUTER_MAX_COST_PER_TOKEN=([\d.]+)",
            }

            for setting, pattern in model_patterns.items():
                match = re.search(pattern, env_content)
                if match:
                    results["model_preferences"][setting] = match.group(1)
                    logger.info(f"✅ Found {setting}: {match.group(1)}")
                else:
                    results["missing_configurations"].append(setting)

            # Extract feature flags
            feature_patterns = {
                "FEATURE_AI_NARRATIVE": r"FEATURE_AI_NARRATIVE=(\w+)",
                "CRISIS_DETECTION_ENABLED": r"CRISIS_DETECTION_ENABLED=(\w+)",
            }

            for setting, pattern in feature_patterns.items():
                match = re.search(pattern, env_content)
                if match:
                    results["feature_flags"][setting] = match.group(1)
                    logger.info(f"✅ Found {setting}: {match.group(1)}")
                else:
                    results["missing_configurations"].append(setting)
        else:
            logger.error("❌ .env file not found")
            results["missing_configurations"].append("ENV_FILE")

        return results

    def _analyze_current_ai_pipeline(self) -> dict[str, Any]:
        """Analyze the current AI processing pipeline in enhanced_api_server.py."""
        results = {
            "server_file_exists": False,
            "ai_generator_class": False,
            "therapeutic_prompt_method": False,
            "enhanced_response_method": False,
            "context_processing": {},
            "personalization_features": [],
            "limitations": [],
        }

        server_path = "enhanced_api_server.py"
        if os.path.exists(server_path):
            results["server_file_exists"] = True
            logger.info("✅ enhanced_api_server.py found")

            with open(server_path) as f:
                server_content = f.read()

            # Check for AI generator class
            if "class TherapeuticAIGenerator" in server_content:
                results["ai_generator_class"] = True
                logger.info("✅ TherapeuticAIGenerator class found")

            # Check for therapeutic prompt method
            if "_create_therapeutic_prompt" in server_content:
                results["therapeutic_prompt_method"] = True
                logger.info("✅ _create_therapeutic_prompt method found")

                # Analyze prompt creation logic
                prompt_match = re.search(
                    r"def _create_therapeutic_prompt\(self, user_message: str, context: Dict\) -> str:(.*?)def ",
                    server_content,
                    re.DOTALL,
                )
                if prompt_match:
                    prompt_code = prompt_match.group(1)

                    # Check what context variables are used
                    context_vars = re.findall(r"context\.get\('(\w+)'", prompt_code)
                    results["context_processing"]["variables_used"] = context_vars
                    logger.info(f"📊 Context variables used: {context_vars}")

                    # Check for personalization features
                    if "character_name" in context_vars:
                        results["personalization_features"].append("character_name")
                    if "setting" in context_vars:
                        results["personalization_features"].append("setting")
                    if "turn_count" in context_vars:
                        results["personalization_features"].append("turn_count")

            # Check for enhanced response method
            if "_generate_enhanced_therapeutic_response" in server_content:
                results["enhanced_response_method"] = True
                logger.info("✅ _generate_enhanced_therapeutic_response method found")

                # Analyze enhanced response logic
                enhanced_match = re.search(
                    r"def _generate_enhanced_therapeutic_response\(self, user_message: str, context: Dict\) -> str:(.*?)# Initialize AI generator",
                    server_content,
                    re.DOTALL,
                )
                if enhanced_match:
                    enhanced_code = enhanced_match.group(1)

                    # Check for emotional analysis
                    if "anxiety_keywords" in enhanced_code:
                        results["personalization_features"].append("anxiety_detection")
                    if "calm_keywords" in enhanced_code:
                        results["personalization_features"].append("calm_detection")
                    if "exploration_keywords" in enhanced_code:
                        results["personalization_features"].append(
                            "exploration_detection"
                        )
                    if "nature_keywords" in enhanced_code:
                        results["personalization_features"].append("nature_detection")

            # Identify limitations
            if "intensity_level" not in server_content:
                results["limitations"].append("No therapeutic intensity customization")
            if "therapeutic_goals" not in server_content:
                results["limitations"].append("No therapeutic goals integration")
            if "conversation_style" not in server_content:
                results["limitations"].append("No conversation style adaptation")
            if "player_preferences" not in server_content:
                results["limitations"].append("No player preference system")

            logger.info(
                f"📊 Current personalization features: {results['personalization_features']}"
            )
            logger.info(f"⚠️ Identified limitations: {results['limitations']}")
        else:
            logger.error("❌ enhanced_api_server.py not found")

        return results

    def _identify_integration_opportunities(self) -> dict[str, Any]:
        """Identify opportunities for player preference integration."""
        results = {
            "prompt_enhancement_opportunities": [],
            "context_enrichment_opportunities": [],
            "response_personalization_opportunities": [],
            "new_features_needed": [],
        }

        # Prompt enhancement opportunities
        results["prompt_enhancement_opportunities"] = [
            {
                "feature": "Therapeutic Intensity Adaptation",
                "description": "Adapt prompt language and approach based on user's preferred intensity level",
                "implementation": "Add intensity_level to context and modify prompt guidelines accordingly",
                "priority": "High",
            },
            {
                "feature": "Therapeutic Approach Integration",
                "description": "Include user's preferred therapeutic approaches (CBT, mindfulness, etc.) in prompt",
                "implementation": "Add preferred_approaches to context and include approach-specific guidance",
                "priority": "High",
            },
            {
                "feature": "Conversation Style Customization",
                "description": "Adapt conversation tone and style based on user preferences",
                "implementation": "Add conversation_style to context and modify response tone accordingly",
                "priority": "Medium",
            },
        ]

        # Context enrichment opportunities
        results["context_enrichment_opportunities"] = [
            {
                "feature": "Therapeutic Goals Context",
                "description": "Include user's therapeutic goals in processing context",
                "implementation": "Add therapeutic_goals array to context for goal-aligned responses",
                "priority": "High",
            },
            {
                "feature": "Emotional State Tracking",
                "description": "Track user's emotional progression across sessions",
                "implementation": "Add emotional_history to context for continuity",
                "priority": "Medium",
            },
            {
                "feature": "Trigger Topic Awareness",
                "description": "Include user's trigger topics and comfort zones in context",
                "implementation": "Add trigger_topics and comfort_topics to context for safe responses",
                "priority": "High",
            },
        ]

        # Response personalization opportunities
        results["response_personalization_opportunities"] = [
            {
                "feature": "Intensity-Based Response Selection",
                "description": "Select response complexity and directness based on user's intensity preference",
                "implementation": "Modify response selection logic to consider intensity_level",
                "priority": "High",
            },
            {
                "feature": "Goal-Aligned Content",
                "description": "Prioritize content that aligns with user's therapeutic goals",
                "implementation": "Weight response selection based on therapeutic_goals",
                "priority": "Medium",
            },
            {
                "feature": "Cultural and Personal Adaptation",
                "description": "Adapt responses based on user's cultural background and personal preferences",
                "implementation": "Add cultural_preferences and personal_style to context",
                "priority": "Low",
            },
        ]

        # New features needed
        results["new_features_needed"] = [
            {
                "feature": "Player Preference Storage",
                "description": "System to store and retrieve player preferences",
                "implementation": "Database schema and API endpoints for preference management",
                "priority": "Critical",
            },
            {
                "feature": "Preference-Aware Context Builder",
                "description": "Service to build enriched context from user preferences",
                "implementation": "PreferenceContextBuilder class with preference integration logic",
                "priority": "Critical",
            },
            {
                "feature": "Adaptive Prompt Engine",
                "description": "Dynamic prompt generation based on user preferences",
                "implementation": "AdaptivePromptEngine class with template-based prompt construction",
                "priority": "High",
            },
        ]

        logger.info(
            f"📊 Identified {len(results['prompt_enhancement_opportunities'])} prompt enhancement opportunities"
        )
        logger.info(
            f"📊 Identified {len(results['context_enrichment_opportunities'])} context enrichment opportunities"
        )
        logger.info(
            f"📊 Identified {len(results['response_personalization_opportunities'])} response personalization opportunities"
        )
        logger.info(
            f"📊 Identified {len(results['new_features_needed'])} new features needed"
        )

        return results

    def _analyze_preprocessing_enhancements(self) -> dict[str, Any]:
        """Analyze potential AI logic pre-processing enhancements."""
        results = {
            "current_preprocessing": [],
            "enhancement_opportunities": [],
            "implementation_recommendations": [],
        }

        # Current preprocessing analysis
        results["current_preprocessing"] = [
            {
                "feature": "Keyword-based Emotional Analysis",
                "description": "Basic emotion detection using keyword matching",
                "effectiveness": "Medium",
                "limitations": [
                    "Limited emotional vocabulary",
                    "No context consideration",
                    "Binary detection",
                ],
            },
            {
                "feature": "Turn-based Response Selection",
                "description": "Response selection based on conversation turn count",
                "effectiveness": "Low",
                "limitations": [
                    "No user state consideration",
                    "Linear progression assumption",
                ],
            },
            {
                "feature": "Basic Context Variables",
                "description": "Simple context variables (character_name, setting, turn_count)",
                "effectiveness": "Low",
                "limitations": [
                    "No personalization",
                    "Static context",
                    "No preference integration",
                ],
            },
        ]

        # Enhancement opportunities
        results["enhancement_opportunities"] = [
            {
                "enhancement": "Advanced Emotional Analysis",
                "description": "Multi-dimensional emotional state analysis with intensity scoring",
                "benefits": [
                    "More nuanced emotional understanding",
                    "Better therapeutic alignment",
                    "Improved response relevance",
                ],
                "implementation_complexity": "Medium",
            },
            {
                "enhancement": "Contextual Memory System",
                "description": "Session and cross-session context memory for continuity",
                "benefits": [
                    "Therapeutic continuity",
                    "Progress tracking",
                    "Personalized experience",
                ],
                "implementation_complexity": "High",
            },
            {
                "enhancement": "Preference-Driven Processing",
                "description": "Pre-processing pipeline that adapts based on user preferences",
                "benefits": [
                    "Personalized therapeutic approach",
                    "Better user engagement",
                    "Improved outcomes",
                ],
                "implementation_complexity": "High",
            },
            {
                "enhancement": "Crisis Detection Integration",
                "description": "Advanced crisis detection with appropriate response protocols",
                "benefits": [
                    "User safety",
                    "Professional standards",
                    "Risk mitigation",
                ],
                "implementation_complexity": "High",
            },
        ]

        # Implementation recommendations
        results["implementation_recommendations"] = [
            {
                "phase": "Phase 1: Foundation",
                "timeline": "1-2 weeks",
                "features": [
                    "Player preference data models",
                    "Basic preference storage system",
                    "Enhanced context builder",
                ],
            },
            {
                "phase": "Phase 2: Integration",
                "timeline": "2-3 weeks",
                "features": [
                    "Preference-aware prompt generation",
                    "Intensity-based response adaptation",
                    "Therapeutic goal alignment",
                ],
            },
            {
                "phase": "Phase 3: Advanced Features",
                "timeline": "3-4 weeks",
                "features": [
                    "Contextual memory system",
                    "Advanced emotional analysis",
                    "Crisis detection integration",
                ],
            },
        ]

        logger.info(
            f"📊 Current preprocessing features: {len(results['current_preprocessing'])}"
        )
        logger.info(
            f"📊 Enhancement opportunities: {len(results['enhancement_opportunities'])}"
        )
        logger.info(
            f"📊 Implementation phases: {len(results['implementation_recommendations'])}"
        )

        return results

    def _generate_recommendations(self):
        """Generate comprehensive recommendations based on analysis."""
        self.recommendations = [
            {
                "category": "Critical Priority",
                "recommendations": [
                    {
                        "title": "Implement Player Preference System",
                        "description": "Create comprehensive player preference storage and retrieval system",
                        "rationale": "Foundation for all personalization features",
                        "implementation": "Add preference models, database schema, and API endpoints",
                        "estimated_effort": "1-2 weeks",
                    },
                    {
                        "title": "Enhance Context Processing",
                        "description": "Expand context processing to include player preferences and therapeutic goals",
                        "rationale": "Enable personalized AI processing pipeline",
                        "implementation": "Modify _create_therapeutic_prompt to use preference-enriched context",
                        "estimated_effort": "1 week",
                    },
                ],
            },
            {
                "category": "High Priority",
                "recommendations": [
                    {
                        "title": "Implement Therapeutic Intensity Adaptation",
                        "description": "Adapt AI responses based on user's preferred therapeutic intensity",
                        "rationale": "Ensure therapeutic approach matches user comfort level",
                        "implementation": "Add intensity-based prompt modification and response selection",
                        "estimated_effort": "1 week",
                    },
                    {
                        "title": "Add Therapeutic Approach Integration",
                        "description": "Include user's preferred therapeutic approaches in AI processing",
                        "rationale": "Align AI responses with user's therapeutic preferences",
                        "implementation": "Modify prompt generation to include approach-specific guidance",
                        "estimated_effort": "1 week",
                    },
                ],
            },
            {
                "category": "Medium Priority",
                "recommendations": [
                    {
                        "title": "Implement Advanced Emotional Analysis",
                        "description": "Replace keyword-based emotion detection with sophisticated analysis",
                        "rationale": "Improve therapeutic response accuracy and relevance",
                        "implementation": "Develop multi-dimensional emotional state analysis system",
                        "estimated_effort": "2-3 weeks",
                    },
                    {
                        "title": "Add Session Continuity Features",
                        "description": "Implement cross-session context memory for therapeutic continuity",
                        "rationale": "Provide consistent therapeutic experience across sessions",
                        "implementation": "Develop session state management and context persistence",
                        "estimated_effort": "2-3 weeks",
                    },
                ],
            },
        ]

        logger.info("📋 Generated comprehensive recommendations")
        for category in self.recommendations:
            logger.info(
                f"   {category['category']}: {len(category['recommendations'])} recommendations"
            )

    def _generate_final_report(self):
        """Generate comprehensive final report."""
        logger.info("\n" + "=" * 50)
        logger.info("🏁 PREFERENCE PIPELINE VALIDATION COMPLETE")
        logger.info("=" * 50)

        # Summary of current state
        logger.info("\n📊 CURRENT STATE SUMMARY:")
        env_config = self.validation_results.get("environment_config", {})
        current_pipeline = self.validation_results.get("current_pipeline", {})

        logger.info(
            f"   Environment Configuration: {'✅ Configured' if env_config.get('env_file_exists') else '❌ Missing'}"
        )
        logger.info(
            f"   AI Pipeline: {'✅ Present' if current_pipeline.get('ai_generator_class') else '❌ Missing'}"
        )
        logger.info(
            f"   Personalization Features: {len(current_pipeline.get('personalization_features', []))}"
        )
        logger.info(
            f"   Identified Limitations: {len(current_pipeline.get('limitations', []))}"
        )

        # Integration opportunities summary
        integration_ops = self.validation_results.get("integration_opportunities", {})
        logger.info("\n🎯 INTEGRATION OPPORTUNITIES:")
        logger.info(
            f"   Prompt Enhancement: {len(integration_ops.get('prompt_enhancement_opportunities', []))}"
        )
        logger.info(
            f"   Context Enrichment: {len(integration_ops.get('context_enrichment_opportunities', []))}"
        )
        logger.info(
            f"   Response Personalization: {len(integration_ops.get('response_personalization_opportunities', []))}"
        )
        logger.info(
            f"   New Features Needed: {len(integration_ops.get('new_features_needed', []))}"
        )

        # Recommendations summary
        logger.info("\n📋 RECOMMENDATIONS SUMMARY:")
        for category in self.recommendations:
            logger.info(
                f"   {category['category']}: {len(category['recommendations'])} items"
            )

        # Overall assessment
        logger.info("\n🎯 OVERALL ASSESSMENT:")

        # Calculate readiness score
        readiness_factors = [
            env_config.get("env_file_exists", False),
            current_pipeline.get("ai_generator_class", False),
            current_pipeline.get("therapeutic_prompt_method", False),
            current_pipeline.get("enhanced_response_method", False),
            len(current_pipeline.get("personalization_features", [])) > 0,
        ]

        readiness_score = sum(readiness_factors) / len(readiness_factors)

        if readiness_score >= 0.8:
            logger.info("🎉 EXCELLENT: Strong foundation for preference integration")
            logger.info("✅ Ready for advanced personalization features")
        elif readiness_score >= 0.6:
            logger.info("✅ GOOD: Solid foundation with some enhancements needed")
            logger.info("⚠️ Focus on critical priority recommendations")
        else:
            logger.info(
                "⚠️ NEEDS DEVELOPMENT: Significant work needed for preference integration"
            )
            logger.info("🔧 Start with foundation-level implementations")

        logger.info(f"📊 Readiness Score: {readiness_score:.1f}/1.0")

        # Save detailed results
        output_data = {
            "validation_timestamp": datetime.now().isoformat(),
            "readiness_score": readiness_score,
            "validation_results": self.validation_results,
            "recommendations": self.recommendations,
        }

        with open("preference_pipeline_validation.json", "w") as f:
            json.dump(output_data, f, indent=2)

        logger.info(
            "\n💾 Detailed results saved to: preference_pipeline_validation.json"
        )


def main():
    """Main validation execution."""
    validator = PreferencePipelineValidator()
    results = validator.run_validation()

    return results


if __name__ == "__main__":
    main()
