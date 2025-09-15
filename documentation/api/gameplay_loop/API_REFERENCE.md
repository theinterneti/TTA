# Gameplay Loop API Reference

## Overview

This document provides detailed API reference for all endpoints in the complete gameplay loop implementation.

## WebSocket API

### Gameplay WebSocket Connection

**Endpoint**: `/ws/gameplay/{player_id}/{session_id}`

**Description**: Real-time gameplay communication channel for story interactions.

**Parameters**:
- `player_id` (string): Unique player identifier
- `session_id` (string): Unique session identifier

**Connection Flow**:
1. Client establishes WebSocket connection
2. Server registers connection and sends confirmation
3. Client sends gameplay messages
4. Server processes and responds with story content
5. Connection maintained until client disconnects

### Message Types

#### Player Input Message
```json
{
  "type": "player_input",
  "content": {
    "text": "I want to explore the peaceful garden",
    "input_type": "narrative_action",
    "metadata": {
      "intent": "exploration",
      "emotional_context": "curious"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Narrative Response Message
```json
{
  "type": "narrative_response",
  "session_id": "session_123",
  "content": {
    "text": "You step into the garden, feeling the soft grass beneath your feet...",
    "scene_updates": {
      "location": "garden_entrance",
      "atmosphere": "peaceful",
      "available_actions": ["sit_by_fountain", "walk_flower_path", "find_quiet_spot"]
    },
    "therapeutic_elements": {
      "mindfulness_cue": "Notice the sounds of nature around you",
      "breathing_reminder": "Take a deep breath and feel grounded"
    }
  },
  "timestamp": "2024-01-01T12:00:01Z",
  "metadata": {
    "response_type": "narrative_continuation",
    "therapeutic_focus": ["mindfulness", "grounding"]
  }
}
```

#### Choice Request Message
```json
{
  "type": "choice_request",
  "session_id": "session_123",
  "content": {
    "prompt": "You notice several paths ahead. Which would you like to take?",
    "choices": [
      {
        "id": "choice_1",
        "text": "The winding path through the flowers",
        "therapeutic_benefit": "Encourages mindful observation"
      },
      {
        "id": "choice_2", 
        "text": "The straight path to the meditation area",
        "therapeutic_benefit": "Promotes focused intention"
      },
      {
        "id": "choice_3",
        "text": "The shaded path under the trees",
        "therapeutic_benefit": "Offers comfort and security"
      }
    ],
    "choice_context": {
      "decision_type": "path_selection",
      "therapeutic_significance": "medium"
    }
  },
  "timestamp": "2024-01-01T12:00:02Z"
}
```

#### Therapeutic Intervention Message
```json
{
  "type": "therapeutic_intervention",
  "session_id": "session_123",
  "content": {
    "intervention_type": "emotional_support",
    "message": "I notice you might be feeling overwhelmed. Let's take a moment to breathe together.",
    "resources": [
      {
        "name": "4-7-8 Breathing",
        "description": "Breathe in for 4, hold for 7, exhale for 8",
        "type": "breathing_exercise"
      }
    ],
    "severity": "medium",
    "immediate_actions": ["breathing_exercise", "grounding_technique"]
  },
  "timestamp": "2024-01-01T12:00:03Z",
  "metadata": {
    "trigger": "emotional_distress_detected",
    "auto_intervention": true
  }
}
```

## REST API

### Story Initialization

#### Initialize Story Session
**POST** `/api/story/initialize`

**Request Body**:
```json
{
  "player_id": "player_123",
  "character_id": "char_456",
  "world_id": "therapeutic_garden",
  "therapeutic_goals": ["anxiety_management", "social_skills"],
  "story_preferences": {
    "complexity": "moderate",
    "interaction_style": "collaborative",
    "therapeutic_approach": "gentle"
  }
}
```

**Response**:
```json
{
  "success": true,
  "story_session_id": "story_session_789",
  "opening_narrative": {
    "text": "Welcome to your therapeutic journey...",
    "scene_setup": {
      "location": "garden_entrance",
      "mood": "welcoming"
    }
  },
  "session_metadata": {
    "created_at": "2024-01-01T12:00:00Z",
    "therapeutic_context": {
      "primary_goals": ["anxiety_management"],
      "secondary_goals": ["social_skills"]
    }
  }
}
```

#### Get Session Details
**GET** `/api/story/session/{session_id}`

**Response**:
```json
{
  "session_id": "session_123",
  "player_id": "player_123",
  "character_id": "char_456",
  "world_id": "therapeutic_garden",
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "last_activity": "2024-01-01T12:30:00Z",
  "therapeutic_progress": {
    "goals_addressed": ["anxiety_management"],
    "skills_practiced": ["deep_breathing", "mindful_observation"],
    "progress_markers": {
      "anxiety_management": 0.3,
      "social_skills": 0.1
    }
  },
  "narrative_state": {
    "current_location": "garden_center",
    "story_progression": 0.25,
    "active_plot_threads": ["self_discovery", "healing_journey"]
  }
}
```

### World Selection

#### List Therapeutic Worlds
**GET** `/api/worlds/therapeutic`

**Query Parameters**:
- `therapeutic_goals` (array): Filter by therapeutic goals
- `complexity` (string): Filter by complexity level
- `approach` (string): Filter by therapeutic approach

**Response**:
```json
{
  "worlds": [
    {
      "world_id": "therapeutic_garden",
      "name": "Healing Garden",
      "description": "A peaceful garden environment for mindfulness and reflection",
      "therapeutic_profile": {
        "primary_goals": ["anxiety_management", "mindfulness", "grounding"],
        "secondary_goals": ["self_esteem", "emotional_regulation"],
        "approach": "nature_based_therapy",
        "complexity": "moderate"
      },
      "compatibility_score": 0.85
    }
  ],
  "total_count": 1,
  "filtered_count": 1
}
```

#### Select Optimal World
**POST** `/api/worlds/select`

**Request Body**:
```json
{
  "therapeutic_goals": ["anxiety_management", "social_skills"],
  "character_data": {
    "personality_traits": {
      "openness": 0.7,
      "neuroticism": 0.4
    },
    "preferences": {
      "environment_type": "natural",
      "interaction_style": "gentle"
    }
  },
  "player_preferences": {
    "complexity": "moderate",
    "therapeutic_approach": "mindfulness_based"
  }
}
```

**Response**:
```json
{
  "success": true,
  "selected_world": "therapeutic_garden",
  "compatibility_score": 0.92,
  "selection_reasoning": {
    "goal_alignment": 0.95,
    "personality_fit": 0.88,
    "preference_match": 0.93
  },
  "world_details": {
    "name": "Healing Garden",
    "therapeutic_focus": ["mindfulness", "anxiety_management"],
    "expected_benefits": ["stress_reduction", "emotional_regulation"]
  }
}
```

### Multiverse Management

#### List Available Destinations
**GET** `/api/multiverse/{player_id}/destinations`

**Response**:
```json
{
  "destinations": [
    {
      "destination_id": "dest_garden_001",
      "title": "Peaceful Garden Path",
      "description": "Continue your mindfulness journey in the healing garden",
      "destination_type": "world_instance",
      "world_id": "therapeutic_garden",
      "therapeutic_context": {
        "focus_areas": ["mindfulness", "grounding"],
        "progress_level": "beginner"
      },
      "accessibility": {
        "accessible": true,
        "requirements": []
      },
      "visit_history": {
        "last_visited": "2024-01-01T11:00:00Z",
        "visit_count": 3
      }
    }
  ],
  "total_destinations": 1,
  "categories": {
    "world_instances": 1,
    "story_branches": 0,
    "therapeutic_return_points": 0
  }
}
```

#### Navigate to Destination
**POST** `/api/multiverse/navigate`

**Request Body**:
```json
{
  "player_id": "player_123",
  "current_session_id": "session_123",
  "destination_id": "dest_garden_001",
  "navigation_type": "story_switch",
  "transition_type": "fade_transition",
  "preserve_context": true,
  "therapeutic_continuity": true
}
```

**Response**:
```json
{
  "success": true,
  "navigation_id": "nav_456",
  "new_session_id": "session_789",
  "transition_effect": {
    "effect": "fade_transition",
    "duration": 2.0,
    "description": "The world gently fades as you transition to a new story..."
  },
  "destination_details": {
    "title": "Peaceful Garden Path",
    "initial_narrative": "You find yourself back in the familiar garden..."
  },
  "character_transferred": true,
  "therapeutic_continuity_maintained": true
}
```

#### Create Therapeutic Return Point
**POST** `/api/multiverse/return-point`

**Request Body**:
```json
{
  "player_id": "player_123",
  "current_session_id": "session_123",
  "return_point_name": "Moment of Peace",
  "therapeutic_context": {
    "emotional_state": "calm",
    "therapeutic_breakthrough": "mindfulness_realization",
    "skills_practiced": ["deep_breathing", "present_moment_awareness"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "return_point_id": "trp_789",
  "return_point_name": "Moment of Peace",
  "created_at": "2024-01-01T12:00:00Z",
  "accessibility": {
    "always_accessible": true,
    "therapeutic_significance": "high"
  }
}
```

### Character Persistence

#### Get Character Profile
**GET** `/api/character/{character_id}/profile`

**Response**:
```json
{
  "profile_id": "csp_123",
  "character_id": "char_456",
  "player_id": "player_123",
  "base_character_data": {
    "name": "Alex",
    "personality_traits": {
      "openness": 0.7,
      "conscientiousness": 0.6
    }
  },
  "accumulated_skills": ["deep_breathing", "active_listening", "mindful_observation"],
  "personality_evolution": {
    "confidence_growth": 0.3,
    "emotional_awareness": 0.4
  },
  "therapeutic_journey": {
    "goals_achieved": ["basic_mindfulness"],
    "goals_in_progress": ["anxiety_management", "social_skills"],
    "total_sessions": 15,
    "breakthrough_moments": 3
  },
  "story_experiences": ["therapeutic_garden", "urban_environment"],
  "created_at": "2024-01-01T10:00:00Z",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

#### Create Character Snapshot
**POST** `/api/character/{character_id}/snapshot`

**Request Body**:
```json
{
  "player_id": "player_123",
  "instance_id": "instance_789",
  "character_data": {
    "therapeutic_progress": {
      "anxiety_management": 0.4,
      "social_skills": 0.2
    },
    "skills_learned": ["deep_breathing", "grounding_techniques"],
    "emotional_state": {
      "current_mood": "calm",
      "stress_level": 0.3
    }
  },
  "story_context": {
    "world_id": "therapeutic_garden",
    "significant_events": ["first_mindfulness_breakthrough"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "snapshot_id": "cs_456",
  "created_at": "2024-01-01T12:00:00Z",
  "snapshot_summary": {
    "therapeutic_progress_captured": true,
    "skills_documented": 2,
    "emotional_state_recorded": true
  }
}
```

#### Get Therapeutic Journey
**GET** `/api/character/{character_id}/journey`

**Response**:
```json
{
  "character_id": "char_456",
  "therapeutic_journey": {
    "total_duration_days": 30,
    "sessions_completed": 15,
    "goals_achieved": ["basic_mindfulness"],
    "goals_in_progress": ["anxiety_management", "social_skills"],
    "skills_mastered": ["deep_breathing"],
    "skills_practicing": ["grounding_techniques", "active_listening"]
  },
  "journey_timeline": [
    {
      "date": "2024-01-01",
      "event_type": "skill_learned",
      "description": "Mastered deep breathing technique",
      "therapeutic_significance": "high"
    }
  ],
  "progress_summary": {
    "overall_progress": 0.35,
    "anxiety_management": 0.4,
    "social_skills": 0.2,
    "emotional_regulation": 0.3
  },
  "insights_gained": [
    "Mindfulness helps reduce anxiety",
    "Breathing techniques are effective for stress"
  ]
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "therapeutic_goals",
      "issue": "At least one therapeutic goal is required"
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_123"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR` (400): Invalid request parameters
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `CONFLICT` (409): Resource conflict
- `RATE_LIMITED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error
- `SERVICE_UNAVAILABLE` (503): Service temporarily unavailable

## Rate Limiting

### Limits
- WebSocket connections: 5 per player
- API requests: 100 per minute per player
- Story generation: 10 per minute per session
- Navigation requests: 5 per minute per player

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Authentication

### WebSocket Authentication
WebSocket connections are authenticated via query parameters:
```
/ws/gameplay/{player_id}/{session_id}?token={auth_token}
```

### REST API Authentication
REST API uses Bearer token authentication:
```
Authorization: Bearer {auth_token}
```

## Pagination

### Request Parameters
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `sort` (string): Sort field
- `order` (string): Sort order ("asc" or "desc")

### Response Format
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

## Webhooks

### Therapeutic Alert Webhook
**POST** `{configured_webhook_url}`

**Payload**:
```json
{
  "event_type": "therapeutic_alert",
  "alert_id": "alert_123",
  "player_id": "player_123",
  "session_id": "session_123",
  "alert_level": "high",
  "trigger_type": "emotional_distress",
  "timestamp": "2024-01-01T12:00:00Z",
  "requires_human_review": true,
  "recommended_actions": ["provide_emotional_support", "offer_coping_strategies"]
}
```

### Story Completion Webhook
**POST** `{configured_webhook_url}`

**Payload**:
```json
{
  "event_type": "story_completion",
  "player_id": "player_123",
  "session_id": "session_123",
  "world_id": "therapeutic_garden",
  "completion_type": "therapeutic_goal_achieved",
  "therapeutic_outcomes": {
    "goals_achieved": ["anxiety_management"],
    "skills_learned": ["deep_breathing", "mindfulness"],
    "progress_made": 0.4
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```
