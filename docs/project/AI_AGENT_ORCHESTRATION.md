# AI Agent Orchestration System

## Overview

The TTA AI Agent Orchestration System coordinates three specialized agents (IPA, WBA, NGA) to process user input and generate therapeutic narrative responses. The system integrates with LangGraph for workflow management and provides comprehensive state persistence, safety validation, and error handling.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Input                                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│           LangGraph Agent Orchestrator                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Workflow Management & Therapeutic Safety Integration    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│           Unified Agent Orchestrator                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Phase 1: Input Processing (IPA)                         │  │
│  │  Phase 2: World Building (WBA)                           │  │
│  │  Phase 3: Narrative Generation (NGA)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Agent Adapters                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │   IPA    │    │   WBA    │    │   NGA    │                  │
│  │ Adapter  │    │ Adapter  │    │ Adapter  │                  │
│  └──────────┘    └──────────┘    └──────────┘                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              State Persistence (Redis)                           │
│  • Workflow State                                                │
│  • Session History                                               │
│  • Agent Results                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **LangGraph Agent Orchestrator** (`src/agent_orchestration/langgraph_orchestrator.py`)
   - Integrates with LangGraph for workflow management
   - Provides therapeutic safety validation
   - Manages workflow state and routing

2. **Unified Agent Orchestrator** (`src/agent_orchestration/unified_orchestrator.py`)
   - Coordinates IPA → WBA → NGA workflow
   - Manages state persistence
   - Handles error recovery and fallbacks

3. **Agent Adapters** (`src/agent_orchestration/adapters.py`)
   - Bridge to real agent implementations
   - Provide retry logic and fallback to mocks
   - Transform data between orchestration and agent formats

4. **Agent Proxies** (`src/agent_orchestration/proxies.py`)
   - Add validation and safety checks
   - Publish progress events
   - Wrap adapters with additional functionality

## Agent Workflow

### Phase 1: Input Processing (IPA)

**Purpose**: Parse and understand user input

**Process**:
1. Validate input safety using therapeutic safety service
2. Process input through IPA adapter
3. Extract intent, entities, and routing information
4. Store IPA result in workflow state

**Output**:
```python
{
    "normalized_text": "explore the forest",
    "routing": {
        "intent": "explore",
        "confidence": 0.85,
        "entities": {"location": "forest"}
    },
    "raw_intent": {...},
    "source": "real_ipa" | "mock_fallback"
}
```

### Phase 2: World Building (WBA)

**Purpose**: Update world state based on user intent

**Process**:
1. Extract intent and entities from IPA result
2. Build world update request
3. Process through WBA adapter
4. Update world context with changes
5. Store WBA result in workflow state

**Output**:
```python
{
    "world_id": "session-123",
    "world_state": {
        "current_location": "forest_entrance",
        "visited_locations": ["village", "forest_entrance"],
        "discovered_items": []
    },
    "updated": True,
    "source": "real_wba" | "mock_fallback"
}
```

### Phase 3: Narrative Generation (NGA)

**Purpose**: Generate therapeutic narrative response

**Process**:
1. Build narrative prompt from workflow state
2. Prepare context (world state, intent, entities, therapeutic context)
3. Generate narrative through NGA adapter
4. Store NGA result in workflow state

**Output**:
```python
{
    "story": "You step into the forest. The trees tower above you...",
    "therapeutic_elements": ["exploration", "curiosity"],
    "emotional_tone": "encouraging",
    "source": "real_nga" | "mock_fallback"
}
```

## State Management

### Workflow State

The orchestration system maintains comprehensive state throughout the workflow:

```python
@dataclass
class OrchestrationState:
    workflow_id: str          # Unique workflow identifier
    session_id: str           # Session identifier
    player_id: str            # Player identifier
    phase: OrchestrationPhase # Current workflow phase
    user_input: str           # Original user input

    # Phase results
    ipa_result: dict | None   # IPA processing result
    wba_result: dict | None   # WBA processing result
    nga_result: dict | None   # NGA processing result

    # Context
    world_context: dict       # Current world state
    therapeutic_context: dict # Therapeutic session context
    safety_level: SafetyLevel # Safety assessment level

    # Metadata
    created_at: datetime
    updated_at: datetime
    error: str | None
```

### State Persistence

**Redis Keys**:
- `orchestration:workflow:{workflow_id}` - Complete workflow state (TTL: 1 hour)
- `orchestration:session:{session_id}:latest` - Latest workflow ID for session (TTL: 1 hour)

**Retrieval Methods**:
```python
# Get specific workflow state
state = await orchestrator.get_workflow_state(workflow_id)

# Get latest workflow for session
state = await orchestrator.get_session_latest_workflow(session_id)
```

## Safety Validation

The system integrates with the therapeutic safety service to validate user input:

**Safety Levels**:
- `SAFE` - No concerns detected
- `WARNING` - Minor concerns, continue with caution
- `BLOCKED` - Serious concerns, trigger safety intervention

**Safety Intervention**:
When `BLOCKED` or `WARNING` level is detected:
1. Workflow pauses after Phase 1 (IPA)
2. Safety intervention response is generated
3. Therapeutic support message is provided
4. Workflow completes without proceeding to WBA/NGA

## Error Handling

### Retry Logic

Agent adapters implement exponential backoff retry logic:

```python
@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0
```

### Fallback Mechanisms

1. **Agent Unavailable**: Falls back to mock implementation
2. **Communication Error**: Retries with exponential backoff
3. **Processing Error**: Returns error response with fallback narrative

### Error Response

```python
{
    "workflow_id": "abc-123",
    "success": False,
    "error": "Error description",
    "narrative": "I'm having trouble processing that. Could you try rephrasing?",
    "safety_level": "safe"
}
```

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379

# OpenAI Configuration (for LangGraph)
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Neo4j Configuration (for WBA)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Agent Configuration
ENABLE_REAL_AGENTS=true  # Use real agents vs mocks
```

### Initialization

```python
from src.agent_orchestration.langgraph_orchestrator import LangGraphAgentOrchestrator

# Create orchestrator
orchestrator = LangGraphAgentOrchestrator(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
    neo4j_manager=neo4j_manager,  # Optional
    model_name="gpt-4-turbo-preview"
)

# Initialize
await orchestrator.initialize()

# Process user input
result = await orchestrator.process_user_input(
    user_input="explore the ancient ruins",
    session_id="session-123",
    player_id="player-456",
    world_context={"current_location": "village"},
    therapeutic_context={"mood": "curious"}
)

# Cleanup
await orchestrator.close()
```

## Testing

### Unit Tests

Located in `tests/agent_orchestration/`:
- `test_unified_orchestrator.py` - Tests for unified orchestrator
- `test_langgraph_orchestrator.py` - Tests for LangGraph integration

### Running Tests

```bash
# Run all agent orchestration tests
uv run pytest tests/agent_orchestration/ -v

# Run specific test file
uv run pytest tests/agent_orchestration/test_unified_orchestrator.py -v

# Run with coverage
uv run pytest tests/agent_orchestration/ --cov=src/agent_orchestration
```

### Test Coverage

- ✅ State serialization/deserialization
- ✅ Complete workflow execution
- ✅ Individual phase processing
- ✅ Safety concern handling
- ✅ State persistence
- ✅ Error handling
- ✅ Concurrent workflows
- ✅ LangGraph workflow integration
- ✅ Routing logic
- ✅ Crisis intervention

## Integration with Existing Systems

### Player Experience API

The orchestrator integrates with the Player Experience API:

```python
from src.agent_orchestration.langgraph_orchestrator import LangGraphAgentOrchestrator

# In your API endpoint
@router.post("/process-input")
async def process_input(request: ProcessInputRequest):
    result = await orchestrator.process_user_input(
        user_input=request.text,
        session_id=request.session_id,
        player_id=request.player_id,
        world_context=await get_world_context(request.session_id),
        therapeutic_context=await get_therapeutic_context(request.session_id)
    )

    return {
        "narrative": result["narrative"],
        "workflow_id": result["workflow_id"],
        "safety_level": result["safety_level"]
    }
```

### WebSocket Real-time Updates

Progress events can be published during workflow execution:

```python
# Agent proxies publish events
await event_publisher.publish_progress(
    session_id=session_id,
    agent="IPA",
    status="processing",
    progress=0.33
)
```

## Performance Considerations

### Optimization Strategies

1. **State Caching**: Workflow state cached in Redis with 1-hour TTL
2. **Parallel Processing**: Independent operations run concurrently
3. **Connection Pooling**: Redis and Neo4j connections pooled
4. **Retry Limits**: Maximum 3 retries per agent call
5. **Timeout Management**: Configurable timeouts for each phase

### Monitoring

Key metrics to monitor:
- Workflow completion time
- Agent response times (IPA, WBA, NGA)
- Safety intervention rate
- Error rate by phase
- Fallback usage rate

## Future Enhancements

1. **Advanced Agent Coordination**: Multi-agent collaboration patterns
2. **Adaptive Workflows**: Dynamic workflow routing based on context
3. **Enhanced State Management**: Long-term memory and context retention
4. **Performance Optimization**: Caching strategies and parallel execution
5. **Monitoring Dashboard**: Real-time workflow visualization

## Troubleshooting

### Common Issues

**Issue**: Agents falling back to mocks
- **Cause**: Real agent implementations not available
- **Solution**: Ensure `tta.prod/src/agents/` directory exists with agent implementations

**Issue**: Redis connection errors
- **Cause**: Redis not running or incorrect URL
- **Solution**: Verify Redis is running: `redis-cli ping`

**Issue**: Safety validation blocking all inputs
- **Cause**: Safety service misconfigured
- **Solution**: Check safety rules configuration and sensitivity settings

**Issue**: Workflow timeouts
- **Cause**: Agent processing taking too long
- **Solution**: Increase retry config timeouts or optimize agent implementations

## References

- [Agent Adapters Documentation](../src/agent_orchestration/adapters.py)
- [Therapeutic Safety Service](../src/agent_orchestration/therapeutic_safety.py)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Redis Documentation](https://redis.io/docs/)
