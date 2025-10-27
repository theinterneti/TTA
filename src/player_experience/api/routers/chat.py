"""
WebSocket chat router for the Player Experience API.

Implements authenticated WebSocket endpoint for therapeutic chat.
"""

from __future__ import annotations

import contextlib
import json
import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from ...database.session_repository import SessionRepository
from ...managers.personalization_service_manager import (
    PersonalizationServiceManager,
    PlayerFeedback,
)
from ...managers.session_integration_manager import SessionIntegrationManager
from ...models.enums import ProgressMarkerType
from ...models.session import ProgressMarker
from ..auth import TokenData, verify_token

# Initialize logger first
logger = logging.getLogger(__name__)

# Import agent orchestration system
# Use lowercase to avoid Pyright constant redefinition warnings
agent_orchestration_available: bool
therapeutic_safety_available: bool

try:
    from tta_ai.orchestration.realtime.agent_event_integration import (
        get_agent_event_integrator,
    )
    from tta_ai.orchestration.therapeutic_safety import (
        CrisisInterventionManager,
        SafetyLevel,
        get_global_safety_service,
    )

    agent_orchestration_available = True
    therapeutic_safety_available = True
except ImportError:
    logger.warning("Agent orchestration system not available, using fallback responses")
    agent_orchestration_available = False
    therapeutic_safety_available = False

# In-memory metrics (testing/observability aid)
METRICS: dict[str, int] = {
    "connections": 0,
    "messages_in": 0,
    "messages_out": 0,
    "crisis_detected": 0,
}


def reset_metrics() -> None:
    METRICS.update(
        {
            "connections": 0,
            "messages_in": 0,
            "messages_out": 0,
            "crisis_detected": 0,
        }
    )


router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections per player."""

    def __init__(self) -> None:
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, player_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(player_id, set()).add(websocket)
        METRICS["connections"] += 1
        logger.info(
            "ws_connect player_id=%s active=%d",
            player_id,
            len(self.active_connections.get(player_id, set())),
        )

    def disconnect(self, player_id: str, websocket: WebSocket) -> None:
        conns = self.active_connections.get(player_id)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                self.active_connections.pop(player_id, None)
        logger.info("ws_disconnect player_id=%s", player_id)

    async def send_json(self, websocket: WebSocket, payload: dict[str, Any]) -> None:
        METRICS["messages_out"] += 1
        await websocket.send_text(json.dumps(payload))

    async def broadcast_to_player(
        self, player_id: str, payload: dict[str, Any]
    ) -> None:
        for ws in self.active_connections.get(player_id, set()):
            await self.send_json(ws, payload)


manager = ConnectionManager()


def _auth_from_ws(websocket: WebSocket) -> TokenData:
    """Extract and verify JWT from query param or headers for WebSocket connections."""
    token: str | None = None
    # Try query parameter first
    token = websocket.query_params.get("token")
    if not token:
        # Fallback to Authorization header if present
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
    if not token:
        # No token provided
        raise PermissionError("Missing token")

    try:
        return verify_token(token)
    except Exception as e:
        # Normalize auth errors to PermissionError for WebSocket close codes
        raise PermissionError(str(e)) from e


def _outgoing_message(
    role: str,
    content: dict[str, Any],
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "role": role,
        "session_id": session_id,
        "content": content,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metadata": metadata or {},
    }


def _event_message(
    event: str, data: dict[str, Any] | None = None, session_id: str | None = None
) -> dict[str, Any]:
    return _outgoing_message(
        role="system",
        content={"event": event, **(data or {})},
        session_id=session_id,
        metadata={},
    )


def _basic_crisis_scan(text: str) -> bool:
    low = text.lower()
    keywords = [
        "suicide",
        "kill myself",
        "self-harm",
        "want to die",
        "can't go on",
        "panic",
        "overdose",
    ]
    return any(k in low for k in keywords)


@router.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for therapeutic chat.

    Auth via query param token or Authorization header.
    """
    # Authenticate
    try:
        token_data = _auth_from_ws(websocket)
    except PermissionError:
        # Accept then close so client context manager enters before failure
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    player_id = token_data.player_id or ""
    await manager.connect(player_id, websocket)

    # Typing indicator opt-in (typing=1|true|yes)
    typing_flag = websocket.query_params.get("typing", "0").lower() in {
        "1",
        "true",
        "yes",
    }

    # Managers (could be dependency-injected if needed)
    sim = SessionIntegrationManager(SessionRepository())
    psm = PersonalizationServiceManager()

    # Send welcome/system message
    welcome = _outgoing_message(
        role="system",
        content={"text": "Connected to therapeutic chat. You're safe here."},
        metadata={"safety": {"crisis": False}},
    )
    await manager.send_json(websocket, welcome)

    # Lightweight per-connection rate limit to protect backend (defaults lenient)
    from collections import deque

    window = deque()  # timestamps of received messages
    window_seconds = 2  # 2s window
    max_msgs = 10  # allow up to 10 msgs per 2s per connection

    # Input validator for user messages (reuse central security module)
    from ...security.input_validator import InputType, get_security_validator

    validator = get_security_validator()

    try:
        while True:
            raw = await websocket.receive_text()

            # Sliding window rate limit per connection
            now_ts = datetime.utcnow().timestamp()
            while window and (now_ts - window[0]) > window_seconds:
                window.popleft()
            window.append(now_ts)
            if len(window) > max_msgs:
                # Soft warn and continue (do not drop connection), echo system notice
                warn = _outgoing_message(
                    "system", {"text": "Rate limit: please slow down."}
                )
                await manager.send_json(websocket, warn)
                continue

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                err = _outgoing_message("system", {"text": "Invalid message format."})
                await manager.send_json(websocket, err)
                continue

            METRICS["messages_in"] += 1

            mtype = msg.get("type")
            session_id: str | None = msg.get("session_id")
            metadata: dict[str, Any] = msg.get("metadata") or {}
            content: dict[str, Any] = msg.get("content") or {}

            # Basic input validation/sanitization for user messages
            if mtype == "user_message":
                text = content.get("text", "")
                vr = validator.validate_and_sanitize(
                    text, input_type=InputType.USER_MESSAGE
                )
                # If invalid or critical issues, send a friendly error and continue
                if not vr.is_valid and vr.severity.value in {"high", "critical"}:
                    err = _outgoing_message(
                        "system",
                        {"text": "Message contains unsafe content. Please rephrase."},
                    )
                    await manager.send_json(websocket, err)
                    continue
                # Apply sanitization if available
                if vr.sanitized_input is not None:
                    content["text"] = vr.sanitized_input

            # Ensure session exists or create default
            if not session_id:
                # Try active session; else create a new one
                session = await sim.get_active_session(player_id)
                if not session:
                    session = await sim.create_session(
                        player_id=player_id,
                        character_id=metadata.get("character_id", "char-default"),
                        world_id=metadata.get("world_id", "world-default"),
                    )
                session_id = session.session_id if session else None

            if mtype == "user_message":
                text = content.get("text", "")

                # Progressive feedback: Start typing indicator
                if typing_flag:
                    await manager.send_json(
                        websocket,
                        _event_message("typing", {"status": "start"}, session_id),
                    )

                # Progressive feedback: Analyzing input
                await manager.send_json(
                    websocket,
                    _event_message(
                        "progress",
                        {
                            "stage": "analyzing",
                            "message": "Understanding your message...",
                        },
                        session_id,
                    ),
                )

                # Detect crisis via PSM
                crisis_detected, crisis_types, crisis_resources = (
                    psm.detect_crisis_situation(
                        player_id, text, context={"session_id": session_id, **metadata}
                    )
                )
                if crisis_detected:
                    METRICS["crisis_detected"] += 1

                # Generate AI response using agent orchestration system
                ai_response_text = text  # Fallback to echo
                safety_validation_result = None
                crisis_intervention = None

                if agent_orchestration_available:
                    try:
                        # Progressive feedback: Processing with AI
                        await manager.send_json(
                            websocket,
                            _event_message(
                                "progress",
                                {
                                    "stage": "processing",
                                    "message": "Processing your input...",
                                },
                                session_id,
                            ),
                        )

                        # Get agent event integrator
                        agent_integrator = get_agent_event_integrator(
                            agent_id=f"chat_agent_{player_id}"
                        )

                        # Progressive feedback: Building world context
                        await manager.send_json(
                            websocket,
                            _event_message(
                                "progress",
                                {
                                    "stage": "world_building",
                                    "message": "Building narrative context...",
                                },
                                session_id,
                            ),
                        )

                        # Execute complete IPA → WBA → NGA workflow
                        # Note: Runtime type differs from static type - agent_integrator has execute_complete_workflow at runtime
                        workflow_result = await agent_integrator.execute_complete_workflow(  # type: ignore[attr-defined]
                            user_input=text,
                            session_id=session_id or "default",
                            world_id=metadata.get("world_id"),
                            workflow_id=f"chat_{player_id}_{int(datetime.utcnow().timestamp() * 1000)}",
                        )

                        # Progressive feedback: Generating response
                        await manager.send_json(
                            websocket,
                            _event_message(
                                "progress",
                                {
                                    "stage": "generating",
                                    "message": "Crafting therapeutic response...",
                                },
                                session_id,
                            ),
                        )

                        # Extract narrative response from NGA
                        ai_response_text = workflow_result.get("nga_result", {}).get(
                            "story", text
                        )

                        # Therapeutic Safety Validation: Validate AI-generated response
                        if therapeutic_safety_available:
                            try:
                                safety_service = get_global_safety_service()
                                safety_validation_result = (
                                    await safety_service.validate_text(ai_response_text)
                                )

                                # If response is blocked, use alternative content
                                if (
                                    safety_validation_result.level
                                    == SafetyLevel.BLOCKED
                                ):
                                    logger.warning(
                                        f"AI response blocked by safety validation for session {session_id}"
                                    )
                                    ai_response_text = (
                                        safety_validation_result.alternative_content
                                        or safety_service.suggest_alternative(
                                            SafetyLevel.BLOCKED, ai_response_text
                                        )
                                    )
                                    metadata["safety_override"] = True

                                # If crisis detected in AI response, initiate intervention
                                if safety_validation_result.crisis_detected:
                                    crisis_manager = CrisisInterventionManager()
                                    crisis_assessment = crisis_manager.assess_crisis(
                                        safety_validation_result,
                                        {
                                            "session_id": session_id,
                                            "player_id": player_id,
                                        },
                                    )
                                    crisis_intervention = (
                                        crisis_manager.initiate_intervention(
                                            crisis_assessment,
                                            session_id or "default",
                                            player_id,
                                        )
                                    )
                                    logger.critical(
                                        f"Crisis intervention initiated: {crisis_intervention.intervention_id}"
                                    )
                                    metadata["crisis_intervention_id"] = (
                                        crisis_intervention.intervention_id
                                    )

                                # Add safety metadata
                                metadata["safety_validation"] = {
                                    "level": safety_validation_result.level.value,
                                    "score": safety_validation_result.score,
                                    "crisis_detected": safety_validation_result.crisis_detected,
                                    "escalation_recommended": safety_validation_result.escalation_recommended,
                                }

                            except Exception as safety_error:
                                logger.error(
                                    f"Therapeutic safety validation failed: {safety_error}"
                                )

                        # Add workflow metadata
                        metadata["workflow_id"] = workflow_result.get("workflow_id")
                        metadata["ipa_intent"] = (
                            workflow_result.get("ipa_result", {})
                            .get("routing", {})
                            .get("intent")
                        )

                        logger.info(
                            f"AI response generated via agent orchestration for session {session_id}"
                        )

                    except Exception as e:
                        logger.error(f"Agent orchestration failed, using fallback: {e}")
                        # Progressive feedback: Using fallback
                        await manager.send_json(
                            websocket,
                            _event_message(
                                "progress",
                                {
                                    "stage": "fallback",
                                    "message": "Generating response...",
                                },
                                session_id,
                            ),
                        )

                        # Fall back to personalization engine
                        adapted = psm.personalization_engine.personalize_content(
                            user_id=player_id,
                            content=text,
                            session_state={},
                            profile={},
                        )
                        ai_response_text = adapted.get("adapted_content", text)
                else:
                    # Progressive feedback: Using personalization
                    await manager.send_json(
                        websocket,
                        _event_message(
                            "progress",
                            {
                                "stage": "personalizing",
                                "message": "Personalizing response...",
                            },
                            session_id,
                        ),
                    )

                    # Use personalization engine as fallback
                    adapted = psm.personalization_engine.personalize_content(
                        user_id=player_id,
                        content=text,
                        session_state={},
                        profile={},
                    )
                    ai_response_text = adapted.get("adapted_content", text)

                # Progressive feedback: Complete
                await manager.send_json(
                    websocket,
                    _event_message(
                        "progress",
                        {"stage": "complete", "message": "Response ready"},
                        session_id,
                    ),
                )

                # Recommendations
                recs = psm.get_adaptive_recommendations(
                    player_id, context={"session_id": session_id}
                )
                # Build assistant response with optional safety block and interactive resources
                # Ensure metadata is JSON-serializable (avoid datetimes)
                safe_recs: list[dict[str, Any]] = [
                    {
                        "recommendation_id": getattr(
                            r, "recommendation_id", getattr(r, "id", "")
                        ),
                        "title": getattr(r, "title", ""),
                        "description": getattr(r, "description", ""),
                        "recommendation_type": getattr(
                            r, "recommendation_type", getattr(r, "type", "")
                        ),
                        "priority": int(getattr(r, "priority", 1)),
                    }
                    for r in (recs or [])
                ]
                reply_metadata: dict[str, Any] = {
                    "recommendations": safe_recs,
                    "safety": {
                        "crisis": bool(crisis_detected),
                        "types": (
                            [ct.value for ct in crisis_types] if crisis_detected else []
                        ),
                    },
                }
                reply_content: dict[str, Any] = {"text": ai_response_text}
                elements: list[dict[str, Any]] = []
                if crisis_detected and crisis_resources:
                    elements.extend(
                        [
                            {
                                "type": "resource",
                                "id": res.resource_id,
                                "label": res.name,
                                "method": res.contact_method,
                                "info": res.contact_info,
                                "emergency": res.is_emergency,
                            }
                            for res in crisis_resources
                        ]
                    )
                # Suggest interactive buttons for guided exercises on anxious keywords
                anxious = any(
                    kw in text.lower()
                    for kw in ["anxious", "panic", "overwhelmed", "stressed"]
                ) or bool(crisis_detected)
                if anxious:
                    elements.extend(
                        [
                            {
                                "type": "button",
                                "id": "ex_breathing",
                                "label": "Try 4-7-8 breathing",
                            },
                            {
                                "type": "button",
                                "id": "ex_grounding",
                                "label": "5-4-3-2-1 grounding",
                            },
                        ]
                    )
                if elements:
                    reply_content["elements"] = elements
                reply = _outgoing_message(
                    role="assistant",
                    content=reply_content,
                    session_id=session_id,
                    metadata=reply_metadata,
                )

                # Therapeutic audit log for message delivery
                from ...monitoring.logging_config import get_logger

                get_logger(__name__).therapeutic_audit(
                    "assistant_reply",
                    therapeutic_event="message_delivery",
                    intervention_type="chat_response",
                    metadata={"player_id": player_id, "session_id": session_id},
                )

                await manager.send_json(websocket, reply)

                if typing_flag:
                    await manager.send_json(
                        websocket,
                        _event_message("typing", {"status": "stop"}, session_id),
                    )

            elif mtype == "interaction":
                # Handle interactive actions (e.g., button clicks to start/complete exercises)
                action = content.get("action") or content.get("type") or "button_click"
                item_id = content.get("id")

                # Default acknowledgement
                ack_elements: list[dict[str, Any]] = [
                    {"type": "ack", "id": item_id, "label": "Received"}
                ]

                # Guided exercise start
                if action in {"button_click", "start_exercise"} and item_id in {
                    "ex_breathing",
                    "ex_grounding",
                }:
                    instructions = {
                        "ex_breathing": "Let's try 4-7-8 breathing. Inhale for 4, hold for 7, exhale for 8. Tap 'Complete' when you're done.",
                        "ex_grounding": "Let's try 5-4-3-2-1 grounding. Name 5 things you see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste. Tap 'Complete' when done.",
                    }[item_id]
                    ack_elements = [
                        {
                            "type": "instruction",
                            "id": f"{item_id}_steps",
                            "label": instructions,
                        },
                        {
                            "type": "button",
                            "id": f"{item_id}_complete",
                            "label": "Complete",
                        },
                    ]

                # Guided exercise completion -> record progress marker
                elif (
                    action in {"button_click", "complete_exercise"}
                    and item_id
                    and item_id.endswith("_complete")
                ):
                    base = item_id.replace("_complete", "")
                    marker = ProgressMarker(
                        marker_id=f"pm_{uuid.uuid4().hex[:10]}",
                        marker_type=ProgressMarkerType.SKILL_ACQUIRED,
                        description=f"Completed guided exercise: {base}",
                        achieved_at=datetime.utcnow(),
                        therapeutic_value=0.2,
                    )
                    await sim.add_progress_marker(player_id, marker)
                    ack_elements = [
                        {
                            "type": "progress",
                            "id": marker.marker_id,
                            "label": "Progress recorded",
                        },
                    ]

                ack = _outgoing_message(
                    role="interactive",
                    content={"elements": ack_elements},
                    session_id=session_id,
                )
                await manager.send_json(websocket, ack)

            elif mtype == "feedback":
                fb = PlayerFeedback(
                    feedback_id=str(uuid.uuid4()),
                    player_id=player_id,
                    session_id=session_id or "",
                    feedback_type=(
                        "text"
                        if "text" in content
                        else ("rating" if "rating" in content else "preference_change")
                    ),
                    content=content,
                )
                result = psm.process_feedback(player_id, fb)
                # After processing feedback, push updated recommendations
                recs = psm.get_adaptive_recommendations(
                    player_id, context={"session_id": session_id}
                )
                note = _outgoing_message(
                    role="system",
                    content={
                        "text": f"Feedback processed. Changes: {', '.join(result.changes_made) or 'none'}.",
                        "elements": (
                            [
                                {
                                    "type": "recommendation",
                                    "id": f"rec_{i}",
                                    "label": getattr(r, "title", "Recommendation"),
                                }  # minimal projection
                                for i, r in enumerate(recs)
                            ]
                            if recs
                            else []
                        ),
                    },
                    session_id=session_id,
                )
                await manager.send_json(websocket, note)

            elif mtype == "update_settings":
                # Accept simple therapeutic settings updates via WS
                content = msg.get("content") or {}
                # Build minimal EnhancedTherapeuticSettings from payload
                try:
                    from ...models.therapeutic_settings import (
                        EnhancedTherapeuticSettings,
                    )
                    from ...utils.normalization import (
                        normalize_approaches,
                        normalize_intensity,
                    )

                    # Normalize values
                    level = normalize_intensity(content.get("intensity_level"))
                    approaches = normalize_approaches(
                        content.get("preferred_approaches", [])
                    )
                    settings = EnhancedTherapeuticSettings(
                        settings_id="",
                        player_id=player_id,
                        intensity_level=level,
                        preferred_approaches=approaches,
                    )
                    ok, conflicts = psm.update_therapeutic_settings(player_id, settings)

                    # Persist change to the active character's therapeutic profile if session/context available
                    with contextlib.suppress(Exception):
                        sess = await sim.get_active_session(player_id)
                        if sess and getattr(sess, "character_id", None):
                            # Use the same repository instance as REST by going through the characters router dependency
                            from ...models.character import TherapeuticProfile
                            from .characters import get_character_manager_dep

                            cmanager = get_character_manager_dep()
                            current_profile = (
                                cmanager.get_character_therapeutic_profile(
                                    sess.character_id
                                )
                            )
                            if current_profile is not None:
                                updated_profile = TherapeuticProfile(
                                    primary_concerns=current_profile.primary_concerns,
                                    therapeutic_goals=current_profile.therapeutic_goals,
                                    preferred_intensity=level,
                                    comfort_zones=current_profile.comfort_zones,
                                    challenge_areas=current_profile.challenge_areas,
                                    coping_strategies=current_profile.coping_strategies,
                                    trigger_topics=current_profile.trigger_topics,
                                    therapeutic_history=current_profile.therapeutic_history,
                                    readiness_level=current_profile.readiness_level,
                                    therapeutic_approaches=approaches,
                                )
                                cmanager.update_character_therapeutic_profile(
                                    sess.character_id, updated_profile
                                )

                    text = (
                        "Settings updated successfully"
                        if ok
                        else "Settings updated with warnings"
                    )
                    resp = _outgoing_message(
                        "system",
                        {
                            "text": text,
                            "conflicts": [
                                getattr(c, "description", str(c)) for c in conflicts
                            ],
                        },
                        session_id=session_id,
                    )
                    await manager.send_json(websocket, resp)
                except Exception as e:
                    err = _outgoing_message(
                        "system",
                        {"text": f"Settings update failed: {e}"},
                        session_id=session_id,
                    )
                    await manager.send_json(websocket, err)
            elif mtype == "switch_context":
                # Switch active context (character/world/session) and acknowledge
                try:
                    # Extract desired context (if provided)
                    target_char = metadata.get("character_id") or content.get(
                        "character_id"
                    )
                    target_world = metadata.get("world_id") or content.get("world_id")
                    target_session = (
                        metadata.get("session_id")
                        or content.get("session_id")
                        or session_id
                    )

                    # If a session id is provided, try to mark it active (best-effort)
                    if target_session and target_session != session_id:
                        session_id = target_session

                    msg_text = "Context switched"
                    details = []
                    if target_char:
                        details.append(f"character {target_char}")
                    if target_world:
                        details.append(f"world {target_world}")
                    if details:
                        msg_text += " to " + ", ".join(details)
                    ack = _outgoing_message(
                        "system", {"text": msg_text + "."}, session_id=session_id
                    )
                    await manager.send_json(websocket, ack)
                except Exception as e:
                    err = _outgoing_message(
                        "system",
                        {"text": f"Context switch failed: {e}"},
                        session_id=session_id,
                    )
                    await manager.send_json(websocket, err)
            else:
                err = _outgoing_message("system", {"text": "Unknown message type."})
                await manager.send_json(websocket, err)

    except WebSocketDisconnect:
        manager.disconnect(player_id, websocket)
    except Exception:
        # Close with internal error
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        manager.disconnect(player_id, websocket)
