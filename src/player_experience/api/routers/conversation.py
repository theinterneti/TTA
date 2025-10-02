"""
Conversation router: HTTP-based therapeutic conversation endpoints.

Provides simple REST API for therapeutic conversations with OpenRouter AI integration.
Complements the existing WebSocket chat system with a simpler HTTP interface.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...services.enhanced_session_persistence import EnhancedSessionPersistence
from ..auth import TokenData, get_current_active_player

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory conversation store for basic session engine (fallback)
_CONVERSATIONS: dict[str, dict[str, Any]] = {}

# Session state tracking (fallback)
_SESSION_STATES: dict[str, dict[str, Any]] = {}

# Enhanced session persistence service (initialized later with Redis client)
_SESSION_PERSISTENCE: EnhancedSessionPersistence | None = None

# Redis key prefixes for conversation storage
CONVERSATION_KEY_PREFIX = "tta:conversation:"
CONVERSATION_MESSAGES_KEY_PREFIX = "tta:conversation:messages:"
CONVERSATION_INDEX_KEY_PREFIX = "tta:player:conversations:"


class ConversationMessage(BaseModel):
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for the conversation")
    message: str = Field(..., description="User message content")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )


class ConversationResponse(BaseModel):
    message_id: str
    session_id: str
    response: str
    timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationHistory(BaseModel):
    session_id: str
    messages: list[ConversationMessage]
    total_messages: int
    created_at: str
    last_activity: str


async def _persist_conversation_to_redis(
    session_id: str,
    player_id: str,
    messages: list[dict[str, Any]],
    created_at: str,
    last_activity: str,
) -> bool:
    """Persist conversation to Redis for durability."""
    if not _SESSION_PERSISTENCE or not _SESSION_PERSISTENCE.redis_client:
        return False

    try:
        redis_client = _SESSION_PERSISTENCE.redis_client

        # Store conversation metadata
        conversation_key = f"{CONVERSATION_KEY_PREFIX}{session_id}"
        conversation_data = {
            "session_id": session_id,
            "player_id": player_id,
            "created_at": created_at,
            "last_activity": last_activity,
            "message_count": len(messages),
        }
        await redis_client.setex(
            conversation_key, 86400 * 30, json.dumps(conversation_data)  # 30 days TTL
        )

        # Store messages as a list
        messages_key = f"{CONVERSATION_MESSAGES_KEY_PREFIX}{session_id}"
        await redis_client.delete(messages_key)  # Clear existing
        if messages:
            await redis_client.rpush(
                messages_key, *[json.dumps(msg) for msg in messages]
            )
            await redis_client.expire(messages_key, 86400 * 30)  # 30 days TTL

        # Add to player's conversation index
        player_index_key = f"{CONVERSATION_INDEX_KEY_PREFIX}{player_id}"
        await redis_client.sadd(player_index_key, session_id)
        await redis_client.expire(player_index_key, 86400 * 90)  # 90 days TTL

        logger.info(
            f"Persisted conversation {session_id} to Redis with {len(messages)} messages"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to persist conversation {session_id} to Redis: {e}")
        return False


async def _load_conversation_from_redis(
    session_id: str, player_id: str
) -> dict[str, Any] | None:
    """Load conversation from Redis."""
    if not _SESSION_PERSISTENCE or not _SESSION_PERSISTENCE.redis_client:
        return None

    try:
        redis_client = _SESSION_PERSISTENCE.redis_client

        # Load conversation metadata
        conversation_key = f"{CONVERSATION_KEY_PREFIX}{session_id}"
        conversation_data_str = await redis_client.get(conversation_key)

        if not conversation_data_str:
            return None

        conversation_data = json.loads(conversation_data_str)

        # Verify ownership
        if conversation_data.get("player_id") != player_id:
            logger.warning(
                f"Player {player_id} attempted to access conversation {session_id} owned by {conversation_data.get('player_id')}"
            )
            return None

        # Load messages
        messages_key = f"{CONVERSATION_MESSAGES_KEY_PREFIX}{session_id}"
        messages_data = await redis_client.lrange(messages_key, 0, -1)
        messages = [json.loads(msg) for msg in messages_data] if messages_data else []

        logger.info(
            f"Loaded conversation {session_id} from Redis with {len(messages)} messages"
        )

        return {
            "session_id": session_id,
            "player_id": player_id,
            "messages": messages,
            "created_at": conversation_data.get("created_at"),
            "last_activity": conversation_data.get("last_activity"),
        }

    except Exception as e:
        logger.error(f"Failed to load conversation {session_id} from Redis: {e}")
        return None


class TherapeuticMetrics(BaseModel):
    """Enhanced therapeutic session metrics."""

    session_quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    emotional_progress_score: float = Field(default=0.0, ge=0.0, le=1.0)
    engagement_level: float = Field(default=0.0, ge=0.0, le=1.0)
    therapeutic_alliance_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    coping_skills_demonstrated: list[str] = Field(default_factory=list)
    breakthrough_moments: int = Field(default=0)
    resistance_indicators: list[str] = Field(default_factory=list)
    safety_concerns: list[str] = Field(default_factory=list)


class SessionAnalytics(BaseModel):
    """Comprehensive session analytics and insights."""

    session_id: str
    therapeutic_metrics: TherapeuticMetrics = Field(default_factory=TherapeuticMetrics)
    progress_indicators: dict[str, float] = Field(default_factory=dict)
    ai_insights: list[str] = Field(default_factory=list)
    recommended_interventions: list[str] = Field(default_factory=list)
    session_effectiveness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    next_session_recommendations: list[str] = Field(default_factory=list)
    therapeutic_goals_progress: dict[str, float] = Field(default_factory=dict)


class EnhancedSessionState(BaseModel):
    """Enhanced session state with comprehensive tracking."""

    session_id: str
    player_id: str
    emotional_themes: list[str] = Field(default_factory=list)
    coping_strategies_discussed: list[str] = Field(default_factory=list)
    progress_markers: list[str] = Field(default_factory=list)
    session_goals: list[str] = Field(default_factory=list)
    therapeutic_focus: str = Field(default="general_support")
    interaction_count: int = Field(default=0)
    created_at: str
    last_updated: str

    # Enhanced tracking
    session_analytics: SessionAnalytics = Field(default_factory=SessionAnalytics)
    therapeutic_interventions_used: list[str] = Field(default_factory=list)
    emotional_state_history: list[dict[str, Any]] = Field(default_factory=list)
    milestone_achievements: list[dict[str, Any]] = Field(default_factory=list)
    session_recovery_data: dict[str, Any] = Field(default_factory=dict)


class EnhancedTherapeuticAI:
    """Enhanced therapeutic AI response generator with OpenRouter integration and fallback responses."""

    def __init__(self):
        # OpenRouter configuration
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.has_openrouter = bool(self.openrouter_api_key)

        # Preferred models (free models first)
        self.preferred_models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            "qwen/qwen-2-7b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
        ]

        logger.info(
            f"🤖 Enhanced AI initialized - OpenRouter: {'✅ Available' if self.has_openrouter else '❌ Not available'}"
        )

        self.therapeutic_responses = {
            "greeting": [
                "Hello! I'm here to support you on your therapeutic journey. How are you feeling today?",
                "Welcome to our safe space. What would you like to explore or discuss today?",
                "Hi there! I'm glad you're here. What's on your mind right now?",
            ],
            "anxiety": [
                "I hear that you're feeling anxious. That's completely understandable. Can you tell me more about what's contributing to these feelings?",
                "Anxiety can feel overwhelming, but you're taking a positive step by talking about it. What helps you feel more grounded?",
                "Thank you for sharing about your anxiety. Let's explore some coping strategies that might help you feel more centered.",
            ],
            "stress": [
                "Stress is a natural response, and it sounds like you're dealing with quite a bit right now. What aspects feel most challenging?",
                "I can sense the stress you're experiencing. Sometimes it helps to break things down into smaller, manageable pieces.",
                "Stress can be exhausting. What are some ways you've found helpful for managing stress in the past?",
            ],
            "sadness": [
                "I'm sorry you're feeling sad. Your feelings are valid, and it's okay to sit with them. Would you like to talk about what's contributing to this sadness?",
                "Sadness is a natural part of the human experience. Thank you for trusting me with these feelings. How can I best support you right now?",
                "It takes courage to acknowledge and share feelings of sadness. What would feel most helpful for you in this moment?",
            ],
            "default": [
                "I'm here to listen and support you. Can you tell me more about what you're experiencing?",
                "Thank you for sharing that with me. How are you feeling about this situation?",
                "I appreciate you opening up. What would feel most helpful to explore right now?",
                "That sounds important to you. Can you help me understand more about your perspective?",
                "I'm listening. What aspects of this feel most significant to you?",
            ],
        }

    async def _generate_openrouter_response(
        self, user_message: str, context: dict[str, Any] = None
    ) -> tuple[str, dict[str, Any]] | None:
        """Generate response using OpenRouter API."""
        if not self.has_openrouter:
            return None

        try:
            # Build therapeutic system prompt
            system_prompt = """You are a compassionate therapeutic AI assistant. Your role is to:
1. Provide emotional support and validation
2. Use evidence-based therapeutic techniques (CBT, mindfulness, etc.)
3. Ask thoughtful questions to help users explore their feelings
4. Suggest practical coping strategies when appropriate
5. Maintain appropriate boundaries and refer to professional help when needed
6. Always prioritize user safety and well-being

Respond with empathy, warmth, and professionalism. Keep responses concise but meaningful."""

            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/theinterneti/TTA",
                "X-Title": "Therapeutic Text Adventure",
            }

            # Try each preferred model
            for model in self.preferred_models:
                try:
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }

                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            f"{self.openrouter_base_url}/chat/completions",
                            json=payload,
                            headers=headers,
                        )

                        if response.status_code == 200:
                            data = response.json()
                            if "choices" in data and data["choices"]:
                                ai_response = data["choices"][0]["message"][
                                    "content"
                                ].strip()
                                metadata = {
                                    "response_type": "ai_generated",
                                    "therapeutic_intent": "ai_therapeutic_support",
                                    "safety_level": "safe",
                                    "generated_by": "openrouter",
                                    "model_used": model,
                                    "tokens_used": data.get("usage", {}).get(
                                        "total_tokens", 0
                                    ),
                                }
                                logger.info(
                                    f"Generated OpenRouter response using {model}"
                                )
                                return ai_response, metadata
                        else:
                            logger.warning(
                                f"OpenRouter API error with {model}: {response.status_code}"
                            )
                            continue

                except Exception as e:
                    logger.warning(f"Error with model {model}: {e}")
                    continue

            logger.warning(
                "All OpenRouter models failed, falling back to basic responses"
            )
            return None

        except Exception as e:
            logger.error(f"OpenRouter integration error: {e}")
            return None

    async def _analyze_therapeutic_progress(
        self, session_id: str, user_message: str, ai_response: str
    ) -> dict[str, Any]:
        """Analyze therapeutic progress using AI-powered assessment."""
        if not self.has_openrouter:
            return {"analysis_available": False}

        session_state = _SESSION_STATES.get(session_id, {})
        interaction_count = session_state.get("interaction_count", 0)
        emotional_themes = session_state.get("emotional_themes", [])

        # Create progress analysis prompt
        analysis_prompt = f"""Analyze this therapeutic conversation exchange for progress indicators:

User Message: "{user_message}"
AI Response: "{ai_response}"

Session Context:
- Interaction Count: {interaction_count}
- Current Emotional Themes: {', '.join(emotional_themes)}

Please provide a JSON analysis with these fields:
{{
    "emotional_progress_score": 0.0-1.0,
    "engagement_level": 0.0-1.0,
    "coping_skills_demonstrated": ["skill1", "skill2"],
    "breakthrough_indicators": ["indicator1"],
    "resistance_indicators": ["indicator1"],
    "recommended_interventions": ["intervention1"],
    "session_quality_score": 0.0-1.0,
    "therapeutic_insights": ["insight1", "insight2"]
}}

Focus on evidence-based therapeutic assessment. Be objective and supportive."""

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/theinterneti/TTA",
                "X-Title": "TTA Progress Analysis",
            }

            payload = {
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a therapeutic progress analyst. Respond only with valid JSON.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                "max_tokens": 500,
                "temperature": 0.3,
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and data["choices"]:
                        analysis_text = data["choices"][0]["message"]["content"]
                        try:
                            # Extract JSON from response
                            import json
                            import re

                            json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
                            if json_match:
                                analysis_data = json.loads(json_match.group())
                                analysis_data["analysis_available"] = True
                                return analysis_data
                        except json.JSONDecodeError:
                            pass

        except Exception as e:
            logger.warning(f"Progress analysis error: {e}")

        # Fallback basic analysis
        return {
            "analysis_available": False,
            "emotional_progress_score": 0.5,
            "engagement_level": 0.7 if len(user_message) > 20 else 0.4,
            "session_quality_score": 0.6,
        }

    async def generate_response(
        self, user_message: str, context: dict[str, Any] = None
    ) -> tuple[str, dict[str, Any]]:
        """Generate a therapeutic response based on user input."""
        context = context or {}

        # Try OpenRouter first if available
        if self.has_openrouter:
            openrouter_result = await self._generate_openrouter_response(
                user_message, context
            )
            if openrouter_result:
                return openrouter_result

        # Fallback to basic responses
        user_lower = user_message.lower()

        # Simple keyword-based response selection
        if any(word in user_lower for word in ["hello", "hi", "hey", "start"]):
            response_type = "greeting"
        elif any(
            word in user_lower for word in ["anxious", "anxiety", "worried", "nervous"]
        ):
            response_type = "anxiety"
        elif any(
            word in user_lower
            for word in ["stressed", "stress", "overwhelmed", "pressure"]
        ):
            response_type = "stress"
        elif any(
            word in user_lower
            for word in ["sad", "sadness", "depressed", "down", "low"]
        ):
            response_type = "sadness"
        else:
            response_type = "default"

        # Select response
        responses = self.therapeutic_responses[response_type]
        import random

        response = random.choice(responses)

        # Generate metadata
        metadata = {
            "response_type": response_type,
            "therapeutic_intent": "emotional_support",
            "safety_level": "safe",
            "generated_by": "basic_ai_fallback",
        }

        return response, metadata


# Initialize AI generator
ai_generator = EnhancedTherapeuticAI()


@router.post("/send", response_model=ConversationResponse)
async def send_message(
    request: SendMessageRequest,
    current_player: TokenData = Depends(get_current_active_player),
) -> ConversationResponse:
    """Send a message and receive a therapeutic response."""
    try:
        player_id = current_player.player_id
        session_id = request.session_id
        user_message = request.message.strip()

        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty",
            )

        # Initialize conversation if it doesn't exist
        if session_id not in _CONVERSATIONS:
            # Try to load from Redis first
            redis_conversation = await _load_conversation_from_redis(
                session_id, player_id
            )

            if redis_conversation:
                _CONVERSATIONS[session_id] = redis_conversation
                logger.info(f"Loaded conversation {session_id} from Redis into memory")
            else:
                _CONVERSATIONS[session_id] = {
                    "session_id": session_id,
                    "player_id": player_id,
                    "messages": [],
                    "created_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat(),
                }

        # Initialize session state if it doesn't exist
        if session_id not in _SESSION_STATES:
            session_analytics = SessionAnalytics(session_id=session_id)
            _SESSION_STATES[session_id] = {
                "session_id": session_id,
                "player_id": player_id,
                "emotional_themes": [],
                "coping_strategies_discussed": [],
                "progress_markers": [],
                "session_goals": [],
                "therapeutic_focus": "general_support",
                "interaction_count": 0,
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                # Enhanced tracking
                "session_analytics": session_analytics.model_dump(),
                "therapeutic_interventions_used": [],
                "emotional_state_history": [],
                "milestone_achievements": [],
                "session_recovery_data": {},
            }

        conversation = _CONVERSATIONS[session_id]
        session_state = _SESSION_STATES[session_id]

        # Verify ownership
        if conversation["player_id"] != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        # Update session state with user input analysis
        session_state["interaction_count"] += 1
        session_state["last_updated"] = datetime.utcnow().isoformat()

        # Analyze emotional themes
        user_lower = user_message.lower()
        if any(
            word in user_lower for word in ["anxious", "anxiety", "worried", "nervous"]
        ):
            if "anxiety" not in session_state["emotional_themes"]:
                session_state["emotional_themes"].append("anxiety")
        if any(
            word in user_lower
            for word in ["stressed", "stress", "overwhelmed", "pressure"]
        ):
            if "stress" not in session_state["emotional_themes"]:
                session_state["emotional_themes"].append("stress")
        if any(
            word in user_lower
            for word in ["sad", "sadness", "depressed", "down", "low"]
        ):
            if "depression" not in session_state["emotional_themes"]:
                session_state["emotional_themes"].append("depression")

        # Add user message
        user_msg = ConversationMessage(
            role="user", content=user_message, metadata={"context": request.context}
        )
        conversation["messages"].append(user_msg.model_dump())

        # Generate AI response with session context
        enhanced_context = {
            **request.context,
            "session_id": session_id,
            "player_id": player_id,
            "session_state": session_state,
        }
        ai_response, ai_metadata = await ai_generator.generate_response(
            user_message, enhanced_context
        )

        # Perform AI-powered progress analysis
        progress_analysis = await ai_generator._analyze_therapeutic_progress(
            session_id, user_message, ai_response
        )

        # Update session analytics with progress analysis
        if progress_analysis.get("analysis_available", False):
            session_analytics = session_state["session_analytics"]
            therapeutic_metrics = session_analytics["therapeutic_metrics"]

            # Update therapeutic metrics
            therapeutic_metrics["emotional_progress_score"] = progress_analysis.get(
                "emotional_progress_score", 0.5
            )
            therapeutic_metrics["engagement_level"] = progress_analysis.get(
                "engagement_level", 0.5
            )
            therapeutic_metrics["session_quality_score"] = progress_analysis.get(
                "session_quality_score", 0.5
            )

            # Update coping skills and interventions
            new_skills = progress_analysis.get("coping_skills_demonstrated", [])
            for skill in new_skills:
                if skill not in therapeutic_metrics["coping_skills_demonstrated"]:
                    therapeutic_metrics["coping_skills_demonstrated"].append(skill)

            # Update session analytics
            session_analytics["ai_insights"] = progress_analysis.get(
                "therapeutic_insights", []
            )
            session_analytics["recommended_interventions"] = progress_analysis.get(
                "recommended_interventions", []
            )

            # Record breakthrough moments
            breakthrough_indicators = progress_analysis.get(
                "breakthrough_indicators", []
            )
            if breakthrough_indicators:
                therapeutic_metrics["breakthrough_moments"] += len(
                    breakthrough_indicators
                )
                milestone_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "breakthrough",
                    "indicators": breakthrough_indicators,
                    "interaction_count": session_state["interaction_count"],
                }
                session_state["milestone_achievements"].append(milestone_data)

            # Update resistance indicators
            resistance_indicators = progress_analysis.get("resistance_indicators", [])
            therapeutic_metrics["resistance_indicators"] = resistance_indicators

            # Update session state
            session_state["session_analytics"] = session_analytics

        # Record emotional state history
        emotional_state_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "interaction_count": session_state["interaction_count"],
            "emotional_themes": session_state["emotional_themes"].copy(),
            "engagement_level": progress_analysis.get("engagement_level", 0.5),
            "user_message_length": len(user_message),
            "ai_response_length": len(ai_response),
        }
        session_state["emotional_state_history"].append(emotional_state_entry)

        # Keep only last 20 emotional state entries to manage memory
        if len(session_state["emotional_state_history"]) > 20:
            session_state["emotional_state_history"] = session_state[
                "emotional_state_history"
            ][-20:]

        # Persist enhanced session state to Redis
        if _SESSION_PERSISTENCE:
            await _SESSION_PERSISTENCE.save_session_state(session_id, session_state)

        # Add AI response
        message_id = str(uuid.uuid4())
        ai_msg = ConversationMessage(
            role="assistant",
            content=ai_response,
            metadata={**ai_metadata, "progress_analysis": progress_analysis},
        )
        conversation["messages"].append(ai_msg.model_dump())
        conversation["last_activity"] = datetime.utcnow().isoformat()

        # Persist conversation history to Redis
        await _persist_conversation_to_redis(
            session_id=session_id,
            player_id=player_id,
            messages=conversation["messages"],
            created_at=conversation["created_at"],
            last_activity=conversation["last_activity"],
        )

        logger.info(
            f"Generated conversation response for session {session_id} with progress analysis"
        )

        return ConversationResponse(
            message_id=message_id,
            session_id=session_id,
            response=ai_response,
            timestamp=ai_msg.timestamp,
            metadata={**ai_metadata, "progress_analysis": progress_analysis},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        ) from e


@router.get("/{session_id}/history", response_model=ConversationHistory)
async def get_conversation_history(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),
    limit: int = 50,
) -> ConversationHistory:
    """Get conversation history for a session."""
    try:
        player_id = current_player.player_id
        conversation = None

        # Try to load from Redis first
        conversation = await _load_conversation_from_redis(session_id, player_id)

        # Fall back to in-memory if not in Redis
        if not conversation and session_id in _CONVERSATIONS:
            conversation = _CONVERSATIONS[session_id]

            # Verify ownership
            if conversation["player_id"] != player_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this conversation",
                )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Get recent messages
        messages = (
            conversation["messages"][-limit:] if limit > 0 else conversation["messages"]
        )

        return ConversationHistory(
            session_id=session_id,
            messages=[ConversationMessage(**msg) for msg in messages],
            total_messages=len(conversation["messages"]),
            created_at=conversation["created_at"],
            last_activity=conversation["last_activity"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_conversation_history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history",
        ) from e


@router.delete("/{session_id}")
async def clear_conversation(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),
) -> dict[str, str]:
    """Clear conversation history for a session."""
    try:
        player_id = current_player.player_id

        if session_id not in _CONVERSATIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        conversation = _CONVERSATIONS[session_id]

        # Verify ownership
        if conversation["player_id"] != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        # Store session recovery data before clearing
        if session_id in _SESSION_STATES:
            session_state = _SESSION_STATES[session_id]
            recovery_data = {
                "session_id": session_id,
                "player_id": player_id,
                "cleared_at": datetime.utcnow().isoformat(),
                "final_analytics": session_state.get("session_analytics", {}),
                "total_interactions": session_state.get("interaction_count", 0),
                "emotional_themes": session_state.get("emotional_themes", []),
                "milestone_count": len(session_state.get("milestone_achievements", [])),
                "session_duration_minutes": session_state.get(
                    "computed_analytics", {}
                ).get("session_duration_minutes", 0),
            }
            session_state["session_recovery_data"] = recovery_data

            # Persist recovery data to Redis
            if _SESSION_PERSISTENCE:
                await _SESSION_PERSISTENCE.save_session_recovery_data(
                    session_id, recovery_data
                )

        # Clear the conversation and session state
        del _CONVERSATIONS[session_id]
        if session_id in _SESSION_STATES:
            del _SESSION_STATES[session_id]

        logger.info(
            f"Cleared conversation and session state {session_id} for player {player_id}"
        )

        return {"message": "Conversation and session state cleared successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in clear_conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear conversation",
        ) from e


@router.get("/{session_id}/state")
async def get_session_state(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),
) -> dict[str, Any]:
    """Get therapeutic session state and progress."""
    try:
        player_id = current_player.player_id

        if session_id not in _SESSION_STATES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session state not found"
            )

        session_state = _SESSION_STATES[session_id]

        # Verify ownership
        if session_state["player_id"] != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session state",
            )

        # Calculate additional analytics
        enhanced_state = session_state.copy()

        # Calculate session duration (approximate)
        created_at = datetime.fromisoformat(session_state["created_at"])
        last_updated = datetime.fromisoformat(session_state["last_updated"])
        session_duration_minutes = (last_updated - created_at).total_seconds() / 60

        # Calculate progress trends
        emotional_history = session_state.get("emotional_state_history", [])
        if len(emotional_history) >= 2:
            recent_engagement = sum(
                entry.get("engagement_level", 0.5) for entry in emotional_history[-3:]
            ) / min(3, len(emotional_history))
            early_engagement = sum(
                entry.get("engagement_level", 0.5) for entry in emotional_history[:3]
            ) / min(3, len(emotional_history))
            engagement_trend = recent_engagement - early_engagement
        else:
            engagement_trend = 0.0

        # Add computed analytics
        enhanced_state["computed_analytics"] = {
            "session_duration_minutes": round(session_duration_minutes, 2),
            "engagement_trend": round(engagement_trend, 3),
            "total_emotional_themes": len(session_state.get("emotional_themes", [])),
            "total_coping_strategies": len(
                session_state.get("coping_strategies_discussed", [])
            ),
            "total_milestones": len(session_state.get("milestone_achievements", [])),
            "emotional_state_entries": len(emotional_history),
            "average_engagement": (
                round(
                    sum(
                        entry.get("engagement_level", 0.5)
                        for entry in emotional_history
                    )
                    / max(1, len(emotional_history)),
                    3,
                )
                if emotional_history
                else 0.5
            ),
        }

        return enhanced_state

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_session_state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session state",
        ) from e


@router.get("/{session_id}/analytics", response_model=SessionAnalytics)
async def get_session_analytics(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),
) -> SessionAnalytics:
    """Get detailed session analytics and therapeutic insights."""
    try:
        player_id = current_player.player_id

        if session_id not in _SESSION_STATES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session state not found"
            )

        session_state = _SESSION_STATES[session_id]

        # Verify ownership
        if session_state["player_id"] != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session analytics",
            )

        # Extract session analytics
        analytics_data = session_state.get("session_analytics", {})

        # Create SessionAnalytics response
        return SessionAnalytics(**analytics_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_session_analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session analytics",
        ) from e


@router.post("/{session_id}/goals")
async def set_session_goals(
    session_id: str,
    goals: list[str],
    current_player: TokenData = Depends(get_current_active_player),
) -> dict[str, Any]:
    """Set therapeutic goals for a session."""
    try:
        player_id = current_player.player_id

        if session_id not in _SESSION_STATES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session state not found"
            )

        session_state = _SESSION_STATES[session_id]

        # Verify ownership
        if session_state["player_id"] != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session",
            )

        # Update session goals
        session_state["session_goals"] = goals
        session_state["last_updated"] = datetime.utcnow().isoformat()

        # Initialize goal progress tracking
        session_analytics = session_state.get("session_analytics", {})
        if "therapeutic_goals_progress" not in session_analytics:
            session_analytics["therapeutic_goals_progress"] = {}

        # Set initial progress for new goals
        for goal in goals:
            if goal not in session_analytics["therapeutic_goals_progress"]:
                session_analytics["therapeutic_goals_progress"][goal] = 0.0

        session_state["session_analytics"] = session_analytics

        logger.info(f"Set {len(goals)} therapeutic goals for session {session_id}")

        return {
            "message": "Session goals updated successfully",
            "goals": goals,
            "goal_count": len(goals),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in set_session_goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set session goals",
        ) from e


@router.get("/player/analytics")
async def get_player_session_analytics(
    current_player: TokenData = Depends(get_current_active_player), limit: int = 10
) -> dict[str, Any]:
    """Get comprehensive session analytics for the current player."""
    try:
        player_id = current_player.player_id

        # Get analytics from Redis if available
        analytics_list = []
        if _SESSION_PERSISTENCE:
            analytics_list = await _SESSION_PERSISTENCE.get_player_session_analytics(
                player_id, limit
            )

        # Get current active session analytics
        active_sessions = []
        for session_id, session_state in _SESSION_STATES.items():
            if session_state.get("player_id") == player_id:
                active_sessions.append(
                    {
                        "session_id": session_id,
                        "analytics": session_state.get("session_analytics", {}),
                        "interaction_count": session_state.get("interaction_count", 0),
                        "emotional_themes": session_state.get("emotional_themes", []),
                        "is_active": True,
                    }
                )

        # Calculate aggregate statistics
        total_interactions = sum(
            session.get("interaction_count", 0)
            for session in analytics_list + active_sessions
        )

        all_emotional_themes = set()
        for session in analytics_list + active_sessions:
            all_emotional_themes.update(session.get("emotional_themes", []))

        return {
            "player_id": player_id,
            "total_sessions": len(analytics_list) + len(active_sessions),
            "active_sessions": len(active_sessions),
            "total_interactions": total_interactions,
            "unique_emotional_themes": list(all_emotional_themes),
            "recent_sessions": analytics_list[:5],  # Last 5 sessions
            "active_session_summaries": active_sessions,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in get_player_session_analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve player analytics",
        ) from e


@router.get("/statistics")
async def get_session_statistics(
    current_player: TokenData = Depends(get_current_active_player),
) -> dict[str, Any]:
    """Get overall session statistics (admin/analytics endpoint)."""
    try:
        # Get Redis statistics if available
        redis_stats = {}
        if _SESSION_PERSISTENCE:
            redis_stats = await _SESSION_PERSISTENCE.get_session_statistics()

        # Get in-memory statistics
        memory_stats = {
            "active_conversations": len(_CONVERSATIONS),
            "active_session_states": len(_SESSION_STATES),
            "total_emotional_themes": len(
                set(
                    theme
                    for session_state in _SESSION_STATES.values()
                    for theme in session_state.get("emotional_themes", [])
                )
            ),
            "total_interactions": sum(
                session_state.get("interaction_count", 0)
                for session_state in _SESSION_STATES.values()
            ),
        }

        return {
            "memory_statistics": memory_stats,
            "redis_statistics": redis_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in get_session_statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session statistics",
        ) from e


@router.get("/health", dependencies=[])
async def health_check() -> dict[str, Any]:
    """Health check endpoint for conversation service."""
    return {
        "status": "healthy",
        "service": "conversation",
        "active_conversations": len(_CONVERSATIONS),
        "active_session_states": len(_SESSION_STATES),
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "ai_progress_analysis": True,
            "session_analytics": True,
            "therapeutic_goals": True,
            "session_recovery": True,
            "emotional_tracking": True,
        },
    }
