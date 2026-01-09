#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Seed_worlds]]
Seed therapeutic worlds into Neo4j database.

This script populates the database with 5 sample therapeutic worlds
covering different therapeutic approaches and difficulty levels.
"""

import logging
import sys
from datetime import timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from player_experience.database.world_repository import WorldRepository
from player_experience.models.enums import DifficultyLevel, TherapeuticApproach
from player_experience.models.world import WorldDetails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_worlds() -> list[WorldDetails]:
    """Create 5 sample therapeutic worlds."""
    worlds = []

    # 1. Mindfulness Garden (Beginner, Mindfulness + CBT)
    worlds.append(
        WorldDetails(
            world_id="world_mindfulness_garden",
            name="Mindfulness Garden",
            description="A peaceful garden environment focused on mindfulness and present-moment awareness",
            long_description="Step into a serene garden where time moves slowly and every breath brings deeper awareness. This therapeutic environment is designed to help you develop mindfulness skills through gentle exploration and contemplative activities.",
            therapeutic_themes=[
                "mindfulness",
                "stress_reduction",
                "present_moment_awareness",
            ],
            therapeutic_approaches=[
                TherapeuticApproach.MINDFULNESS,
                TherapeuticApproach.CBT,
            ],
            difficulty_level=DifficultyLevel.BEGINNER,
            estimated_duration=timedelta(hours=1, minutes=30),
            setting_description="A beautiful garden with winding paths, meditation spots, and gentle water features",
            key_characters=[
                {
                    "name": "Sage",
                    "role": "Mindfulness Guide",
                    "description": "A gentle guide who teaches mindfulness techniques",
                }
            ],
            main_storylines=[
                "Learning to observe thoughts without judgment",
                "Discovering the power of present-moment awareness",
                "Building a daily mindfulness practice",
            ],
            therapeutic_techniques_used=[
                "breathing_meditation",
                "body_scan",
                "mindful_walking",
                "loving_kindness",
            ],
            recommended_therapeutic_readiness=0.3,
            content_warnings=[],
            player_count=0,
            average_rating=0.0,
            completion_rate=0.0,
            therapeutic_effectiveness_score=0.0,
        )
    )

    # 2. Anxiety Challenge Course (Intermediate, CBT + Behavioral Activation)
    worlds.append(
        WorldDetails(
            world_id="world_anxiety_challenge",
            name="Anxiety Challenge Course",
            description="A structured environment for learning to manage anxiety through gradual exposure",
            long_description="Navigate through carefully designed challenges that help you build confidence and develop effective anxiety management strategies. Each challenge is tailored to your comfort level and therapeutic goals.",
            therapeutic_themes=[
                "anxiety_management",
                "gradual_exposure",
                "confidence_building",
            ],
            therapeutic_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.BEHAVIORAL_ACTIVATION,
            ],
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            estimated_duration=timedelta(hours=2),
            setting_description="A series of interconnected spaces representing different anxiety-provoking scenarios",
            key_characters=[
                {
                    "name": "Coach Alex",
                    "role": "Anxiety Coach",
                    "description": "A supportive coach who helps you face challenges at your own pace",
                }
            ],
            main_storylines=[
                "Understanding your anxiety triggers",
                "Developing coping strategies",
                "Building resilience through practice",
            ],
            therapeutic_techniques_used=[
                "cognitive_restructuring",
                "exposure_therapy",
                "relaxation_techniques",
                "behavioral_experiments",
            ],
            recommended_therapeutic_readiness=0.5,
            content_warnings=["anxiety-inducing scenarios"],
            player_count=0,
            average_rating=0.0,
            completion_rate=0.0,
            therapeutic_effectiveness_score=0.0,
        )
    )

    # 3. Social Skills Village (Intermediate, DBT + Humanistic)
    worlds.append(
        WorldDetails(
            world_id="world_social_skills",
            name="Social Skills Village",
            description="A vibrant community where you can practice and develop social interaction skills",
            long_description="Explore a welcoming village filled with diverse characters and social situations. Practice communication, empathy, and relationship-building in a safe, supportive environment.",
            therapeutic_themes=[
                "social_skills",
                "communication",
                "empathy_development",
                "relationship_building",
            ],
            therapeutic_approaches=[
                TherapeuticApproach.DIALECTICAL_BEHAVIORAL,
                TherapeuticApproach.HUMANISTIC,
            ],
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            estimated_duration=timedelta(hours=2, minutes=30),
            setting_description="A bustling village with a town square, marketplace, community center, and various social gathering spots",
            key_characters=[
                {
                    "name": "Maya",
                    "role": "Social Coordinator",
                    "description": "A friendly guide who helps you navigate social situations",
                },
                {
                    "name": "Various Villagers",
                    "role": "Practice Partners",
                    "description": "Diverse characters representing different social scenarios",
                },
            ],
            main_storylines=[
                "Learning effective communication techniques",
                "Building meaningful connections",
                "Navigating conflict resolution",
            ],
            therapeutic_techniques_used=[
                "interpersonal_effectiveness",
                "active_listening",
                "assertiveness_training",
                "emotion_regulation",
            ],
            recommended_therapeutic_readiness=0.6,
            content_warnings=[],
            player_count=0,
            average_rating=0.0,
            completion_rate=0.0,
            therapeutic_effectiveness_score=0.0,
        )
    )

    # 4. Emotional Regulation Sanctuary (Advanced, DBT + ACT)
    worlds.append(
        WorldDetails(
            world_id="world_emotional_regulation",
            name="Emotional Regulation Sanctuary",
            description="An advanced environment for mastering emotional regulation and distress tolerance",
            long_description="Enter a transformative space designed to help you understand, accept, and skillfully manage intense emotions. This sanctuary provides tools and practices for building emotional resilience.",
            therapeutic_themes=[
                "emotional_regulation",
                "distress_tolerance",
                "acceptance",
                "mindful_awareness",
            ],
            therapeutic_approaches=[
                TherapeuticApproach.DIALECTICAL_BEHAVIORAL,
                TherapeuticApproach.ACCEPTANCE_COMMITMENT,
            ],
            difficulty_level=DifficultyLevel.ADVANCED,
            estimated_duration=timedelta(hours=3),
            setting_description="A serene sanctuary with different zones representing various emotional states and regulation techniques",
            key_characters=[
                {
                    "name": "Dr. Chen",
                    "role": "Emotion Specialist",
                    "description": "An expert guide in emotional regulation and acceptance",
                }
            ],
            main_storylines=[
                "Understanding the function of emotions",
                "Developing distress tolerance skills",
                "Practicing radical acceptance",
            ],
            therapeutic_techniques_used=[
                "dbt_skills",
                "acceptance_strategies",
                "mindfulness_meditation",
                "values_clarification",
            ],
            recommended_therapeutic_readiness=0.7,
            content_warnings=["intense emotional content"],
            player_count=0,
            average_rating=0.0,
            completion_rate=0.0,
            therapeutic_effectiveness_score=0.0,
        )
    )

    # 5. Insight Forest (Beginner, Narrative Therapy + Solution-Focused)
    worlds.append(
        WorldDetails(
            world_id="world_insight_forest",
            name="Insight Forest",
            description="A mystical forest where you explore your personal narrative and discover new perspectives",
            long_description="Wander through an enchanted forest where each path reveals insights about your life story. Discover strengths, reframe challenges, and envision new possibilities for your journey.",
            therapeutic_themes=[
                "self_discovery",
                "narrative_exploration",
                "strength_identification",
                "future_visioning",
            ],
            therapeutic_approaches=[
                TherapeuticApproach.NARRATIVE_THERAPY,
                TherapeuticApproach.SOLUTION_FOCUSED,
            ],
            difficulty_level=DifficultyLevel.BEGINNER,
            estimated_duration=timedelta(hours=2),
            setting_description="A magical forest with glowing paths, reflective pools, and ancient trees that whisper wisdom",
            key_characters=[
                {
                    "name": "Elder Oak",
                    "role": "Wisdom Keeper",
                    "description": "An ancient tree spirit who helps you explore your story",
                }
            ],
            main_storylines=[
                "Exploring your personal narrative",
                "Identifying your strengths and resources",
                "Envisioning your preferred future",
            ],
            therapeutic_techniques_used=[
                "narrative_reframing",
                "externalization",
                "miracle_question",
                "scaling_questions",
            ],
            recommended_therapeutic_readiness=0.4,
            content_warnings=[],
            player_count=0,
            average_rating=0.0,
            completion_rate=0.0,
            therapeutic_effectiveness_score=0.0,
        )
    )

    return worlds


def main():
    """Main function to seed worlds into Neo4j."""
    logger.info("Starting world seeding process...")

    # Create repository
    try:
        repository = WorldRepository()
        logger.info("WorldRepository initialized")
    except Exception as e:
        logger.error(f"Failed to initialize WorldRepository: {e}")
        sys.exit(1)

    # Create sample worlds
    worlds = create_sample_worlds()
    logger.info(f"Created {len(worlds)} sample worlds")

    # Seed each world
    success_count = 0
    for world in worlds:
        try:
            repository.create_world(world)
            logger.info(f"✅ Seeded world: {world.name} ({world.world_id})")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to seed world {world.name}: {e}")

    # Close repository
    repository.close()

    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info("World Seeding Complete!")
    logger.info(f"Successfully seeded: {success_count}/{len(worlds)} worlds")
    logger.info(f"{'=' * 60}\n")

    if success_count < len(worlds):
        sys.exit(1)


if __name__ == "__main__":
    main()
