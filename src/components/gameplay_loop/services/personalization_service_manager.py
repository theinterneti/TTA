"""
Personalization Service Manager

This module provides personalization services for the therapeutic gameplay loop,
including user preference management, adaptive content delivery, and personalized
therapeutic interventions.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PersonalizationProfile:
    """User personalization profile."""
    
    user_id: str
    preferences: dict[str, Any] = field(default_factory=dict)
    therapeutic_goals: list[str] = field(default_factory=list)
    learning_style: str = "balanced"
    difficulty_preference: str = "adaptive"
    session_length_preference: int = 30  # minutes
    break_frequency_preference: int = 15  # minutes
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class PersonalizationServiceManager:
    """Manages personalization services for therapeutic sessions."""
    
    def __init__(self):
        self.profiles: dict[str, PersonalizationProfile] = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_profile(self, user_id: str) -> PersonalizationProfile:
        """Get or create personalization profile for user."""
        if user_id not in self.profiles:
            self.profiles[user_id] = PersonalizationProfile(user_id=user_id)
        return self.profiles[user_id]
    
    async def update_profile(self, user_id: str, updates: dict[str, Any]) -> PersonalizationProfile:
        """Update user personalization profile."""
        profile = await self.get_profile(user_id)
        
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
            else:
                profile.preferences[key] = value
        
        profile.updated_at = datetime.utcnow()
        return profile
    
    async def get_personalized_content(self, user_id: str, content_type: str) -> dict[str, Any]:
        """Get personalized content based on user profile."""
        profile = await self.get_profile(user_id)
        
        # Placeholder implementation - would contain actual personalization logic
        return {
            "content_type": content_type,
            "user_id": user_id,
            "personalization_applied": True,
            "difficulty_level": profile.difficulty_preference,
            "learning_style": profile.learning_style,
            "therapeutic_goals": profile.therapeutic_goals,
        }
    
    async def record_interaction(self, user_id: str, interaction_data: dict[str, Any]) -> None:
        """Record user interaction for personalization learning."""
        profile = await self.get_profile(user_id)
        
        # Update preferences based on interaction
        if "preferred_difficulty" in interaction_data:
            profile.difficulty_preference = interaction_data["preferred_difficulty"]
        
        if "session_rating" in interaction_data:
            # Adjust preferences based on session feedback
            rating = interaction_data["session_rating"]
            if rating >= 4:  # Good session
                # Reinforce current settings
                pass
            elif rating <= 2:  # Poor session
                # Adjust settings
                if profile.difficulty_preference == "hard":
                    profile.difficulty_preference = "medium"
                elif profile.difficulty_preference == "easy":
                    profile.difficulty_preference = "medium"
        
        profile.updated_at = datetime.utcnow()
    
    async def get_adaptive_recommendations(self, user_id: str) -> dict[str, Any]:
        """Get adaptive recommendations for user."""
        profile = await self.get_profile(user_id)
        
        return {
            "recommended_session_length": profile.session_length_preference,
            "recommended_break_frequency": profile.break_frequency_preference,
            "recommended_difficulty": profile.difficulty_preference,
            "recommended_therapeutic_focus": profile.therapeutic_goals[:3] if profile.therapeutic_goals else ["general_wellbeing"],
            "learning_style_adaptations": {
                "visual": profile.learning_style in ["visual", "balanced"],
                "auditory": profile.learning_style in ["auditory", "balanced"],
                "kinesthetic": profile.learning_style in ["kinesthetic", "balanced"],
            }
        }
    
    async def health_check(self) -> dict[str, Any]:
        """Health check for personalization service."""
        return {
            "status": "healthy",
            "active_profiles": len(self.profiles),
            "service": "PersonalizationServiceManager"
        }
