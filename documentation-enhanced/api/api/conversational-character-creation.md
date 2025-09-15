# Conversational Character Creation API

The Conversational Character Creation API provides a therapeutic, chat-based interface for creating personalized therapeutic companions. This API enables users to create characters through natural conversation rather than traditional forms.

## Overview

The conversational character creation system uses WebSocket connections to provide real-time, interactive character creation experiences. The system guides users through therapeutic conversations that gradually collect character information while maintaining safety and therapeutic boundaries.

## WebSocket Endpoints

### Connect to Conversational Character Creation

**Endpoint:** `ws://localhost:8000/ws/conversational-character-creation`

**Authentication:** Token-based authentication via query parameter

**Connection URL:**
```
ws://localhost:8000/ws/conversational-character-creation?token=<jwt_token>
```

#### Connection Events

**On Connect:**
- Client automatically receives a welcome message
- Conversation session is initialized
- Progress tracking begins

**On Disconnect:**
- Conversation state is preserved in Redis
- Can be resumed within session timeout period

## Message Types

### Client to Server Messages

#### Start Conversation
```json
{
  "type": "start_conversation",
  "player_id": "string",
  "metadata": {
    "source": "conversational_ui",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### User Response
```json
{
  "type": "user_response",
  "conversation_id": "string",
  "content": "string",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "source": "user_input"
  }
}
```

#### Pause Conversation
```json
{
  "type": "pause_conversation",
  "conversation_id": "string",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Resume Conversation
```json
{
  "type": "resume_conversation",
  "conversation_id": "string",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Abandon Conversation
```json
{
  "type": "abandon_conversation",
  "conversation_id": "string",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Server to Client Messages

#### Conversation Started
```json
{
  "type": "conversation_started",
  "conversation_id": "string",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Assistant Message
```json
{
  "type": "assistant_message",
  "message_id": "string",
  "conversation_id": "string",
  "content": "string",
  "timestamp": "2024-01-15T10:30:00Z",
  "stage": "welcome",
  "prompt_id": "welcome_intro",
  "context_text": "string",
  "follow_up_prompts": ["string"]
}
```

#### Progress Update
```json
{
  "type": "progress_update",
  "conversation_id": "string",
  "progress": {
    "current_stage": "identity",
    "progress_percentage": 25,
    "completed_stages": ["welcome"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Conversation Completed
```json
{
  "type": "conversation_completed",
  "conversation_id": "string",
  "character_preview": {
    "character_id": "string",
    "name": "string",
    "completeness_score": 0.85,
    "ready_for_creation": true,
    "character_preview": {
      "name": "Alice",
      "appearance": {
        "age_range": "adult",
        "gender_identity": "female",
        "physical_description": "Average height with brown hair"
      },
      "therapeutic_profile": {
        "primary_concerns": ["anxiety"],
        "preferred_intensity": "medium",
        "readiness_level": 0.7
      }
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Validation Error
```json
{
  "type": "validation_error",
  "conversation_id": "string",
  "error_message": "string",
  "error_code": "INVALID_INPUT",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Crisis Detected
```json
{
  "type": "crisis_detected",
  "conversation_id": "string",
  "crisis_level": "high",
  "support_message": "string",
  "resources": [
    {
      "name": "National Suicide Prevention Lifeline",
      "contact": "988"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Error Message
```json
{
  "type": "error",
  "error_message": "string",
  "error_code": "CONNECTION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Conversation Stages

The conversational character creation process follows these therapeutic stages:

1. **Welcome** - Initial greeting and safety establishment
2. **Identity** - Basic identity exploration (name, age, gender)
3. **Appearance** - Physical self-image and presentation
4. **Background** - Personal history and experiences
5. **Values** - Core values and beliefs exploration
6. **Relationships** - Social connections and relationship patterns
7. **Therapeutic Transition** - Gentle transition to therapeutic focus
8. **Concerns** - Primary therapeutic concerns and challenges
9. **Goals** - Therapeutic goals and desired outcomes
10. **Preferences** - Therapeutic approach preferences
11. **Readiness** - Assessment of readiness for therapeutic work
12. **Summary** - Review and confirmation of collected information
13. **Completion** - Character creation finalization

## REST API Endpoints

### Get Conversation State

**GET** `/api/conversations/{conversation_id}/state`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "conversation_id": "string",
  "player_id": "string",
  "status": "active",
  "progress": {
    "current_stage": "identity",
    "progress_percentage": 25,
    "completed_stages": ["welcome"]
  },
  "collected_data": {
    "name": "Alice",
    "age_range": "adult",
    "gender_identity": "female"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "crisis_detected": false
}
```

### Pause Conversation

**POST** `/api/conversations/{conversation_id}/pause`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "message": "Conversation paused successfully"
}
```

### Resume Conversation

**POST** `/api/conversations/{conversation_id}/resume`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "message": "Conversation resumed successfully"
}
```

### Abandon Conversation

**POST** `/api/conversations/{conversation_id}/abandon`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "success": true,
  "message": "Conversation abandoned successfully"
}
```

## Error Handling

### Error Codes

- `CONVERSATION_NOT_FOUND` - Conversation ID does not exist
- `CONVERSATION_INACTIVE` - Conversation is not in active state
- `INVALID_INPUT` - User input validation failed
- `AUTHENTICATION_ERROR` - Invalid or expired token
- `RATE_LIMIT_ERROR` - Too many requests
- `CONNECTION_ERROR` - WebSocket connection issues
- `SERVICE_ERROR` - Internal service error
- `CRISIS_ERROR` - Crisis situation detected

### Error Response Format

```json
{
  "type": "error",
  "error_message": "Human readable error message",
  "error_code": "ERROR_CODE",
  "conversation_id": "string",
  "timestamp": "2024-01-15T10:30:00Z",
  "details": {
    "additional_context": "string"
  }
}
```

## Safety and Therapeutic Compliance

### Crisis Detection

The system continuously monitors conversations for crisis indicators:
- Suicidal ideation
- Self-harm intentions
- Severe depression symptoms
- Immediate danger situations

When crisis indicators are detected:
1. Immediate crisis response message is sent
2. Professional resources are provided
3. Conversation may be paused for safety
4. Appropriate authorities may be notified (per policy)

### Content Validation

All user inputs are validated for:
- Therapeutic appropriateness
- Safety compliance
- Boundary violations
- Inappropriate content

### Data Privacy

- All conversation data is encrypted in transit and at rest
- Personal information is handled according to HIPAA guidelines
- Users can request data deletion at any time
- Conversation history is automatically purged after retention period

## Rate Limiting

- Maximum 60 messages per minute per user
- Maximum 10 concurrent conversations per user
- Automatic throttling for rapid successive requests

## Authentication

All endpoints require JWT authentication:
- Include token in WebSocket connection query parameter
- Include `Authorization: Bearer <token>` header for REST endpoints
- Tokens expire after 24 hours and must be refreshed

## Example Usage

### JavaScript WebSocket Client

```javascript
const token = localStorage.getItem('tta_access_token');
const ws = new WebSocket(`ws://localhost:8000/ws/conversational-character-creation?token=${token}`);

ws.onopen = () => {
  // Start conversation
  ws.send(JSON.stringify({
    type: 'start_conversation',
    player_id: 'user123',
    metadata: { source: 'web_ui' }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'assistant_message':
      displayMessage(message.content);
      break;
    case 'progress_update':
      updateProgress(message.progress);
      break;
    case 'crisis_detected':
      handleCrisis(message);
      break;
  }
};

// Send user response
function sendResponse(content) {
  ws.send(JSON.stringify({
    type: 'user_response',
    conversation_id: currentConversationId,
    content: content,
    timestamp: new Date().toISOString()
  }));
}
```

## Testing

### WebSocket Testing

Use tools like `wscat` for testing WebSocket connections:

```bash
wscat -c "ws://localhost:8000/ws/conversational-character-creation?token=<jwt_token>"
```

### REST API Testing

Use curl for testing REST endpoints:

```bash
curl -X GET "http://localhost:8000/api/conversations/conv123/state" \
  -H "Authorization: Bearer <jwt_token>"
```
