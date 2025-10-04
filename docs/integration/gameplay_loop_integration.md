# Core Gameplay Loop Integration

This document describes the integration of the Core Gameplay Loop system with the existing TTA (Therapeutic Text Adventure) infrastructure.

## Overview

The Core Gameplay Loop integration provides a complete therapeutic text adventure experience by connecting the gameplay system with TTA's authentication, safety validation, and agent orchestration systems.

## Architecture

### Components

1. **GameplayLoopComponent** - TTA component wrapper for the gameplay system
2. **GameplayLoopIntegration** - Integration layer connecting gameplay with TTA systems
3. **GameplayService** - Service layer for API endpoints
4. **Gameplay API Router** - REST API endpoints for frontend clients

### Integration Flow

```
Frontend Client
    ↓ (HTTP/WebSocket)
Gameplay API Router
    ↓ (Service Layer)
GameplayService
    ↓ (Integration Layer)
GameplayLoopIntegration
    ↓ (Component Layer)
GameplayLoopComponent
    ↓ (Core System)
GameplayLoopController
```

## Configuration

The gameplay loop integration is configured through the main TTA configuration file:

```yaml
core_gameplay_loop:
  enabled: true
  max_concurrent_sessions: 100
  session_timeout_minutes: 30
  enable_performance_tracking: true
  
  narrative_engine:
    complexity_adaptation: true
    immersion_tracking: true
    max_description_length: 2000
    min_description_length: 100
  
  choice_architecture:
    min_choices: 2
    max_choices: 5
    therapeutic_weighting: 0.4
  
  consequence_system:
    learning_emphasis: true
    pattern_tracking: true
    therapeutic_framing: true
  
  session_manager:
    auto_save_interval: 60
    context_preservation: true
    therapeutic_goal_tracking: true
```

## API Endpoints

### Session Management

#### Create Session
```http
POST /api/v1/gameplay/sessions
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "therapeutic_context": {
    "goals": ["anxiety_management", "social_skills"]
  }
}
```

#### Get Session Status
```http
GET /api/v1/gameplay/sessions/{session_id}
Authorization: Bearer <jwt_token>
```

#### End Session
```http
DELETE /api/v1/gameplay/sessions/{session_id}
Authorization: Bearer <jwt_token>
```

### Choice Processing

#### Process User Choice
```http
POST /api/v1/gameplay/sessions/{session_id}/choices
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "choice_id": "choice-123"
}
```

### User Management

#### Get User Sessions
```http
GET /api/v1/gameplay/sessions
Authorization: Bearer <jwt_token>
```

### Health Check

#### System Health
```http
GET /api/v1/gameplay/health
```

## Integration Features

### Authentication Integration

- **JWT Token Validation**: All gameplay endpoints require valid JWT authentication
- **User Session Ownership**: Users can only access their own gameplay sessions
- **Role-Based Access**: Future support for different user roles and permissions

### Safety Validation Integration

- **Content Validation**: All generated narrative content is validated for therapeutic safety
- **Risk Level Assessment**: High-risk content is automatically modified or blocked
- **Alternative Content Generation**: Safe alternatives are provided for flagged content
- **Crisis Detection**: Integration with TTA's crisis detection and intervention systems

### Agent Orchestration Integration

- **Multi-Agent Coordination**: Gameplay events can trigger agent workflows
- **Therapeutic Analysis**: AI agents can analyze gameplay patterns for therapeutic insights
- **Dynamic Content Generation**: Agents can contribute to narrative generation and choice creation
- **Progress Tracking**: Integration with therapeutic progress monitoring systems

## Database Integration

### Neo4j Integration

The gameplay loop uses Neo4j for storing:
- **Narrative Graphs**: Story structures and branching paths
- **Character Relationships**: Dynamic character interactions and development
- **Therapeutic Progress**: User progress and therapeutic outcomes
- **Session History**: Complete gameplay session records

### Redis Integration

Redis is used for:
- **Session State Caching**: Fast access to active session data
- **Performance Optimization**: Caching frequently accessed data
- **Real-time Updates**: Supporting real-time gameplay features

## Error Handling

### Error Codes

- `AUTH_ERROR`: Authentication or authorization failure
- `SESSION_NOT_FOUND`: Requested session does not exist
- `ACCESS_DENIED`: User does not have access to the requested resource
- `SAFETY_ERROR`: Content failed safety validation
- `SESSION_ERROR`: General session management error
- `CHOICE_ERROR`: Choice processing error
- `INTERNAL_ERROR`: Internal system error

### Error Response Format

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": {
    "additional": "context"
  }
}
```

## Performance Considerations

### Response Time Targets

- **Choice Processing**: < 2 seconds
- **Session Creation**: < 1 second
- **Status Queries**: < 500ms
- **Health Checks**: < 100ms

### Scalability

- **Concurrent Sessions**: Supports up to 100 concurrent sessions by default
- **Horizontal Scaling**: Components can be scaled independently
- **Database Optimization**: Proper indexing and query optimization
- **Caching Strategy**: Multi-level caching for optimal performance

## Testing

### Integration Tests

Run the integration tests to validate the complete system:

```bash
pytest tests/integration/test_gameplay_loop_integration.py -v
pytest tests/integration/test_gameplay_api.py -v
```

### Manual Testing

Use the provided startup script to test the integration:

```bash
python scripts/start_with_gameplay.py
```

## Deployment

### Prerequisites

1. **Neo4j Database**: Running and accessible
2. **Redis Cache**: Running and accessible
3. **TTA Configuration**: Properly configured with gameplay loop settings
4. **Dependencies**: All required Python packages installed

### Startup Sequence

1. Start Neo4j and Redis
2. Initialize TTA configuration
3. Start core infrastructure components
4. Start gameplay loop component
5. Start player experience API
6. Verify integration health

### Health Monitoring

Monitor the integration using:

- **Health Check Endpoint**: `/api/v1/gameplay/health`
- **Component Status**: TTA orchestrator status commands
- **Database Connectivity**: Neo4j and Redis connection status
- **Performance Metrics**: Response times and session metrics

## Troubleshooting

### Common Issues

1. **Component Not Starting**
   - Check configuration settings
   - Verify database connectivity
   - Review dependency requirements

2. **Authentication Failures**
   - Verify JWT token validity
   - Check authentication service status
   - Review user permissions

3. **Performance Issues**
   - Monitor database query performance
   - Check Redis cache hit rates
   - Review concurrent session limits

4. **Safety Validation Errors**
   - Check safety service configuration
   - Review content validation rules
   - Monitor risk level thresholds

### Debugging

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger('src.components.gameplay_loop_component').setLevel(logging.DEBUG)
logging.getLogger('src.integration.gameplay_loop_integration').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **WebSocket Support**: Real-time gameplay updates
2. **Multiplayer Sessions**: Collaborative therapeutic adventures
3. **Advanced Analytics**: Detailed therapeutic progress tracking
4. **Content Personalization**: AI-driven content adaptation
5. **Mobile API**: Optimized endpoints for mobile clients

### Extension Points

The integration provides several extension points for future development:

- **Custom Therapeutic Modules**: Plugin architecture for specialized therapeutic approaches
- **Third-party Integrations**: APIs for external therapeutic tools and services
- **Advanced AI Features**: Integration with additional AI models and services
- **Reporting and Analytics**: Comprehensive therapeutic outcome reporting
