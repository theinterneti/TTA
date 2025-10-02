"""
AI-powered therapeutic world content generator.

Uses OpenRouter AI integration to generate rich, therapeutic world content
for the TTA system. Creates comprehensive world descriptions, storylines,
characters, and therapeutic elements.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

import httpx

from ..models.enums import DifficultyLevel, TherapeuticApproach
from ..models.world import WorldDetails, WorldParameters

logger = logging.getLogger(__name__)


class AIWorldGenerator:
    """AI-powered generator for therapeutic world content."""

    def __init__(self):
        # OpenRouter configuration
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.has_openrouter = bool(self.openrouter_api_key)

        # Preferred models for content generation
        self.preferred_models = [
            "meta-llama/llama-3.2-3b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            "qwen/qwen-2-7b-instruct:free",
            "meta-llama/llama-3.1-8b-instruct:free",
        ]

        logger.info(
            f"🌍 AI World Generator initialized - OpenRouter: {'✅ Available' if self.has_openrouter else '❌ Not available'}"
        )

    async def _generate_with_openrouter(
        self, prompt: str, max_tokens: int = 1000
    ) -> str | None:
        """Generate content using OpenRouter API."""
        if not self.has_openrouter:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/theinterneti/TTA",
                "X-Title": "Therapeutic Text Adventure - World Generator",
            }

            # Try each preferred model
            for model in self.preferred_models:
                try:
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert therapeutic content creator specializing in mental health environments and narrative therapy. Create rich, immersive, and therapeutically sound content.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.8,
                        "top_p": 0.9,
                    }

                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            f"{self.openrouter_base_url}/chat/completions",
                            json=payload,
                            headers=headers,
                        )

                        if response.status_code == 200:
                            data = response.json()
                            if "choices" in data and data["choices"]:
                                content = data["choices"][0]["message"][
                                    "content"
                                ].strip()
                                logger.info(
                                    f"Generated content using {model} ({len(content)} chars)"
                                )
                                return content
                        else:
                            logger.warning(
                                f"OpenRouter API error with {model}: {response.status_code}"
                            )
                            continue

                except Exception as e:
                    logger.warning(f"Error with model {model}: {e}")
                    continue

            logger.warning("All OpenRouter models failed")
            return None

        except Exception as e:
            logger.error(f"OpenRouter integration error: {e}")
            return None

    def _create_fallback_content(self, world_type: str) -> dict[str, Any]:
        """Create fallback content when AI generation fails."""
        fallback_content = {
            "depression_recovery": {
                "name": "Depression Recovery Haven",
                "description": "A supportive environment focused on depression recovery and mood improvement",
                "long_description": "A warm, welcoming space designed to help individuals work through depression with evidence-based therapeutic approaches and peer support.",
                "setting_description": "A cozy retreat center with comfortable spaces, natural lighting, and calming environments",
                "key_characters": [
                    {
                        "name": "Dr. Hope",
                        "role": "Depression Specialist",
                        "description": "A compassionate therapist specializing in depression treatment",
                    }
                ],
                "main_storylines": [
                    "Understanding depression and its impact",
                    "Building healthy coping strategies",
                    "Reconnecting with joy and purpose",
                ],
                "therapeutic_techniques": [
                    "cognitive_restructuring",
                    "behavioral_activation",
                    "mindfulness",
                    "interpersonal_therapy",
                ],
            },
            "social_confidence": {
                "name": "Social Confidence Campus",
                "description": "A supportive environment for building social skills and confidence",
                "long_description": "An interactive campus setting where individuals can practice social interactions and build confidence in a safe, supportive environment.",
                "setting_description": "A friendly campus with various social spaces, practice areas, and supportive community environments",
                "key_characters": [
                    {
                        "name": "Coach Sam",
                        "role": "Social Skills Coach",
                        "description": "An encouraging coach who helps build social confidence",
                    }
                ],
                "main_storylines": [
                    "Overcoming social anxiety",
                    "Building communication skills",
                    "Developing authentic relationships",
                ],
                "therapeutic_techniques": [
                    "exposure_therapy",
                    "social_skills_training",
                    "cognitive_restructuring",
                    "role_playing",
                ],
            },
            "trauma_healing": {
                "name": "Trauma Healing Sanctuary",
                "description": "A safe, specialized environment for trauma recovery and healing",
                "long_description": "A carefully designed sanctuary that provides safety, support, and evidence-based trauma treatment in a controlled, therapeutic environment.",
                "setting_description": "A secure, peaceful sanctuary with private spaces, safety features, and healing-focused environments",
                "key_characters": [
                    {
                        "name": "Dr. Sage",
                        "role": "Trauma Specialist",
                        "description": "A skilled trauma therapist with expertise in PTSD and complex trauma",
                    }
                ],
                "main_storylines": [
                    "Processing traumatic experiences safely",
                    "Building resilience and coping skills",
                    "Reclaiming personal power and healing",
                ],
                "therapeutic_techniques": [
                    "EMDR",
                    "trauma_focused_CBT",
                    "somatic_therapy",
                    "grounding_techniques",
                ],
            },
        }

        return fallback_content.get(world_type, fallback_content["depression_recovery"])

    async def generate_world_content(
        self, world_type: str, therapeutic_themes: list[str]
    ) -> dict[str, Any]:
        """Generate comprehensive world content using AI."""

        # Create detailed prompt for AI generation
        prompt = f"""Create a detailed therapeutic world for a mental health text adventure game.

World Type: {world_type}
Therapeutic Themes: {', '.join(therapeutic_themes)}

Please generate a JSON response with the following structure:
{{
    "name": "World Name",
    "description": "Brief description (1-2 sentences)",
    "long_description": "Detailed description (3-4 sentences)",
    "setting_description": "Physical environment description",
    "key_characters": [
        {{"name": "Character Name", "role": "Their Role", "description": "Character description"}}
    ],
    "main_storylines": [
        "Storyline 1",
        "Storyline 2", 
        "Storyline 3"
    ],
    "therapeutic_techniques": [
        "technique1",
        "technique2",
        "technique3"
    ],
    "therapeutic_goals": [
        "goal1",
        "goal2",
        "goal3"
    ],
    "content_warnings": [
        "warning1 (if any)"
    ]
}}

Requirements:
- Therapeutically sound and evidence-based
- Safe and supportive environment
- Engaging and immersive
- Appropriate for the therapeutic themes
- Professional mental health approach
- Include diverse, inclusive characters
- Focus on healing and growth

Generate rich, detailed content that would be suitable for a professional therapeutic setting."""

        # Try AI generation first
        if self.has_openrouter:
            ai_content = await self._generate_with_openrouter(prompt, max_tokens=1500)
            if ai_content:
                try:
                    # Try to parse JSON response
                    if ai_content.startswith("```json"):
                        ai_content = (
                            ai_content.split("```json")[1].split("```")[0].strip()
                        )
                    elif ai_content.startswith("```"):
                        ai_content = ai_content.split("```")[1].split("```")[0].strip()

                    parsed_content = json.loads(ai_content)
                    logger.info(f"Successfully generated AI content for {world_type}")
                    return parsed_content
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse AI JSON response: {e}")
                    # Fall through to fallback

        # Use fallback content
        logger.info(f"Using fallback content for {world_type}")
        return self._create_fallback_content(world_type)

    async def create_therapeutic_world(
        self,
        world_type: str,
        therapeutic_themes: list[str],
        therapeutic_approaches: list[TherapeuticApproach],
        difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
    ) -> WorldDetails:
        """Create a complete therapeutic world with AI-generated content."""

        logger.info(f"Creating therapeutic world: {world_type}")

        # Generate content using AI
        content = await self.generate_world_content(world_type, therapeutic_themes)

        # Create world ID
        world_id = f"world_{world_type.lower().replace(' ', '_')}"

        # Create WorldDetails object
        world = WorldDetails(
            world_id=world_id,
            name=content.get("name", f"{world_type.title()} World"),
            description=content.get("description", "A therapeutic environment"),
            long_description=content.get(
                "long_description", "A detailed therapeutic environment"
            ),
            therapeutic_themes=therapeutic_themes,
            therapeutic_approaches=therapeutic_approaches,
            difficulty_level=difficulty_level,
            estimated_duration=timedelta(hours=2),
            # World content
            setting_description=content.get(
                "setting_description", "A therapeutic environment"
            ),
            key_characters=content.get("key_characters", []),
            main_storylines=content.get("main_storylines", []),
            therapeutic_techniques_used=content.get("therapeutic_techniques", []),
            # Prerequisites and safety
            prerequisites=[],
            recommended_therapeutic_readiness=0.5,
            content_warnings=content.get("content_warnings", []),
            # Customization
            available_parameters=[
                "therapeutic_intensity",
                "session_length_preference",
                "focus_areas",
            ],
            default_parameters=WorldParameters(),
            # Metadata
            tags=[world_type.lower(), "ai_generated", "therapeutic"],
            preview_images=[],
            creator_notes=f"AI-generated therapeutic world for {world_type}",
            therapeutic_goals_addressed=content.get("therapeutic_goals", []),
            success_metrics=[
                "therapeutic_progress",
                "engagement_level",
                "session_completion",
            ],
            # Stats (placeholder values for new worlds)
            player_count=0,
            completion_rate=0.0,
            average_rating=0.0,
            average_session_count=0,
            therapeutic_effectiveness_score=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        logger.info(f"Created world: {world.name} ({world.world_id})")
        return world
