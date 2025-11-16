#!/usr/bin/env python3
"""
Enhanced TTA API Server with Real AI Narrative Generation

This server provides:
1. Real OpenRouter API integration for therapeutic narrative generation
2. Fallback to high-quality therapeutic responses when API unavailable
3. Complete WebSocket chat functionality
4. Comprehensive logging and error handling
5. Production-ready AI narrative generation pipeline

Usage:
    # With OpenRouter API key (real AI):
    export OPENROUTER_API_KEY='your-key-here'
    python enhanced_api_server.py

    # Without API key (enhanced therapeutic responses):
    python enhanced_api_server.py
"""

import json
import logging
import os
import uuid
from datetime import datetime
from enum import Enum

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global state
sessions: dict[str, dict] = {}
chat_history: dict[str, list] = {}
player_preferences: dict[str, dict] = {}  # In-memory storage for preferences


class ChatMessage(BaseModel):
    message: str
    session_id: str | None = None
    character_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    therapeutic_notes: str
    ai_generated: bool = False


# Player Preferences Models
class IntensityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TherapeuticApproach(str, Enum):
    CBT = "cognitive_behavioral_therapy"
    MINDFULNESS = "mindfulness"
    NARRATIVE = "narrative_therapy"
    SOMATIC = "somatic_therapy"
    HUMANISTIC = "humanistic"
    PSYCHODYNAMIC = "psychodynamic"
    ACCEPTANCE_COMMITMENT = "acceptance_commitment_therapy"
    DIALECTICAL_BEHAVIOR = "dialectical_behavior_therapy"


class ConversationStyle(str, Enum):
    GENTLE = "gentle"
    DIRECT = "direct"
    EXPLORATORY = "exploratory"
    SUPPORTIVE = "supportive"


class PreferredSetting(str, Enum):
    PEACEFUL_FOREST = "peaceful_forest"
    MOUNTAIN_RETREAT = "mountain_retreat"
    OCEAN_SANCTUARY = "ocean_sanctuary"
    URBAN_GARDEN = "urban_garden"
    COZY_LIBRARY = "cozy_library"
    STARLIT_MEADOW = "starlit_meadow"
    QUIET_GARDEN = "quiet_garden"
    FOREST_CLEARING = "forest_clearing"


class PlayerPreferences(BaseModel):
    player_id: str
    intensity_level: IntensityLevel = IntensityLevel.MEDIUM
    preferred_approaches: list[TherapeuticApproach] = Field(default_factory=list)
    conversation_style: ConversationStyle = ConversationStyle.SUPPORTIVE
    therapeutic_goals: list[str] = Field(default_factory=list)
    primary_concerns: list[str] = Field(default_factory=list)
    character_name: str = "Alex"
    preferred_setting: PreferredSetting = PreferredSetting.PEACEFUL_FOREST
    comfort_topics: list[str] = Field(default_factory=list)
    trigger_topics: list[str] = Field(default_factory=list)
    avoid_topics: list[str] = Field(default_factory=list)
    session_duration_preference: int = 30
    reminder_frequency: str = "weekly"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1


class PreferenceValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PreferencePreviewRequest(BaseModel):
    preferences: PlayerPreferences
    test_message: str


class PreferencePreviewResponse(BaseModel):
    user_message: str
    preferences: PlayerPreferences
    preview_response: str
    adaptations_applied: list[str] = Field(default_factory=list)


class TherapeuticAIGenerator:
    """AI-powered therapeutic narrative generator with OpenRouter integration."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.has_api_key = bool(self.api_key)
        self.headers = (
            {
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/theinterneti/TTA",
                "X-Title": "Therapeutic Text Adventure",
            }
            if self.api_key
            else {}
        )

        # Initialize connection status
        self.api_available = False

        logger.info(
            f"🤖 AI Generator initialized - API Key: {'✅ Present' if self.has_api_key else '❌ Missing'}"
        )

    async def initialize(self):
        """Initialize and test API connection."""
        if not self.has_api_key:
            logger.info("🔄 Running in Enhanced Therapeutic Mode (no API key)")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models", headers=self.headers, timeout=10.0
                )

                if response.status_code == 200:
                    self.api_available = True
                    models = response.json()
                    logger.info(
                        f"✅ OpenRouter API connected - {len(models.get('data', []))} models available"
                    )
                else:
                    logger.warning(
                        f"⚠️ OpenRouter API connection failed: {response.status_code}"
                    )

        except Exception as e:
            logger.warning(f"⚠️ OpenRouter API connection error: {e}")

    async def generate_therapeutic_response(
        self,
        user_message: str,
        context: dict = None,
        preferences: PlayerPreferences | None = None,
    ) -> tuple[str, bool]:
        """Generate therapeutic response - AI if available, enhanced fallback otherwise."""

        if self.api_available and self.has_api_key:
            # Try AI generation first
            ai_response = await self._generate_ai_response(
                user_message, context or {}, preferences
            )
            if ai_response:
                return ai_response, True

        # Fallback to enhanced therapeutic responses
        enhanced_response = self._generate_enhanced_therapeutic_response(
            user_message, context or {}, preferences
        )
        return enhanced_response, False

    async def _generate_ai_response(
        self,
        user_message: str,
        context: dict,
        preferences: PlayerPreferences | None = None,
    ) -> str | None:
        """Generate AI response using OpenRouter API."""
        try:
            therapeutic_prompt = self._create_therapeutic_prompt(
                user_message, context, preferences
            )

            payload = {
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a compassionate therapeutic storytelling AI that helps users explore emotions through immersive, calming narratives. Create engaging therapeutic stories that help users process anxiety, build confidence, and find inner peace. Keep responses conversational and under 200 words.",
                    },
                    {"role": "user", "content": therapeutic_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 250,
                "top_p": 0.9,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    narrative = result["choices"][0]["message"]["content"].strip()
                    logger.info(
                        f"✅ AI generated therapeutic narrative ({len(narrative)} chars)"
                    )
                    return narrative
                logger.warning(f"⚠️ AI generation failed: {response.status_code}")
                return None

        except Exception as e:
            logger.warning(f"⚠️ AI generation error: {e}")
            return None

    def _create_therapeutic_prompt(
        self,
        user_message: str,
        context: dict,
        preferences: PlayerPreferences | None = None,
    ) -> str:
        """Create therapeutic prompt for AI generation with player preferences."""
        turn_count = context.get("turn_count", 1)
        character_name = context.get("character_name", "Alex")
        setting = context.get("setting", "peaceful forest")

        # Apply player preferences if available
        if preferences:
            character_name = preferences.character_name
            setting = preferences.preferred_setting.value.replace("_", " ")

            # Build preference-aware prompt
            return self._build_preference_aware_prompt(
                user_message, context, preferences
            )

        # Fallback to basic prompt

        return f"""
Create a therapeutic narrative response for: "{user_message}"

Context: Turn {turn_count}, Character: {character_name}, Setting: {setting}

Guidelines:
1. Acknowledge user's message with empathy
2. Continue immersive, calming narrative in {setting}
3. Include therapeutic elements (breathing, mindfulness, nature)
4. Ask gentle question for exploration
5. Keep warm, supportive tone
6. 2-3 sentences maximum

Response:"""

    def _build_preference_aware_prompt(
        self, user_message: str, context: dict, preferences: PlayerPreferences
    ) -> str:
        """Build a therapeutic prompt that incorporates player preferences."""
        turn_count = context.get("turn_count", 1)

        # Intensity level adaptations
        intensity_guidance = {
            IntensityLevel.LOW: "Use gentle, non-confrontational language. Focus on comfort and safety. Avoid challenging questions.",
            IntensityLevel.MEDIUM: "Use balanced therapeutic approach with moderate guidance. Include supportive challenges when appropriate.",
            IntensityLevel.HIGH: "Use direct, intensive therapeutic language. Include challenging questions and deeper exploration.",
        }

        # Conversation style adaptations
        style_guidance = {
            ConversationStyle.GENTLE: "Use soft, nurturing tone. Emphasize comfort and patience.",
            ConversationStyle.DIRECT: "Use clear, straightforward communication. Provide honest, practical feedback.",
            ConversationStyle.EXPLORATORY: "Use curious, open-ended questions. Encourage self-discovery and multiple perspectives.",
            ConversationStyle.SUPPORTIVE: "Use encouraging, validating language. Focus on strengths and positive reinforcement.",
        }

        # Therapeutic approach integration
        approach_techniques = []
        for approach in preferences.preferred_approaches:
            if approach == TherapeuticApproach.CBT:
                approach_techniques.append(
                    "cognitive behavioral techniques (thought challenging, behavioral experiments)"
                )
            elif approach == TherapeuticApproach.MINDFULNESS:
                approach_techniques.append(
                    "mindfulness practices (present-moment awareness, breathing exercises)"
                )
            elif approach == TherapeuticApproach.NARRATIVE:
                approach_techniques.append(
                    "narrative therapy techniques (story reconstruction, externalization)"
                )
            elif approach == TherapeuticApproach.SOMATIC:
                approach_techniques.append(
                    "somatic awareness (body sensations, movement, breathing)"
                )

        # Build comfort and avoid topics guidance
        comfort_guidance = ""
        if preferences.comfort_topics:
            comfort_guidance = f"Naturally incorporate these comfort topics when appropriate: {', '.join(preferences.comfort_topics[:5])}"

        avoid_guidance = ""
        if preferences.avoid_topics:
            avoid_guidance = f"Completely avoid these topics: {', '.join(preferences.avoid_topics[:5])}"

        trigger_guidance = ""
        if preferences.trigger_topics:
            trigger_guidance = f"Approach these topics with extra sensitivity or avoid if possible: {', '.join(preferences.trigger_topics[:5])}"

        # Build comprehensive prompt
        prompt = f"""
Create a therapeutic narrative response for: "{user_message}"

PLAYER PREFERENCES:
- Character: {preferences.character_name}
- Setting: {preferences.preferred_setting.value.replace("_", " ")}
- Intensity Level: {preferences.intensity_level.value} - {intensity_guidance[preferences.intensity_level]}
- Conversation Style: {preferences.conversation_style.value} - {style_guidance[preferences.conversation_style]}
- Therapeutic Goals: {", ".join(preferences.therapeutic_goals[:3]) if preferences.therapeutic_goals else "General wellbeing"}

THERAPEUTIC APPROACH:
{f"Integrate these approaches: {', '.join(approach_techniques)}" if approach_techniques else "Use general therapeutic principles"}

CONTENT GUIDELINES:
{comfort_guidance}
{avoid_guidance}
{trigger_guidance}

RESPONSE REQUIREMENTS:
1. Acknowledge user's message with empathy matching their {preferences.conversation_style.value} style preference
2. Continue immersive narrative in {preferences.preferred_setting.value.replace("_", " ")} setting
3. Apply {preferences.intensity_level.value} intensity therapeutic intervention
4. Include relevant therapeutic techniques from preferred approaches
5. Ask questions appropriate to {preferences.conversation_style.value} style
6. Keep response 2-3 sentences maximum
7. Maintain warm, therapeutic tone as {preferences.character_name}

Response:"""

        return prompt

    def _generate_enhanced_therapeutic_response(
        self,
        user_message: str,
        context: dict,
        preferences: PlayerPreferences | None = None,
    ) -> str:
        """Generate enhanced therapeutic response using advanced pattern matching with preference awareness."""
        turn_count = context.get("turn_count", 1)
        user_lower = user_message.lower()

        # Get character name and setting from preferences or defaults
        character_name = (
            preferences.character_name
            if preferences
            else context.get("character_name", "Alex")
        )
        setting = (
            preferences.preferred_setting.value.replace("_", " ")
            if preferences
            else context.get("setting", "peaceful forest")
        )

        # Analyze user message for emotional content
        anxiety_keywords = [
            "anxious",
            "worried",
            "nervous",
            "scared",
            "afraid",
            "stress",
        ]
        calm_keywords = ["calm", "peaceful", "relaxed", "better", "good"]
        exploration_keywords = ["explore", "deeper", "more", "continue", "next"]
        nature_keywords = ["birds", "trees", "forest", "stream", "flowers", "clearing"]

        # Contextual response generation based on content analysis
        if any(word in user_lower for word in anxiety_keywords):
            responses = [
                "I hear that you're feeling anxious, and that's completely understandable. Let's imagine we're standing at the edge of a peaceful forest where the air is fresh and clean. Can you take a deep breath with me and notice how the gentle breeze feels on your skin?",
                "Anxiety can feel overwhelming, but you're safe here in this moment. Picture yourself sitting by a calm stream where the water flows gently over smooth stones. As you listen to this soothing sound, what do you notice happening in your body?",
                "It takes courage to acknowledge those anxious feelings. Imagine we're in a sunlit meadow where wildflowers sway gently in the breeze. With each breath, you can let go of one worry. What would you like to release first?",
            ]
        elif any(word in user_lower for word in calm_keywords):
            responses = [
                "I'm so glad you're feeling more at peace. This sense of calm is something you can carry with you always. As we continue through this tranquil forest, what draws your attention - the dappled sunlight through the leaves or the soft sounds of nature around us?",
                "That's wonderful that you're finding your center. You've discovered something powerful about your ability to find peace. As we walk along this peaceful path, what would you like to explore about this feeling of calm?",
                "Your growing sense of tranquility is beautiful to witness. You're learning to trust in your own capacity for peace. What aspect of this serene forest setting speaks most deeply to you right now?",
            ]
        elif any(word in user_lower for word in exploration_keywords):
            responses = [
                "Your curiosity and willingness to explore is inspiring. Let's venture deeper into this enchanted forest where ancient trees hold wisdom and every step reveals new wonders. What do you hope to discover about yourself on this journey?",
                "I love your spirit of exploration. As we follow this winding path deeper into the forest, imagine that each step represents growing self-understanding. What questions about yourself are you most curious to explore?",
                "Your openness to go deeper shows real courage. Picture us approaching a hidden grove where the light filters through in magical ways. This sacred space holds insights just for you. What feels ready to be discovered?",
            ]
        elif any(word in user_lower for word in nature_keywords):
            responses = [
                "Nature has such a powerful way of speaking to our souls. The birds you're hearing are like messengers of peace, reminding us that we're part of something larger and more beautiful. How does connecting with these natural sounds affect your breathing?",
                "The forest is alive with gentle wisdom all around us. Each tree, each flower, each creature has something to teach us about resilience and growth. What do you think this peaceful forest might want to share with you today?",
                "You're so attuned to the natural world around us. This connection you're feeling is a form of mindfulness that can ground you anytime you need it. What other details in this beautiful setting are calling for your attention?",
            ]
        else:
            # General therapeutic responses
            responses = [
                "Thank you for sharing that with me. Your words matter, and I'm here to listen. Imagine we're sitting together in a comfortable spot in this peaceful forest. What would feel most supportive for you to explore right now?",
                "I appreciate your openness in this moment. Sometimes the most important conversations happen in spaces like this - surrounded by the gentle presence of nature. What's stirring in your heart that you'd like to give voice to?",
                "Your willingness to be present here is meaningful. In this safe space among the trees, you can take all the time you need. What feels most important for you to focus on as we continue this journey together?",
            ]

        # Select response based on turn count for natural progression
        response_index = min(turn_count - 1, len(responses) - 1)
        return responses[response_index]


# Initialize AI generator
ai_generator = TherapeuticAIGenerator()

# FastAPI app setup
app = FastAPI(title="Enhanced TTA API Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize AI generator on startup."""
    await ai_generator.initialize()
    logger.info("🚀 Enhanced TTA API Server started")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "ai_available": ai_generator.api_available,
        "mode": "AI-Powered" if ai_generator.api_available else "Enhanced Therapeutic",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/auth/login")
async def login(credentials: dict):
    """Demo login endpoint."""
    username = credentials.get("username")
    password = credentials.get("password")

    if username == "demo_user" and password == "demo_password":
        token = f"demo_token_{uuid.uuid4().hex[:24]}"
        return {
            "token": token,  # Frontend expects 'token', not 'access_token'
            "access_token": token,  # Keep both for compatibility
            "token_type": "bearer",
            "user": {"username": username, "id": "demo_user_id"},
        }

    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/players/{player_id}/characters")
async def get_characters(player_id: str):
    """Get player characters."""
    return {
        "characters": [
            {
                "id": "char_001",
                "name": "Alex the Explorer",
                "background": "A curious soul seeking inner peace through nature",
                "therapeutic_goals": [
                    "Reduce anxiety",
                    "Build confidence",
                    "Find inner calm",
                ],
            }
        ]
    }


@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Enhanced WebSocket chat endpoint with real AI integration and player preferences."""
    # Extract authentication and session info
    token = websocket.query_params.get("token")
    session_id = websocket.query_params.get("session_id", str(uuid.uuid4()))
    player_id = websocket.query_params.get(
        "player_id"
    )  # Extract player ID for preferences

    if not token or not token.startswith("demo_token_"):
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await websocket.accept()
    logger.info(f"🔌 WebSocket connected - Session: {session_id}, Player: {player_id}")

    # Load player preferences if available
    preferences = None
    if player_id and player_id in player_preferences:
        try:
            preferences = PlayerPreferences(**player_preferences[player_id])
            logger.info(f"✅ Loaded preferences for player: {player_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load preferences for player {player_id}: {e}")

    # Initialize session with preference-aware defaults
    if session_id not in sessions:
        character_name = preferences.character_name if preferences else "Alex"
        setting = (
            preferences.preferred_setting.value.replace("_", " ")
            if preferences
            else "peaceful forest"
        )

        sessions[session_id] = {
            "session_id": session_id,
            "player_id": player_id,
            "character_id": "char_001",
            "character_name": character_name,
            "setting": setting,
            "turn_count": 0,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "preferences_loaded": preferences is not None,
        }
        chat_history[session_id] = []

    # Send welcome message
    welcome_msg = "Welcome to your therapeutic storytelling journey, Alex. I'm here to guide you through a peaceful forest where you can explore your thoughts and feelings safely. What brings you here today?"

    await websocket.send_text(
        json.dumps(
            {
                "type": "assistant_message",
                "content": {"text": welcome_msg},
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "metadata": {
                    "turn_count": 0,
                    "ai_generated": False,
                    "therapeutic_context": "welcome",
                },
            }
        )
    )

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "user_message":
                user_message = message_data.get("message", "")
                sessions[session_id]["turn_count"] += 1

                # Store user message
                user_msg = {
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat(),
                }
                sessions[session_id]["messages"].append(user_msg)

                # Generate AI response with preferences
                context = {
                    "turn_count": sessions[session_id]["turn_count"],
                    "character_name": sessions[session_id]["character_name"],
                    "setting": sessions[session_id]["setting"],
                }

                (
                    ai_response,
                    is_ai_generated,
                ) = await ai_generator.generate_therapeutic_response(
                    user_message, context, preferences
                )

                # Store AI response
                ai_msg = {
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().isoformat(),
                }
                sessions[session_id]["messages"].append(ai_msg)

                # Store in chat history
                chat_history[session_id].append(
                    {
                        "user_message": user_message,
                        "ai_response": ai_response,
                        "timestamp": datetime.now().isoformat(),
                        "ai_generated": is_ai_generated,
                    }
                )

                # Send response back to client
                response_data = {
                    "type": "assistant_message",
                    "content": {"text": ai_response},
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "metadata": {
                        "turn_count": sessions[session_id]["turn_count"],
                        "ai_generated": is_ai_generated,
                        "therapeutic_context": "forest_exploration",
                    },
                }

                await websocket.send_text(json.dumps(response_data))
                logger.info(
                    f"💬 Processed message - Session: {session_id}, Turn: {sessions[session_id]['turn_count']}, AI: {is_ai_generated}"
                )

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected - Session: {session_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        await websocket.close(code=1011, reason="Internal server error")


# Player Preferences API Endpoints


@app.get("/api/preferences/{player_id}", response_model=PlayerPreferences)
async def get_player_preferences(player_id: str):
    """Get player preferences by player ID."""
    if player_id not in player_preferences:
        raise HTTPException(status_code=404, detail="Player preferences not found")

    return PlayerPreferences(**player_preferences[player_id])


@app.post("/api/preferences", response_model=PlayerPreferences)
async def create_player_preferences(preferences: PlayerPreferences):
    """Create new player preferences."""
    preferences.created_at = datetime.now().isoformat()
    preferences.updated_at = datetime.now().isoformat()

    player_preferences[preferences.player_id] = preferences.dict()
    logger.info(f"✅ Created preferences for player: {preferences.player_id}")

    return preferences


@app.put("/api/preferences/{player_id}", response_model=PlayerPreferences)
async def update_player_preferences(player_id: str, preferences: PlayerPreferences):
    """Update existing player preferences."""
    if player_id not in player_preferences:
        raise HTTPException(status_code=404, detail="Player preferences not found")

    preferences.player_id = player_id
    preferences.updated_at = datetime.now().isoformat()
    preferences.version = player_preferences[player_id].get("version", 1) + 1

    player_preferences[player_id] = preferences.dict()
    logger.info(f"✅ Updated preferences for player: {player_id}")

    return preferences


@app.delete("/api/preferences/{player_id}")
async def delete_player_preferences(player_id: str):
    """Delete player preferences."""
    if player_id not in player_preferences:
        raise HTTPException(status_code=404, detail="Player preferences not found")

    del player_preferences[player_id]
    logger.info(f"🗑️ Deleted preferences for player: {player_id}")

    return {"message": "Preferences deleted successfully"}


@app.post("/api/preferences/validate", response_model=PreferenceValidationResult)
async def validate_player_preferences(preferences: PlayerPreferences):
    """Validate player preferences."""
    errors = []
    warnings = []

    # Basic validation
    if not preferences.player_id:
        errors.append("Player ID is required")

    if not preferences.character_name or len(preferences.character_name.strip()) == 0:
        errors.append("Character name cannot be empty")

    if len(preferences.preferred_approaches) == 0:
        warnings.append(
            "No therapeutic approaches selected - consider choosing at least one"
        )

    if len(preferences.therapeutic_goals) == 0:
        warnings.append("No therapeutic goals specified - consider setting some goals")

    # Advanced validation
    if (
        preferences.intensity_level == IntensityLevel.HIGH
        and len(preferences.trigger_topics) == 0
    ):
        warnings.append(
            "High intensity with no trigger topics specified - consider adding trigger topics for safety"
        )

    return PreferenceValidationResult(
        is_valid=len(errors) == 0, errors=errors, warnings=warnings
    )


@app.post("/api/preferences/preview", response_model=PreferencePreviewResponse)
async def generate_preference_preview(request: PreferencePreviewRequest):
    """Generate a preview of how preferences affect AI responses."""
    try:
        # Create context for preview
        context = {
            "turn_count": 1,
            "character_name": request.preferences.character_name,
            "setting": request.preferences.preferred_setting.value.replace("_", " "),
        }

        # Generate response with preferences
        response, ai_generated = await ai_generator.generate_therapeutic_response(
            request.test_message, context, request.preferences
        )

        # Identify applied adaptations
        adaptations = []
        adaptations.append(f"Intensity: {request.preferences.intensity_level.value}")
        adaptations.append(f"Style: {request.preferences.conversation_style.value}")
        if request.preferences.preferred_approaches:
            adaptations.append(
                f"Approaches: {len(request.preferences.preferred_approaches)} selected"
            )
        if request.preferences.character_name != "Alex":
            adaptations.append(f"Character: {request.preferences.character_name}")
        if request.preferences.preferred_setting != PreferredSetting.PEACEFUL_FOREST:
            adaptations.append(
                f"Setting: {request.preferences.preferred_setting.value.replace('_', ' ')}"
            )

        return PreferencePreviewResponse(
            user_message=request.test_message,
            preferences=request.preferences,
            preview_response=response,
            adaptations_applied=adaptations,
        )

    except Exception as e:
        logger.error(f"❌ Preview generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")


@app.get("/api/preferences/{player_id}/export")
async def export_player_preferences(player_id: str):
    """Export player preferences as JSON."""
    if player_id not in player_preferences:
        raise HTTPException(status_code=404, detail="Player preferences not found")

    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "export_version": "1.0",
        "preferences": player_preferences[player_id],
    }

    return export_data


@app.post("/api/preferences/{player_id}/import", response_model=PlayerPreferences)
async def import_player_preferences(player_id: str, import_data: dict):
    """Import player preferences from JSON."""
    try:
        # Extract preferences from import data
        if "preferences" in import_data:
            preferences_data = import_data["preferences"]
        else:
            preferences_data = import_data

        # Ensure player_id matches
        preferences_data["player_id"] = player_id
        preferences_data["updated_at"] = datetime.now().isoformat()
        preferences_data["version"] = preferences_data.get("version", 1) + 1

        # Validate and create preferences object
        preferences = PlayerPreferences(**preferences_data)

        # Store preferences
        player_preferences[player_id] = preferences.dict()
        logger.info(f"📥 Imported preferences for player: {player_id}")

        return preferences

    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to import preferences: {str(e)}"
        )


if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced TTA API Server...")
    logger.info(
        f"🤖 AI Mode: {'OpenRouter API' if os.getenv('OPENROUTER_API_KEY') else 'Enhanced Therapeutic'}"
    )

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
