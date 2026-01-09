# WebSocket Chat Backend Specification (Task 8)

## Overview

Implements the backend for real-time therapeutic chat via WebSocket. Provides:

- Authenticated WebSocket connection per player
- Connection management and per-player pooling
- Message schema for user/assistant/system/interactive messages
- Therapeutic message processing pipeline integrating existing managers
- Support for interactive elements (buttons, guided exercises)

## Endpoint

- Path: `/ws/chat`
- Protocol: WebSocket
- Auth: JWT required via one of:
  - Query param `token=<JWT>`
  - Header `Authorization: Bearer <JWT>` (if client can set)
- Options:
  - `typing=1|true|yes` to opt-in to typing start/stop events
- On connect: validate token; attach player_id; send initial system message

## Message Schema

- Incoming (client -> server):

```json
{
  "type": "user_message" | "interaction" | "feedback",
  "session_id": "string?",
  "content": {"text": "..."} | {"action": "button_click", "id": "..."} | {"rating": 1..5, "text": "..."},
  "metadata": {"character_id": "...", "world_id": "..."}
}
```

- Outgoing (server -> client):

```json
{
  "id": "msg_<uuid>",
  "role": "assistant" | "system" | "interactive",
  "session_id": "string?",
  "content": {
    "text": "...",
    "elements": [
      {"type": "button", "id": "..", "label": ".."},
      {"type": "resource", "id": "..", "label": "..", "method": "phone|text|chat|website", "info": "...", "emergency": true|false},
      {"type": "recommendation", "id": "..", "label": "..."},
      {"type": "instruction", "id": "..", "label": "..."},
      {"type": "progress", "id": "..", "label": "..."}
    ]
  },
  "timestamp": "ISO8601",
  "metadata": {
    "recommendations": [...],
    "safety": {"crisis": false, "types": ["..."]}
  }
}
```

## Components

- ConnectionManager
  - Tracks `player_id -> set[WebSocket]`
  - Methods: `connect(ws, player_id)`, `disconnect(ws, player_id)`, `send_json(ws|player_id, payload)`, `broadcast_to_player(player_id, payload)`
- ChatProcessor
  - Depends on: `SessionIntegrationManager`, `PersonalizationServiceManager`
  - `process(player_id, incoming) -> list[OutgoingMessage]`
  - Handles:
    - user_message: produce assistant reply via personalization engine (mock adapter ok)
    - interaction: acknowledge and possibly return next step
    - feedback: invoke personalization feedback processing
- Message models in Pydantic for validation

## Safety & Therapeutic Considerations

- Use existing middleware patterns for safety but note WebSockets bypass HTTP middleware; validate and add crisis/safety metadata in processor using PersonalizationServiceManager.detect_crisis_situation
- Surface crisis resources in assistant messages when crisis detected (as resource elements)
- Rate limiting: connection-level simple throttling (optional future enhancement)

## Testing

- Connect without token -> reject/close with policy violation
- Connect with valid token -> welcome message
- Send user_message -> assistant response returned
- Send interaction payload -> interactive response structure
- Guided exercise flow: button click returns an instruction + a "Complete" button; clicking the completion button emits a progress acknowledgement

## Integration

- New router `src/player_experience/api/routers/chat.py` mounted with prefix `/ws` (endpoint `/ws/chat`)
- Add import/include in `app.py`
- Reuse existing SECRET_KEY/verify_token and models/managers

## Operational Events & Observability

- Typing indicators:
  - When `typing` option is enabled, server emits system messages with `{"event": "typing", "status": "start|stop"}`
- Metrics:
  - In-memory counters for `connections`, `messages_in`, `messages_out`, `crisis_detected`

## Interactive Elements

- Assistant may include interactive buttons for guided exercises when context suggests anxiety/panic or when crisis is detected
- Interaction handling:
  - Button click (e.g., id: "ex_breathing") returns an `instruction` element and a `button` to complete the exercise (id suffix `_complete`)
  - Completion button click records a progress marker and returns a `progress` element acknowledgement

## Progress Tracking

- On guided exercise completion, a `ProgressMarker` of type `SKILL_ACQUIRED` is recorded via `SessionIntegrationManager.add_progress_marker`
- Marker fields: `marker_id`, `marker_type`, `description`, `achieved_at`, `therapeutic_value`
- Enables downstream analytics in tasks 9.x

- Logging:
  - Structured logs for `ws_connect`, `ws_disconnect` and general message flow

## Non-goals (future work)

- Group chat/broadcast across players
- Persistence of chat history


---
**Logseq:** [[TTA.dev/_archive/Kiro/Specs/Specs/Player-experience-interface/Websocket-chat-backend]]
