"""
Patient Interface API Endpoints
Provides therapeutic gaming and patient-focused functionality
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from ...components.therapeutic_systems_enhanced.adaptive_difficulty_engine import (
    AdaptiveDifficultyEngine,
)
from ...components.therapeutic_systems_enhanced.character_development_system import (
    CharacterDevelopmentSystem,
)
from ...components.therapeutic_systems_enhanced.emotional_safety_system import (
    EmotionalSafetySystem,
)
from ...components.therapeutic_systems_enhanced.therapeutic_integration_system import (
    TherapeuticIntegrationSystem,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/patient", tags=["patient"])
security = HTTPBearer()


# Pydantic models for request/response
class TherapeuticSessionCreate(BaseModel):
    patient_id: str
    therapeutic_framework: str = "Narrative"
    initial_difficulty: int = Field(default=3, ge=1, le=10)
    goals: list[str] = []


class TherapeuticSessionResponse(BaseModel):
    id: str
    patient_id: str
    start_time: datetime
    status: str
    therapeutic_framework: str
    progress_metrics: dict[str, Any]
    current_scenario: str | None = None


class ProgressUpdate(BaseModel):
    emotional_state: dict[str, float]
    engagement_level: float = Field(ge=0, le=100)
    user_choices: list[dict[str, Any]] = []
    session_duration: int  # seconds


class InterventionTrigger(BaseModel):
    intervention_type: str
    priority: str = "medium"
    context: dict[str, Any] = {}


class PatientProfile(BaseModel):
    id: str
    demographics: dict[str, Any]
    therapeutic_history: dict[str, Any]
    preferences: dict[str, Any]
    consent_status: dict[str, bool]


# Dependency injection for therapeutic systems
async def get_therapeutic_system() -> TherapeuticIntegrationSystem:
    """Get therapeutic integration system instance"""
    return TherapeuticIntegrationSystem()


async def get_safety_system() -> EmotionalSafetySystem:
    """Get emotional safety system instance"""
    return EmotionalSafetySystem()


async def get_difficulty_engine() -> AdaptiveDifficultyEngine:
    """Get adaptive difficulty engine instance"""
    return AdaptiveDifficultyEngine()


async def get_character_system() -> CharacterDevelopmentSystem:
    """Get character development system instance"""
    return CharacterDevelopmentSystem()


async def get_current_patient(token: str = Depends(security)) -> str:
    """Extract patient ID from authentication token"""
    # In production, this would validate JWT and extract patient ID
    # For now, return a mock patient ID
    return "patient_123"


# Session management endpoints
@router.post("/sessions", response_model=TherapeuticSessionResponse)
async def start_therapeutic_session(
    session_data: TherapeuticSessionCreate,
    background_tasks: BackgroundTasks,
    patient_id: str = Depends(get_current_patient),
    therapeutic_system: TherapeuticIntegrationSystem = Depends(get_therapeutic_system),
    safety_system: EmotionalSafetySystem = Depends(get_safety_system),
    difficulty_engine: AdaptiveDifficultyEngine = Depends(get_difficulty_engine),
):
    """Start a new therapeutic session"""
    try:
        session_id = str(uuid4())

        # Initialize session with therapeutic systems
        session_config = {
            "session_id": session_id,
            "patient_id": patient_id,
            "therapeutic_framework": session_data.therapeutic_framework,
            "initial_difficulty": session_data.initial_difficulty,
            "goals": session_data.goals,
        }

        # Initialize therapeutic integration
        await therapeutic_system.initialize_session(session_config)

        # Set up safety monitoring
        safety_config = {
            "patient_id": patient_id,
            "session_id": session_id,
            "monitoring_level": "standard",
            "crisis_thresholds": {
                "emotional_distress": 0.8,
                "engagement_drop": 0.3,
                "risk_indicators": ["suicidal_ideation", "self_harm"],
            },
        }
        await safety_system.initialize_monitoring(safety_config)

        # Configure adaptive difficulty
        difficulty_config = {
            "patient_id": patient_id,
            "initial_level": session_data.initial_difficulty,
            "adaptation_rate": 0.1,
            "factors": ["emotional_state", "engagement", "skill_level"],
        }
        await difficulty_engine.initialize_adaptation(difficulty_config)

        # Generate initial scenario
        initial_scenario = await therapeutic_system.generate_scenario(
            patient_id=patient_id,
            context={"session_start": True, "goals": session_data.goals},
        )

        # Schedule background monitoring
        background_tasks.add_task(
            monitor_session_safety, session_id, patient_id, safety_system
        )

        response = TherapeuticSessionResponse(
            id=session_id,
            patient_id=patient_id,
            start_time=datetime.utcnow(),
            status="active",
            therapeutic_framework=session_data.therapeutic_framework,
            progress_metrics={
                "emotional_state": {"valence": 0, "arousal": 50, "dominance": 50},
                "engagement_level": 0,
                "therapeutic_compliance": 100,
                "skill_acquisition": [],
                "risk_assessment": {"overall_risk": "low", "factors": []},
            },
            current_scenario=initial_scenario.get(
                "content", "Welcome to your therapeutic journey..."
            ),
        )

        logger.info(
            f"Started therapeutic session {session_id} for patient {patient_id}"
        )
        return response

    except Exception as e:
        logger.error(f"Failed to start therapeutic session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start session")


@router.patch("/sessions/{session_id}/progress")
async def update_session_progress(
    session_id: str,
    progress: ProgressUpdate,
    background_tasks: BackgroundTasks,
    patient_id: str = Depends(get_current_patient),
    therapeutic_system: TherapeuticIntegrationSystem = Depends(get_therapeutic_system),
    safety_system: EmotionalSafetySystem = Depends(get_safety_system),
    difficulty_engine: AdaptiveDifficultyEngine = Depends(get_difficulty_engine),
):
    """Update session progress and metrics"""
    try:
        # Update therapeutic system with progress
        await therapeutic_system.update_progress(
            session_id=session_id,
            patient_id=patient_id,
            progress_data={
                "emotional_state": progress.emotional_state,
                "engagement_level": progress.engagement_level,
                "user_choices": progress.user_choices,
                "session_duration": progress.session_duration,
            },
        )

        # Safety assessment
        safety_assessment = await safety_system.assess_emotional_state(
            patient_id=patient_id,
            emotional_state=progress.emotional_state,
            engagement_level=progress.engagement_level,
        )

        # Adaptive difficulty adjustment
        difficulty_adjustment = await difficulty_engine.adjust_difficulty(
            patient_id=patient_id,
            performance_metrics={
                "engagement": progress.engagement_level,
                "emotional_stability": progress.emotional_state.get("valence", 0),
                "choice_quality": len(progress.user_choices),
            },
        )

        # Trigger interventions if needed
        if safety_assessment.get("risk_level", "low") in ["high", "crisis"]:
            background_tasks.add_task(
                trigger_safety_intervention,
                session_id,
                patient_id,
                safety_assessment,
                therapeutic_system,
            )

        response_data = {
            "session_id": session_id,
            "updated_at": datetime.utcnow(),
            "safety_assessment": safety_assessment,
            "difficulty_level": difficulty_adjustment.get("new_level", 3),
            "interventions_triggered": safety_assessment.get("interventions", []),
        }

        logger.info(f"Updated progress for session {session_id}")
        return response_data

    except Exception as e:
        logger.error(f"Failed to update session progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update progress")


@router.post("/interventions")
async def trigger_intervention(
    intervention: InterventionTrigger,
    patient_id: str = Depends(get_current_patient),
    therapeutic_system: TherapeuticIntegrationSystem = Depends(get_therapeutic_system),
):
    """Manually trigger a therapeutic intervention"""
    try:
        intervention_response = await therapeutic_system.trigger_intervention(
            patient_id=patient_id,
            intervention_type=intervention.intervention_type,
            priority=intervention.priority,
            context=intervention.context,
        )

        logger.info(
            f"Triggered {intervention.intervention_type} intervention for patient {patient_id}"
        )
        return {
            "intervention_id": str(uuid4()),
            "type": intervention.intervention_type,
            "triggered_at": datetime.utcnow(),
            "content": intervention_response,
            "estimated_duration": intervention_response.get("duration", 5),
        }

    except Exception as e:
        logger.error(f"Failed to trigger intervention: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger intervention")


@router.get("/profile", response_model=PatientProfile)
async def get_patient_profile(patient_id: str = Depends(get_current_patient)):
    """Get patient profile and preferences"""
    try:
        # In production, this would fetch from database
        profile = PatientProfile(
            id=patient_id,
            demographics={
                "age": 28,
                "timezone": "UTC",
                "language": "en",
                "accessibility_needs": {
                    "screen_reader": False,
                    "high_contrast": False,
                    "large_text": False,
                },
            },
            therapeutic_history={
                "previous_sessions": 15,
                "total_engagement_time": 450,  # minutes
                "completed_programs": ["anxiety_management", "mindfulness_basics"],
                "current_programs": ["narrative_therapy"],
            },
            preferences={
                "therapeutic_frameworks": ["CBT", "Narrative"],
                "communication_style": "supportive",
                "session_length": 30,
                "reminder_frequency": "weekly",
            },
            consent_status={
                "data_collection": True,
                "therapeutic_interventions": True,
                "emergency_contact": True,
                "research_participation": False,
            },
        )

        return profile

    except Exception as e:
        logger.error(f"Failed to get patient profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get profile")


# Background tasks
async def monitor_session_safety(
    session_id: str, patient_id: str, safety_system: EmotionalSafetySystem
):
    """Background task to monitor session safety"""
    try:
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds

            # Perform safety check
            safety_status = await safety_system.check_session_safety(
                session_id=session_id, patient_id=patient_id
            )

            if safety_status.get("requires_intervention", False):
                logger.warning(f"Safety intervention required for session {session_id}")
                # Trigger appropriate intervention
                break

    except Exception as e:
        logger.error(f"Error in safety monitoring: {str(e)}")


async def trigger_safety_intervention(
    session_id: str,
    patient_id: str,
    safety_assessment: dict[str, Any],
    therapeutic_system: TherapeuticIntegrationSystem,
):
    """Background task to trigger safety interventions"""
    try:
        intervention_type = (
            "crisis_support"
            if safety_assessment.get("risk_level") == "crisis"
            else "emotional_support"
        )

        await therapeutic_system.trigger_intervention(
            patient_id=patient_id,
            intervention_type=intervention_type,
            priority="high",
            context={
                "session_id": session_id,
                "safety_assessment": safety_assessment,
                "automated": True,
            },
        )

        logger.info(f"Triggered safety intervention for patient {patient_id}")

    except Exception as e:
        logger.error(f"Failed to trigger safety intervention: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for patient interface API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "patient-interface-api",
    }
