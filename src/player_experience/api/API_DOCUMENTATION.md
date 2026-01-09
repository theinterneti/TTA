# TTA Player Experience API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8080/api/v1`
**Authentication:** Bearer Token (JWT)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Examples](#requestresponse-examples)
5. [Error Handling](#error-handling)
6. [Validation Rules](#validation-rules)
7. [Rate Limiting](#rate-limiting)

---

## Overview

The TTA Player Experience API provides endpoints for managing players, characters, worlds, sessions, and therapeutic interactions. All endpoints (except authentication) require a valid JWT token.

### Key Features:
- **RESTful Design** - Standard HTTP methods and status codes
- **JWT Authentication** - Secure token-based authentication
- **Comprehensive Validation** - Request validation with detailed error messages
- **OpenAPI Documentation** - Interactive API docs at `/docs`
- **CORS Support** - Configured for frontend integration

---

## Authentication

### Endpoints

#### POST `/api/v1/auth/login`
Authenticate a user and receive access/refresh tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `422 Unprocessable Entity` - Invalid request format

#### POST `/api/v1/auth/refresh`
Refresh an expired access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## API Endpoints

### Characters

#### GET `/api/v1/characters`
List all characters owned by the authenticated player.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "character_id": "char_123",
    "player_id": "player_456",
    "name": "Aria Moonwhisper",
    "appearance": {
      "age_range": "adult",
      "gender_identity": "non-binary",
      "physical_description": "Tall with silver hair",
      "clothing_style": "casual",
      "distinctive_features": ["silver eyes"],
      "avatar_image_url": null
    },
    "background": {
      "name": "Aria Moonwhisper",
      "backstory": "A journey of self-discovery...",
      "personality_traits": ["brave", "compassionate"],
      "core_values": ["honesty", "kindness"],
      "fears_and_anxieties": ["abandonment"],
      "strengths_and_skills": ["empathy"],
      "life_goals": ["find inner peace"],
      "relationships": []
    },
    "therapeutic_profile": {
      "primary_concerns": ["anxiety"],
      "therapeutic_goals": [
        {
          "goal_id": "goal_789",
          "description": "Manage anxiety",
          "target_date": "2025-12-31",
          "progress_percentage": 0,
          "is_active": true,
          "therapeutic_approaches": ["CBT"]
        }
      ],
      "preferred_intensity": "moderate",
      "comfort_zones": ["safe_exploration"],
      "readiness_level": "ready",
      "therapeutic_approaches": ["CBT", "mindfulness"]
    },
    "created_at": "2025-09-29T12:00:00Z",
    "last_active": "2025-09-29T12:00:00Z",
    "is_active": true
  }
]
```

#### POST `/api/v1/characters`
Create a new character for the authenticated player.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Aria Moonwhisper",
  "appearance": {
    "age_range": "adult",
    "gender_identity": "non-binary",
    "physical_description": "Tall with silver hair",
    "clothing_style": "casual",
    "distinctive_features": ["silver eyes"],
    "avatar_image_url": null
  },
  "background": {
    "name": "Aria Moonwhisper",
    "backstory": "A journey of self-discovery through magical realms...",
    "personality_traits": ["brave", "compassionate", "curious"],
    "core_values": ["honesty", "kindness"],
    "fears_and_anxieties": ["abandonment"],
    "strengths_and_skills": ["empathy", "problem-solving"],
    "life_goals": ["find inner peace"],
    "relationships": []
  },
  "therapeutic_profile": {
    "primary_concerns": ["anxiety", "self-esteem"],
    "therapeutic_goals": [
      {
        "description": "Manage anxiety in social situations",
        "target_date": "2025-12-31",
        "therapeutic_approaches": ["CBT", "exposure therapy"]
      }
    ],
    "preferred_intensity": "moderate",
    "comfort_zones": ["safe_exploration", "gradual_challenge"],
    "readiness_level": "ready",
    "therapeutic_approaches": ["CBT", "mindfulness"]
  }
}
```

**Response (201 Created):**
```json
{
  "character_id": "char_123",
  "player_id": "player_456",
  "name": "Aria Moonwhisper",
  ...
}
```

**Validation Rules:**
- `name`: 2-50 characters, letters/spaces/hyphens/apostrophes only
- `age_range`: Must be one of: child, teen, adult, elder
- `physical_description`: 1-1000 characters
- `backstory`: 10-5000 characters
- `personality_traits`: 1-10 traits, each 2-50 characters
- `primary_concerns`: At least 1 concern
- `therapeutic_goals`: At least 1 goal with description

**Errors:**
- `400 Bad Request` - Character limit exceeded or validation error
- `401 Unauthorized` - Invalid or missing token
- `422 Unprocessable Entity` - Invalid request format

#### GET `/api/v1/characters/{character_id}`
Get a specific character by ID (owner-only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "character_id": "char_123",
  "player_id": "player_456",
  "name": "Aria Moonwhisper",
  ...
}
```

**Errors:**
- `403 Forbidden` - Not the character owner
- `404 Not Found` - Character doesn't exist

#### PUT `/api/v1/characters/{character_id}`
Update a character (owner-only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "appearance": { ... },
  "background": { ... },
  "therapeutic_profile": { ... }
}
```

**Response (200 OK):**
```json
{
  "character_id": "char_123",
  ...
}
```

#### DELETE `/api/v1/characters/{character_id}`
Delete a character (owner-only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

### Players

#### POST `/api/v1/players`
Create a new player profile.

**Request Body:**
```json
{
  "username": "player123",
  "email": "player@example.com",
  "password": "SecurePass123!",
  "therapeutic_preferences": {
    "preferred_approaches": ["CBT", "mindfulness"],
    "intensity_preference": "moderate",
    "session_duration_preference": 30
  },
  "privacy_settings": {
    "data_sharing_consent": true,
    "analytics_consent": true
  }
}
```

**Validation Rules:**
- `username`: 3-50 characters, alphanumeric/underscore/hyphen only
- `email`: Valid email format
- `password`: Minimum 8 characters

**Response (201 Created):**
```json
{
  "player_id": "player_456",
  "username": "player123",
  "email": "player@example.com",
  ...
}
```

#### GET `/api/v1/players/{player_id}`
Get player profile (owner-only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "player_id": "player_456",
  "username": "player123",
  "email": "player@example.com",
  ...
}
```

---

### Worlds

#### GET `/api/v1/worlds`
List available therapeutic worlds.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `character_id` (optional): Filter worlds compatible with character
- `limit` (optional, default: 20): Number of results
- `offset` (optional, default: 0): Pagination offset

**Response (200 OK):**
```json
[
  {
    "world_id": "world_mindfulness_garden",
    "name": "Mindfulness Garden",
    "description": "A peaceful garden for practicing mindfulness",
    "therapeutic_themes": ["anxiety", "stress"],
    "therapeutic_approaches": ["mindfulness", "relaxation"],
    "difficulty_level": "BEGINNER",
    "estimated_duration_minutes": 30
  }
]
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong",
  "error": "Error type (optional)",
  "message": "User-friendly message (optional)"
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## Validation Rules

### Character Name
- Length: 2-50 characters
- Allowed: Letters, spaces, hyphens, apostrophes
- Pattern: `^[a-zA-Z\s\-']+$`

### Username
- Length: 3-50 characters
- Allowed: Letters, numbers, underscores, hyphens
- Pattern: `^[a-zA-Z0-9_-]+$`

### Email
- Must be valid email format
- Pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

### Password
- Minimum length: 8 characters
- Recommended: Mix of uppercase, lowercase, numbers, symbols

---

## Rate Limiting

Rate limits are applied per IP address:
- **Default**: 100 requests per minute
- **Authentication**: 10 requests per minute
- **Character Creation**: 5 requests per minute

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response with a `Retry-After` header.

---

## Interactive Documentation

For interactive API exploration, visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

---

**Last Updated:** 2025-09-29
**API Version:** 1.0.0


---
**Logseq:** [[TTA.dev/Player_experience/Api/Api_documentation]]
