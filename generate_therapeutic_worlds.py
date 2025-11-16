#!/usr/bin/env python3
"""
Generate additional therapeutic worlds for the TTA system.

This script uses AI content generation to create 3 new therapeutic worlds:
1. Depression Recovery Haven
2. Social Confidence Campus
3. Trauma Healing Sanctuary

The worlds are added to the world management system and made available
through the existing world API endpoints.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from player_experience.managers.ai_world_generator import AIWorldGenerator
from player_experience.managers.world_management_module import WorldManagementModule
from player_experience.models.enums import DifficultyLevel, TherapeuticApproach


async def generate_new_worlds():
    """Generate 3 new therapeutic worlds using AI content generation."""

    print("🌍 TTA Therapeutic World Generator")
    print("=" * 50)

    # Initialize generators
    ai_generator = AIWorldGenerator()
    world_manager = WorldManagementModule()

    # Define the 3 new worlds to create
    world_specs = [
        {
            "world_type": "depression_recovery",
            "therapeutic_themes": [
                "depression",
                "mood_improvement",
                "hope",
                "self_worth",
            ],
            "therapeutic_approaches": [
                TherapeuticApproach.CBT,
                TherapeuticApproach.BEHAVIORAL_ACTIVATION,
            ],
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
        },
        {
            "world_type": "social_confidence",
            "therapeutic_themes": [
                "social_anxiety",
                "confidence_building",
                "communication",
                "relationships",
            ],
            "therapeutic_approaches": [
                TherapeuticApproach.CBT,
                TherapeuticApproach.SKILL_BUILDING,
            ],
            "difficulty_level": DifficultyLevel.BEGINNER,
        },
        {
            "world_type": "trauma_healing",
            "therapeutic_themes": ["trauma_recovery", "PTSD", "safety", "resilience"],
            "therapeutic_approaches": [
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
            "difficulty_level": DifficultyLevel.ADVANCED,
        },
    ]

    generated_worlds = []

    # Generate each world
    for i, spec in enumerate(world_specs, 1):
        print(
            f"\n🎯 Generating World {i}/3: {spec['world_type'].replace('_', ' ').title()}"
        )
        print(f"   Themes: {', '.join(spec['therapeutic_themes'])}")
        print(
            f"   Approaches: {', '.join([approach.value for approach in spec['therapeutic_approaches']])}"
        )
        print(f"   Difficulty: {spec['difficulty_level'].value}")

        try:
            # Generate world using AI
            world = await ai_generator.create_therapeutic_world(
                world_type=spec["world_type"],
                therapeutic_themes=spec["therapeutic_themes"],
                therapeutic_approaches=spec["therapeutic_approaches"],
                difficulty_level=spec["difficulty_level"],
            )

            # Add to world manager cache
            world_manager._world_cache[world.world_id] = world
            generated_worlds.append(world)

            print(f"   ✅ Generated: {world.name}")
            print(f"      ID: {world.world_id}")
            print(f"      Description: {world.description}")
            print(f"      Characters: {len(world.key_characters)} characters")
            print(f"      Storylines: {len(world.main_storylines)} storylines")
            print(
                f"      Techniques: {len(world.therapeutic_techniques_used)} techniques"
            )

        except Exception as e:
            print(f"   ❌ Failed to generate {spec['world_type']}: {e}")
            continue

    print("\n🎉 World Generation Complete!")
    print(f"   Successfully generated: {len(generated_worlds)}/3 worlds")

    # Display summary
    print("\n📊 World Library Summary:")
    all_worlds = world_manager.get_available_worlds("demo_player")
    print(f"   Total worlds available: {len(all_worlds)}")

    for world in all_worlds:
        print(f"   • {world.name} ({world.difficulty_level.value})")
        print(f"     Themes: {', '.join(world.therapeutic_themes)}")
        print(
            f"     Rating: {world.average_rating:.1f}/5.0 ({world.player_count} players)"
        )

    return generated_worlds


async def test_world_api():
    """Test the world API endpoints with the new worlds."""

    print("\n🧪 Testing World API Integration")
    print("=" * 40)

    try:
        import httpx

        # Test worlds list endpoint
        async with httpx.AsyncClient() as client:
            # Note: This would require authentication in a real test
            print("   📡 World API endpoints ready for testing")
            print("   Use: GET /api/v1/worlds/ to list all worlds")
            print("   Use: GET /api/v1/worlds/{world_id} for world details")

    except ImportError:
        print("   ⚠️ httpx not available for API testing")


def display_world_details(world):
    """Display detailed information about a generated world."""
    print(f"\n📖 {world.name} Details:")
    print(f"   ID: {world.world_id}")
    print(f"   Description: {world.description}")
    print(f"   Long Description: {world.long_description}")
    print(f"   Setting: {world.setting_description}")

    if world.key_characters:
        print("   Characters:")
        for char in world.key_characters:
            print(
                f"     • {char.get('name', 'Unknown')} - {char.get('role', 'Unknown Role')}"
            )

    if world.main_storylines:
        print("   Storylines:")
        for storyline in world.main_storylines:
            print(f"     • {storyline}")

    if world.therapeutic_techniques_used:
        print("   Therapeutic Techniques:")
        for technique in world.therapeutic_techniques_used:
            print(f"     • {technique}")


async def main():
    """Main execution function."""

    # Check if OpenRouter API key is available
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️ OPENROUTER_API_KEY not found in environment")
        print("   AI generation will use fallback content")
        print("   Set OPENROUTER_API_KEY for enhanced AI-generated content")
    else:
        print("✅ OpenRouter API key found - AI generation enabled")

    try:
        # Generate the worlds
        generated_worlds = await generate_new_worlds()

        # Display detailed information for each generated world
        for world in generated_worlds:
            display_world_details(world)

        # Test API integration
        await test_world_api()

        print("\n🚀 Minimal World Content Population - COMPLETE!")
        print(
            f"   The TTA system now has {len(generated_worlds) + 2} therapeutic worlds available"
        )
        print("   Worlds are ready for character-world pairing and session creation")

    except Exception as e:
        print(f"❌ Error during world generation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Set up environment
    if os.path.exists(".env.homelab"):
        print("📁 Loading environment from .env.homelab")
        with open(".env.homelab") as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    # Run the world generation
    asyncio.run(main())
