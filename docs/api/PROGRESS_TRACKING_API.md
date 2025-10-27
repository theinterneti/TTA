# Progress Tracking API Documentation

## Overview

The Progress Tracking API provides comprehensive endpoints for monitoring therapeutic progress, tracking milestones, and generating analytics for TTA (Therapeutic Text Adventure) sessions.

## Authentication

All endpoints require authentication via Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. Get Player Progress Visualization

**Endpoint:** `GET /api/v1/players/{player_id}/progress/viz`

**Description:** Retrieve visualization data for player progress over a specified time period.

**Parameters:**
- `player_id` (path, required): The ID of the player
- `days` (query, optional): Number of days to include in visualization (default: 14, range: 1-60)

**Authentication:** Required

**Response Format:**
```json
{
  "time_buckets": [
    "2025-10-27",
    "2025-10-28",
    ...
  ],
  "series": {
    "duration_minutes": [30, 45, 60, ...],
    "sessions": [1, 1, 2, ...],
    "engagement_score": [0.7, 0.8, 0.9, ...],
    "therapeutic_effectiveness": [0.6, 0.7, 0.8, ...]
  },
  "meta": {
    "total_sessions": 15,
    "total_time_minutes": 450,
    "average_session_length": 30,
    "engagement_trend": "improving"
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8080/api/v1/players/player-123/progress/viz?days=30" \
  -H "Authorization: Bearer your_access_token"
```

**Status Codes:**
- `200 OK`: Successfully retrieved visualization data
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Player not found

---

### 2. Get Session Progress

**Endpoint:** `GET /api/v1/sessions/{session_id}/progress`

**Description:** Retrieve progress information for a specific session.

**Parameters:**
- `session_id` (path, required): The ID of the session

**Authentication:** Required

**Response Format:**
```json
{
  "session_id": "session-123",
  "character_id": "char-456",
  "world_id": "world-789",
  "progress": {
    "completed_steps": 5,
    "total_steps": 10,
    "completion_percentage": 50
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8080/api/v1/sessions/session-123/progress" \
  -H "Authorization: Bearer your_access_token"
```

**Status Codes:**
- `200 OK`: Successfully retrieved session progress
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Session not found

---

### 3. Get Player Progress Summary

**Endpoint:** `GET /api/v1/players/{player_id}/progress`

**Description:** Retrieve comprehensive progress summary for a player including engagement metrics and milestones.

**Parameters:**
- `player_id` (path, required): The ID of the player

**Authentication:** Required

**Response Format:**
```json
{
  "player_id": "player-123",
  "total_sessions": 15,
  "total_time_minutes": 450,
  "milestones_achieved": 3,
  "current_streak_days": 7,
  "longest_streak_days": 14,
  "favorite_therapeutic_approach": "mindfulness",
  "most_effective_world_type": "garden",
  "last_session_date": "2025-10-27T14:30:00Z",
  "next_recommended_session": "2025-10-28T15:00:00Z"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8080/api/v1/players/player-123/progress" \
  -H "Authorization: Bearer your_access_token"
```

**Status Codes:**
- `200 OK`: Successfully retrieved progress summary
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Player not found

---

## Data Models

### EngagementMetrics
Tracks player engagement patterns and consistency:
- `total_sessions`: Total number of completed sessions
- `total_time_minutes`: Total time spent in therapeutic sessions
- `average_session_length`: Average duration per session
- `sessions_this_week`: Sessions completed in the current week
- `current_streak_days`: Current consecutive days with sessions
- `longest_streak_days`: Longest streak of consecutive session days
- `dropout_risk_score`: Risk score for session dropout (0.0-1.0)

### Milestone
Represents significant achievements:
- `milestone_id`: Unique identifier
- `milestone_type`: Type of milestone (e.g., "session_count", "skill_acquired")
- `title`: Human-readable title
- `description`: Detailed description
- `achieved_at`: Timestamp when milestone was achieved
- `therapeutic_value`: Therapeutic significance (0.0-1.0)

### TherapeuticMetric
Measures therapeutic effectiveness:
- `metric_name`: Name of the metric
- `value`: Numeric value (0.0-1.0)
- `unit`: Unit of measurement
- `measured_at`: Timestamp of measurement
- `confidence_level`: Confidence in the measurement (0.0-1.0)

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Player not found"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["query", "days"],
      "msg": "ensure this value is less than or equal to 60",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Rate Limiting

Progress tracking endpoints are subject to rate limiting:
- **Limit:** 100 requests per minute per user
- **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Best Practices

1. **Caching:** Cache visualization data for 5-10 minutes to reduce server load
2. **Pagination:** For large datasets, request data in smaller time windows
3. **Error Handling:** Implement retry logic with exponential backoff for failed requests
4. **Authentication:** Store tokens securely and refresh before expiration

---

## Examples

### Python Example
```python
import requests

headers = {"Authorization": f"Bearer {access_token}"}

# Get 30-day progress visualization
response = requests.get(
    "http://localhost:8080/api/v1/players/player-123/progress/viz?days=30",
    headers=headers
)
data = response.json()
print(f"Total sessions: {data['meta']['total_sessions']}")
```

### JavaScript Example
```javascript
const accessToken = 'your_access_token';

fetch('http://localhost:8080/api/v1/players/player-123/progress/viz?days=30', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})
.then(response => response.json())
.then(data => console.log(`Total sessions: ${data.meta.total_sessions}`));
```

---

## Support

For issues or questions about the Progress Tracking API, please contact support@example.com or create an issue on GitHub.
