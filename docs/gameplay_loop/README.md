# Complete Gameplay Loop Implementation

## Overview

This document provides comprehensive documentation for the complete gameplay loop implementation in the Therapeutic Text Adventure (TTA) system. The implementation enables seamless player experiences from character creation through active story participation with therapeutic integration.

## Architecture Overview

The gameplay loop consists of several interconnected components:

### Core Components

1. **Story Initialization Service** - Manages the transition from character creation to active storytelling
2. **Therapeutic World Selection Service** - Selects optimal worlds based on therapeutic goals
3. **Gameplay Chat Manager** - Handles real-time WebSocket communication
4. **Narrative Generation Service** - Generates contextual story content
5. **Dynamic Story Generation Service** - Processes player messages into story responses
6. **Agent Orchestration WebSocket Bridge** - Integrates agent proxies with real-time messaging
7. **Agent Proxy Chat Integration** - Provides seamless narrative delivery

### Multiverse Framework

8. **Concurrent World State Manager** - Manages multiple story instances
9. **Story Branching Service** - Creates and manages narrative branches
10. **Cross-Story Character Persistence** - Maintains character continuity across stories
11. **Multiverse Navigation Service** - Enables navigation between story experiences

### Safety and Integration

12. **Therapeutic Safety Integration** - Monitors and ensures player wellbeing

## Key Features

### Real-Time Gameplay
- WebSocket-based real-time communication
- Instant story responses to player actions
- Live therapeutic monitoring and intervention

### Multiverse Support
- Multiple concurrent story experiences
- Story branching with isolated narrative contexts
- Character persistence across different stories
- Seamless navigation between story worlds

### Therapeutic Integration
- Continuous therapeutic goal tracking
- Crisis detection and intervention
- Adaptive story content based on therapeutic needs
- Safety monitoring across all interactions

### Agent Orchestration
- Integration with existing agent proxies (IPA, WBA, NGA)
- Dynamic agent workflow execution
- Contextual agent responses in real-time

## Component Details

### Story Initialization Service

**Purpose**: Manages the transition from character creation completion to active storytelling.

**Key Methods**:
- `initialize_story_session()` - Creates new story session
- `generate_opening_narrative()` - Creates initial story content
- `setup_therapeutic_context()` - Establishes therapeutic framework

**Integration Points**:
- Character creation system
- World selection service
- Narrative generation service

### Therapeutic World Selection Service

**Purpose**: Selects optimal therapeutic worlds based on player goals and character data.

**Key Methods**:
- `select_optimal_world()` - Chooses best world for therapeutic goals
- `get_world_therapeutic_profile()` - Retrieves world's therapeutic capabilities
- `evaluate_world_compatibility()` - Assesses world-character fit

**Selection Criteria**:
- Therapeutic goal alignment
- Character personality compatibility
- Player preferences
- Therapeutic approach matching

### Gameplay Chat Manager

**Purpose**: Handles real-time WebSocket communication for gameplay interactions.

**Key Features**:
- Connection management
- Message broadcasting
- Session isolation
- Error handling and recovery

**Message Types**:
- Player input messages
- Narrative response messages
- Choice request messages
- Therapeutic intervention messages
- System status messages

### Dynamic Story Generation Service

**Purpose**: Translates player messages into contextual story responses.

**Key Capabilities**:
- Message intent analysis
- Emotional tone detection
- Therapeutic indicator identification
- Response complexity determination
- Multi-agent orchestration

**Response Types**:
- Simple narrative continuations
- Moderate complexity responses
- Complex responses with choices
- Therapeutic interventions

### Multiverse Framework

**Concurrent World State Manager**:
- Manages multiple world instances per player
- Provides state isolation between stories
- Handles world instance lifecycle
- Maintains multiverse context

**Story Branching Service**:
- Creates branch points for story divergence
- Manages isolated narrative contexts
- Handles branch merging
- Maintains narrative coherence

**Cross-Story Character Persistence**:
- Tracks character evolution across stories
- Maintains therapeutic progress continuity
- Handles character data transfer
- Preserves learned skills and insights

**Multiverse Navigation Service**:
- Discovers available story destinations
- Handles navigation between stories
- Manages transition effects
- Creates therapeutic return points

## API Documentation

### WebSocket Endpoints

#### `/ws/gameplay/{player_id}/{session_id}`
Real-time gameplay WebSocket connection.

**Connection Flow**:
1. Client connects with player_id and session_id
2. Server registers connection
3. Client sends player input messages
4. Server responds with narrative content
5. Connection maintained for session duration

**Message Formats**:

```json
// Player Input
{
  "type": "player_input",
  "content": {
    "text": "I want to explore the garden",
    "input_type": "narrative_action"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}

// Narrative Response
{
  "type": "narrative_response",
  "session_id": "session_123",
  "content": {
    "text": "You step into the peaceful garden...",
    "scene_updates": {"location": "garden_entrance"},
    "therapeutic_elements": {"mindfulness_cue": "Notice the sounds"}
  },
  "timestamp": "2024-01-01T12:00:01Z"
}
```

### REST Endpoints

#### Story Initialization
- `POST /api/story/initialize` - Initialize new story session
- `GET /api/story/session/{session_id}` - Get session details
- `PUT /api/story/session/{session_id}` - Update session configuration

#### World Selection
- `GET /api/worlds/therapeutic` - List therapeutic worlds
- `POST /api/worlds/select` - Select optimal world
- `GET /api/worlds/{world_id}/profile` - Get world therapeutic profile

#### Multiverse Management
- `GET /api/multiverse/{player_id}/destinations` - List available destinations
- `POST /api/multiverse/navigate` - Navigate to destination
- `POST /api/multiverse/return-point` - Create therapeutic return point
- `GET /api/multiverse/{player_id}/history` - Get navigation history

#### Character Persistence
- `GET /api/character/{character_id}/profile` - Get character profile
- `POST /api/character/{character_id}/snapshot` - Create character snapshot
- `GET /api/character/{character_id}/journey` - Get therapeutic journey
- `POST /api/character/transfer` - Transfer character to new story

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Agent Orchestration
AGENT_ORCHESTRATION_ENABLED=true
AGENT_ORCHESTRATION_TIMEOUT=30

# Safety Integration
THERAPEUTIC_SAFETY_ENABLED=true
CRISIS_DETECTION_SENSITIVITY=0.8
AUTO_INTERVENTION_ENABLED=true

# Multiverse Configuration
MAX_CONCURRENT_INSTANCES_PER_PLAYER=5
MAX_BRANCHES_PER_PLAYER=10
INSTANCE_EXPIRY_DAYS=30

# WebSocket Configuration
WEBSOCKET_HEARTBEAT_INTERVAL=30
WEBSOCKET_TIMEOUT_SECONDS=300
MAX_CONNECTIONS_PER_SESSION=5
```

### Service Configuration

```yaml
# config/gameplay_loop.yaml
story_initialization:
  enable_auto_detection: true
  opening_narrative_length: "moderate"
  therapeutic_integration: "seamless"

world_selection:
  selection_algorithm: "therapeutic_compatibility"
  fallback_world: "therapeutic_garden"
  compatibility_threshold: 0.7

chat_management:
  message_queue_size: 1000
  broadcast_timeout_seconds: 5
  connection_cleanup_interval: 300

narrative_generation:
  response_timeout_seconds: 10
  max_response_length: 2000
  enable_therapeutic_filtering: true

multiverse:
  enable_branching: true
  enable_navigation: true
  enable_character_persistence: true
  coherence_level: "moderate"

safety:
  enable_crisis_detection: true
  enable_emotional_monitoring: true
  enable_narrative_safety: true
  human_review_threshold: "high"
```

## Deployment Guide

### Prerequisites

1. **Infrastructure Requirements**:
   - Redis server (for session management and caching)
   - Neo4j database (for world and character data)
   - Python 3.9+ environment
   - WebSocket-capable load balancer

2. **Dependencies**:
   ```bash
   pip install fastapi uvicorn websockets redis neo4j asyncio pydantic
   ```

### Deployment Steps

1. **Environment Setup**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd TTA

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   # Start Redis
   redis-server

   # Start Neo4j
   neo4j start

   # Run database migrations
   python scripts/setup_database.py
   ```

3. **Configuration**:
   ```bash
   # Copy configuration template
   cp config/gameplay_loop.yaml.template config/gameplay_loop.yaml

   # Edit configuration
   nano config/gameplay_loop.yaml

   # Set environment variables
   export REDIS_HOST=localhost
   export NEO4J_URI=bolt://localhost:7687
   # ... other variables
   ```

4. **Service Startup**:
   ```bash
   # Start the application
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

   # Or use the startup script
   ./scripts/start_gameplay_services.sh
   ```

### Production Deployment

1. **Docker Deployment**:
   ```dockerfile
   # Dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY src/ ./src/
   COPY config/ ./config/

   EXPOSE 8000
   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     tta-gameplay:
       build: .
       ports:
         - "8000:8000"
       environment:
         - REDIS_HOST=redis
         - NEO4J_URI=bolt://neo4j:7687
       depends_on:
         - redis
         - neo4j

     redis:
       image: redis:alpine
       ports:
         - "6379:6379"

     neo4j:
       image: neo4j:latest
       ports:
         - "7474:7474"
         - "7687:7687"
       environment:
         - NEO4J_AUTH=neo4j/password
   ```

2. **Kubernetes Deployment**:
   ```yaml
   # k8s/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: tta-gameplay
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: tta-gameplay
     template:
       metadata:
         labels:
           app: tta-gameplay
       spec:
         containers:
         - name: tta-gameplay
           image: tta-gameplay:latest
           ports:
           - containerPort: 8000
           env:
           - name: REDIS_HOST
             value: "redis-service"
           - name: NEO4J_URI
             value: "bolt://neo4j-service:7687"
   ```

### Monitoring and Maintenance

1. **Health Checks**:
   - `/health` - Basic health check
   - `/health/detailed` - Detailed component health
   - `/metrics` - Prometheus metrics

2. **Logging**:
   - Structured JSON logging
   - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Log rotation and retention policies

3. **Monitoring Metrics**:
   - WebSocket connection count
   - Message processing latency
   - Story generation success rate
   - Therapeutic intervention frequency
   - Multiverse navigation usage

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/player_experience/test_complete_gameplay_flow.py
pytest tests/player_experience/test_chat_and_websocket_integration.py
pytest tests/player_experience/test_multiverse_and_branching.py

# Run with coverage
pytest --cov=src tests/

# Run performance tests
pytest -m performance tests/
```

### Test Categories

1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Component interaction testing
3. **End-to-End Tests** - Complete workflow testing
4. **Performance Tests** - Load and stress testing
5. **Safety Tests** - Therapeutic safety validation

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failures**:
   - Check network connectivity
   - Verify WebSocket endpoint configuration
   - Review firewall settings

2. **Story Generation Delays**:
   - Monitor agent proxy response times
   - Check Redis connection health
   - Review narrative generation timeouts

3. **Multiverse Navigation Issues**:
   - Verify world instance states
   - Check character persistence data
   - Review navigation permissions

4. **Therapeutic Safety Alerts**:
   - Review safety configuration
   - Check crisis detection sensitivity
   - Verify intervention strategies

### Debug Mode

Enable debug mode for detailed logging:

```bash
export LOG_LEVEL=DEBUG
export ENABLE_DEBUG_ENDPOINTS=true
```

Debug endpoints:
- `/debug/connections` - Active WebSocket connections
- `/debug/sessions` - Active gameplay sessions
- `/debug/multiverse/{player_id}` - Player multiverse state
- `/debug/safety/alerts` - Active safety alerts

## Support and Maintenance

### Regular Maintenance Tasks

1. **Database Cleanup**:
   - Archive old sessions
   - Clean up expired world instances
   - Optimize character snapshot storage

2. **Performance Optimization**:
   - Monitor response times
   - Optimize database queries
   - Review caching strategies

3. **Safety Review**:
   - Review therapeutic interventions
   - Update crisis detection patterns
   - Validate safety protocols

### Getting Help

- Documentation: `/docs/`
- API Reference: `/docs/api`
- Health Status: `/health`
- Metrics: `/metrics`

For technical support, contact the development team with:
- Error logs
- System configuration
- Reproduction steps
- Expected vs actual behavior
