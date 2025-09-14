# TTA API Quick Reference

This document provides a quick reference for the most commonly used APIs in the TTA therapeutic gaming system.

## 🔐 Authentication APIs

### Login
```typescript
POST /api/auth/login
Content-Type: application/json

{
  "email": "patient@example.com",
  "password": "securePassword"
}

Response: {
  "success": true,
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "patient@example.com",
      "role": "patient",
      "profile": {
        "firstName": "John",
        "lastName": "Doe",
        "therapeuticGoals": ["anxiety-management", "social-skills"]
      }
    },
    "token": "jwt-token-here",
    "refreshToken": "refresh-token-here"
  }
}
```

### Register
```typescript
POST /api/auth/register
Content-Type: application/json

{
  "email": "newpatient@example.com",
  "password": "securePassword",
  "profile": {
    "firstName": "Jane",
    "lastName": "Smith",
    "dateOfBirth": "1990-01-01",
    "therapeuticGoals": ["depression-support"]
  }
}
```

### Logout
```typescript
POST /api/auth/logout
Authorization: Bearer {jwt-token}
```

## 👤 Character Management APIs

### Get Available Characters
```typescript
GET /api/characters/available
Authorization: Bearer {jwt-token}

Response: {
  "success": true,
  "data": [
    {
      "id": "char-uuid",
      "name": "Alex the Explorer",
      "description": "A curious adventurer who helps with confidence building",
      "archetype": "Explorer",
      "traits": ["Curious", "Brave", "Empathetic"],
      "therapeuticFocus": ["confidence-building", "exploration"]
    }
  ]
}
```

### Create Custom Character
```typescript
POST /api/characters
Authorization: Bearer {jwt-token}
Content-Type: application/json

{
  "name": "My Therapeutic Companion",
  "description": "A personalized character for my journey",
  "archetype": "Companion",
  "traits": ["Patient", "Understanding", "Encouraging"],
  "therapeuticGoals": ["anxiety-management"]
}
```

### Get Character Details
```typescript
GET /api/characters/{characterId}
Authorization: Bearer {jwt-token}

Response: {
  "success": true,
  "data": {
    "id": "char-uuid",
    "name": "Alex the Explorer",
    "description": "...",
    "currentState": {
      "mood": "encouraging",
      "energy": 85,
      "relationship": "trusted-friend"
    },
    "conversationHistory": [...]
  }
}
```

## 🌍 World Management APIs

### Get Available Worlds
```typescript
GET /api/worlds/available
Authorization: Bearer {jwt-token}

Response: {
  "success": true,
  "data": [
    {
      "id": "world-uuid",
      "name": "Peaceful Garden",
      "description": "A serene environment for relaxation",
      "theme": "Nature",
      "difficulty": "beginner",
      "therapeuticFocus": ["anxiety-reduction", "mindfulness"],
      "isAvailable": true
    }
  ]
}
```

### Enter World
```typescript
POST /api/worlds/{worldId}/enter
Authorization: Bearer {jwt-token}
Content-Type: application/json

{
  "characterId": "char-uuid",
  "sessionGoals": ["practice-mindfulness", "reduce-anxiety"]
}

Response: {
  "success": true,
  "data": {
    "sessionId": "session-uuid",
    "worldState": {
      "currentLocation": "garden-entrance",
      "availableActions": ["explore", "meditate", "talk-to-character"],
      "environmentMood": "calm"
    }
  }
}
```

## 🎮 Session Management APIs

### Start Therapeutic Session
```typescript
POST /api/sessions/start
Authorization: Bearer {jwt-token}
Content-Type: application/json

{
  "worldId": "world-uuid",
  "characterId": "char-uuid",
  "sessionType": "guided-exploration",
  "goals": ["anxiety-management", "confidence-building"],
  "duration": 30
}

Response: {
  "success": true,
  "data": {
    "sessionId": "session-uuid",
    "startTime": "2024-09-13T10:00:00Z",
    "estimatedEndTime": "2024-09-13T10:30:00Z",
    "initialState": {
      "worldState": {...},
      "characterState": {...}
    }
  }
}
```

### Update Session Progress
```typescript
PUT /api/sessions/{sessionId}/progress
Authorization: Bearer {jwt-token}
Content-Type: application/json

{
  "actions": [
    {
      "type": "character-interaction",
      "timestamp": "2024-09-13T10:05:00Z",
      "data": {
        "message": "I'm feeling anxious about the upcoming challenge",
        "characterResponse": "That's completely normal. Let's take a deep breath together."
      }
    }
  ],
  "currentMood": "slightly-anxious",
  "progressMetrics": {
    "anxietyLevel": 6,
    "engagementLevel": 8,
    "therapeuticGoalProgress": {
      "anxiety-management": 0.3
    }
  }
}
```

### End Session
```typescript
POST /api/sessions/{sessionId}/end
Authorization: Bearer {jwt-token}
Content-Type: application/json

{
  "endReason": "completed",
  "finalMood": "calm",
  "sessionSummary": "Successfully practiced mindfulness techniques",
  "achievements": ["first-meditation", "anxiety-reduction"]
}
```

## 📊 Progress Tracking APIs

### Get User Progress
```typescript
GET /api/progress/overview
Authorization: Bearer {jwt-token}

Response: {
  "success": true,
  "data": {
    "overallProgress": {
      "totalSessions": 15,
      "totalTime": 450, // minutes
      "currentStreak": 5,
      "longestStreak": 12
    },
    "therapeuticGoals": {
      "anxiety-management": {
        "progress": 0.65,
        "milestones": ["first-session", "week-streak", "anxiety-reduction"],
        "nextMilestone": "month-streak"
      }
    },
    "achievements": [
      {
        "id": "first-week",
        "name": "First Week Complete",
        "description": "Completed your first week of therapeutic gaming",
        "unlockedAt": "2024-09-06T10:00:00Z"
      }
    ]
  }
}
```

### Get Session History
```typescript
GET /api/progress/sessions?limit=10&offset=0
Authorization: Bearer {jwt-token}

Response: {
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "session-uuid",
        "startTime": "2024-09-13T10:00:00Z",
        "endTime": "2024-09-13T10:30:00Z",
        "worldName": "Peaceful Garden",
        "characterName": "Alex the Explorer",
        "goals": ["anxiety-management"],
        "outcomes": {
          "moodImprovement": 2,
          "goalProgress": 0.1,
          "achievements": ["mindfulness-practice"]
        }
      }
    ],
    "pagination": {
      "total": 15,
      "limit": 10,
      "offset": 0
    }
  }
}
```

## 🚨 Crisis Support APIs

### Check Crisis Status
```typescript
GET /api/crisis/status
Authorization: Bearer {jwt-token}

Response: {
  "success": true,
  "data": {
    "riskLevel": "low", // low, medium, high, critical
    "lastAssessment": "2024-09-13T09:00:00Z",
    "supportResources": [
      {
        "type": "hotline",
        "name": "Crisis Text Line",
        "contact": "Text HOME to 741741",
        "available24x7": true
      }
    ]
  }
}
```

### Report Crisis Situation
```typescript
POST /api/crisis/report
Authorization: Bearer {jwt-token}
Content-Type: application/json

{
  "severity": "high",
  "description": "Patient expressing suicidal ideation",
  "immediateRisk": true,
  "context": {
    "sessionId": "session-uuid",
    "timestamp": "2024-09-13T10:15:00Z"
  }
}

Response: {
  "success": true,
  "data": {
    "interventionId": "intervention-uuid",
    "immediateActions": [
      "Contact emergency services",
      "Notify clinical team",
      "Provide crisis resources"
    ],
    "followUpRequired": true
  }
}
```

## 🔄 WebSocket Events

### Connection
```typescript
// Connect to WebSocket
const ws = new WebSocket('wss://api.tta.dev/ws');

// Authentication
ws.send(JSON.stringify({
  type: 'auth',
  token: 'jwt-token-here'
}));
```

### Real-time Character Interaction
```typescript
// Send message to character
ws.send(JSON.stringify({
  type: 'character-message',
  sessionId: 'session-uuid',
  characterId: 'char-uuid',
  message: 'I need help with my anxiety'
}));

// Receive character response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'character-response') {
    console.log('Character says:', data.message);
  }
};
```

### Session State Updates
```typescript
// Listen for session state changes
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'session-state-update') {
    // Update UI with new session state
    updateSessionUI(data.sessionState);
  }
};
```

### Crisis Alerts
```typescript
// Listen for crisis alerts
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'crisis-alert') {
    // Show crisis support resources immediately
    showCrisisSupport(data.resources);
  }
};
```

## 📝 Common Response Formats

### Success Response
```typescript
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully"
}
```

### Error Response
```typescript
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

### Pagination Response
```typescript
{
  "success": true,
  "data": { /* paginated data */ },
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

## 🔧 Error Codes

| Code | Description | Action |
|------|-------------|--------|
| `AUTH_REQUIRED` | Authentication required | Redirect to login |
| `AUTH_EXPIRED` | Token expired | Refresh token |
| `VALIDATION_ERROR` | Input validation failed | Show field errors |
| `RESOURCE_NOT_FOUND` | Resource doesn't exist | Show 404 message |
| `CRISIS_DETECTED` | Crisis situation detected | Show crisis support |
| `SESSION_EXPIRED` | Therapeutic session expired | End session gracefully |
| `RATE_LIMITED` | Too many requests | Show retry message |

---

For complete API documentation, see the `./api/` directory.
