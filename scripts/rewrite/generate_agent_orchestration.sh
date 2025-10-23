#!/bin/bash
# =============================================================================
# Gemini CLI Code Generation Script - Agent Orchestration Component
# =============================================================================
# Purpose: Generate production-ready Agent Orchestration component using Google ADK
# Usage: ./scripts/rewrite/generate_agent_orchestration.sh
# =============================================================================

set -e  # Exit on error

# Source environment variables for database access
source scripts/gemini-cli-env.sh

echo ""
echo "========================================="
echo "TTA Agent Orchestration Code Generation"
echo "========================================="
echo ""
echo "Using Gemini CLI to generate Agent Orchestration component..."
echo ""

# Create output directories
mkdir -p src/agent_orchestration
mkdir -p tests/agent_orchestration

# Generate Agent Orchestration component using Gemini CLI
gemini "
# Task: Generate TTA Agent Orchestration Component using Google ADK

## Context Files to Read
1. **Specifications:**
   - .kiro/specs/ai-agent-orchestration/requirements.md
   - .kiro/specs/ai-agent-orchestration/design.md
   - .kiro/specs/ai-agent-orchestration/metrics.md

2. **Project Context:**
   - GEMINI.md (TTA project overview, tech stack, conventions)

3. **ADK Reference:**
   - docs/development/google-adk-reference.md (ADK patterns and examples)
   - .augment/rules/google-adk-integration.md (TTA-specific ADK conventions)

4. **Existing Configuration:**
   - src/agent_orchestration/adk_config.py (centralized ADK configuration)

## Tech Stack
- **Language:** Python 3.12
- **Framework:** Google ADK (Agent Development Kit) v1.16.0
- **Model:** Gemini 2.0 Flash (unlimited usage, optimized for speed)
- **Databases:** Neo4j (knowledge graphs), Redis (session state)
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Quality:** ruff (linting), pyright (type checking)

## Architecture Requirements

### 1. Agent Types (Use Google ADK)
- **InputProcessorAgent (IPA):** LlmAgent for processing user input
- **WorldBuilderAgent (WBA):** LlmAgent for updating world state
- **NarrativeGeneratorAgent (NGA):** LlmAgent for generating narrative

### 2. Workflow Patterns
- **Sequential Workflow:** IPA → WBA → NGA (use SequentialAgent)
- **Parallel Validation:** Safety + Coherence + Consistency (use ParallelAgent)
- **Iterative Refinement:** Narrative quality improvement (use LoopAgent)

### 3. Integration Points
- **Neo4j:** World state persistence (use async tools)
- **Redis:** Session state management (use async tools)
- **TTA Component System:** Follow component maturity workflow

## Code Generation Requirements

### File 1: src/agent_orchestration/agents.py
Generate specialized agents (IPA, WBA, NGA) using Google ADK:

\`\`\`python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from src.agent_orchestration.adk_config import DEFAULT_MODEL, AGENT_CONFIG, SESSION_STATE_KEYS

# Import database tools (to be created)
from src.agent_orchestration.tools import (
    get_world_state_from_neo4j,
    update_world_state_in_neo4j,
    get_session_state_from_redis,
    update_session_state_in_redis,
)

# Create InputProcessorAgent
input_processor_agent = LlmAgent(
    name=AGENT_CONFIG[\"input_processor\"][\"name\"],
    model=DEFAULT_MODEL,
    instruction=\"\"\"
    Process user input and extract therapeutic intent.

    Your role:
    1. Analyze user input for emotional state, intent, and context
    2. Extract therapeutic goals and narrative preferences
    3. Identify safety concerns or crisis indicators
    4. Structure input for downstream agents

    Output format: JSON with keys: intent, emotional_state, safety_level, narrative_context
    \"\"\",
    description=AGENT_CONFIG[\"input_processor\"][\"description\"],
    output_key=SESSION_STATE_KEYS[\"processed_input\"],
    tools=[
        FunctionTool(func=get_session_state_from_redis),
        FunctionTool(func=update_session_state_in_redis),
    ],
)

# Create WorldBuilderAgent
world_builder_agent = LlmAgent(
    name=AGENT_CONFIG[\"world_builder\"][\"name\"],
    model=DEFAULT_MODEL,
    instruction=\"\"\"
    Build and update therapeutic world state based on processed input.

    Your role:
    1. Retrieve current world state from Neo4j
    2. Update world state based on {processed_input}
    3. Maintain narrative consistency and therapeutic coherence
    4. Track character development and story progression

    Output format: Updated world state as JSON
    \"\"\",
    description=AGENT_CONFIG[\"world_builder\"][\"description\"],
    output_key=SESSION_STATE_KEYS[\"world_state\"],
    tools=[
        FunctionTool(func=get_world_state_from_neo4j),
        FunctionTool(func=update_world_state_in_neo4j),
    ],
)

# Create NarrativeGeneratorAgent
narrative_generator_agent = LlmAgent(
    name=AGENT_CONFIG[\"narrative_generator\"][\"name\"],
    model=DEFAULT_MODEL,
    instruction=\"\"\"
    Generate therapeutic narrative content using world state.

    Your role:
    1. Use {world_state} to generate contextually appropriate narrative
    2. Incorporate therapeutic techniques (CBT, narrative therapy, etc.)
    3. Maintain engaging storytelling while supporting mental health goals
    4. Provide meaningful choices that promote reflection and growth

    Output format: Narrative text with embedded choices
    \"\"\",
    description=AGENT_CONFIG[\"narrative_generator\"][\"description\"],
    output_key=SESSION_STATE_KEYS[\"narrative_response\"],
)
\`\`\`

### File 2: src/agent_orchestration/workflows.py
Generate workflow orchestration using Google ADK:

\`\`\`python
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import exit_loop
from src.agent_orchestration.agents import (
    input_processor_agent,
    world_builder_agent,
    narrative_generator_agent,
)
from src.agent_orchestration.adk_config import WORKFLOW_CONFIG

# Sequential Workflow: IPA → WBA → NGA
tta_sequential_workflow = SequentialAgent(
    name=WORKFLOW_CONFIG[\"sequential\"][\"name\"],
    description=WORKFLOW_CONFIG[\"sequential\"][\"description\"],
    sub_agents=[
        input_processor_agent,
        world_builder_agent,
        narrative_generator_agent,
    ],
)

# Parallel Validation Workflow
# (Create validation agents and parallel workflow)

# Iterative Refinement Workflow
# (Create refinement agent with exit_loop tool and LoopAgent)
\`\`\`

### File 3: src/agent_orchestration/tools.py
Generate async database tools for Neo4j and Redis:

\`\`\`python
import asyncio
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext

async def get_world_state_from_neo4j(session_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    \"\"\"Retrieve world state from Neo4j.\"\"\"
    # TODO: Implement Neo4j query
    await asyncio.sleep(0.1)  # Simulate async operation
    world_state = {\"location\": \"forest\", \"characters\": []}
    tool_context.state[\"world_state\"] = world_state
    return world_state

async def update_world_state_in_neo4j(
    session_id: str,
    world_state: Dict[str, Any],
    tool_context: ToolContext
) -> Dict[str, Any]:
    \"\"\"Update world state in Neo4j.\"\"\"
    # TODO: Implement Neo4j update
    await asyncio.sleep(0.1)  # Simulate async operation
    return {\"success\": True, \"updated_state\": world_state}

# Similar functions for Redis
\`\`\`

### File 4: src/agent_orchestration/core.py
Generate main orchestration service:

\`\`\`python
from typing import Dict, Any
from src.agent_orchestration.workflows import tta_sequential_workflow

class AgentOrchestrationService:
    \"\"\"Main service for TTA agent orchestration.\"\"\"

    def __init__(self):
        self.workflow = tta_sequential_workflow

    async def process_user_input(
        self,
        user_input: str,
        session_id: str
    ) -> Dict[str, Any]:
        \"\"\"Process user input through TTA workflow.\"\"\"
        result = await self.workflow.run_async(
            user_input=user_input,
            session_id=session_id
        )
        return {
            \"narrative_response\": result.state.get(\"narrative_response\"),
            \"world_state\": result.state.get(\"world_state\"),
            \"processed_input\": result.state.get(\"processed_input\"),
        }
\`\`\`

### File 5: tests/agent_orchestration/test_agents.py
Generate comprehensive unit tests (target 70%+ coverage):

\`\`\`python
import pytest
from google.adk.agents import LlmAgent
from src.agent_orchestration.agents import (
    input_processor_agent,
    world_builder_agent,
    narrative_generator_agent,
)

@pytest.mark.asyncio
async def test_input_processor_agent():
    \"\"\"Test InputProcessorAgent processes user input correctly.\"\"\"
    result = await input_processor_agent.run_async(
        user_input=\"I'm feeling anxious about my upcoming presentation.\"
    )

    assert result is not None
    assert \"processed_input\" in result.state
    # Add more assertions

@pytest.mark.asyncio
async def test_world_builder_agent():
    \"\"\"Test WorldBuilderAgent updates world state.\"\"\"
    # Test implementation

@pytest.mark.asyncio
async def test_narrative_generator_agent():
    \"\"\"Test NarrativeGeneratorAgent generates narrative.\"\"\"
    # Test implementation
\`\`\`

### File 6: tests/agent_orchestration/test_workflows.py
Generate workflow integration tests:

\`\`\`python
import pytest
from src.agent_orchestration.workflows import tta_sequential_workflow

@pytest.mark.asyncio
async def test_sequential_workflow():
    \"\"\"Test complete IPA → WBA → NGA workflow.\"\"\"
    result = await tta_sequential_workflow.run_async(
        user_input=\"I want to explore a peaceful forest.\",
        session_id=\"test-session-123\"
    )

    assert \"processed_input\" in result.state
    assert \"world_state\" in result.state
    assert \"narrative_response\" in result.state
\`\`\`

## Code Quality Requirements
1. **Type Hints:** All functions must have complete type annotations
2. **Docstrings:** Google-style docstrings for all public functions/classes
3. **Error Handling:** Comprehensive try-except blocks with logging
4. **Async/Await:** Use async functions for all I/O operations
5. **Testing:** 70%+ test coverage with pytest
6. **Linting:** Pass ruff linting (no violations)
7. **Type Checking:** Pass pyright type checking

## TTA-Specific Conventions
1. **Configuration:** Always use centralized config from \`adk_config.py\`
2. **Session State Keys:** Use \`SESSION_STATE_KEYS\` constants
3. **Model Selection:** Use \`DEFAULT_MODEL\` (gemini-2.0-flash)
4. **Agent Communication:** Use \`output_key\` for state management
5. **Database Access:** Use async tools with proper error handling

## Output Instructions
Generate complete, production-ready code for all 6 files listed above. Ensure:
- All imports are correct and available
- All code follows TTA conventions
- All tests are comprehensive and pass
- Code is ready for immediate use in TTA project

Generate the code now.
"

echo ""
echo "✓ Code generation complete!"
echo ""
echo "Generated files:"
echo "  - src/agent_orchestration/agents.py"
echo "  - src/agent_orchestration/workflows.py"
echo "  - src/agent_orchestration/tools.py"
echo "  - src/agent_orchestration/core.py"
echo "  - tests/agent_orchestration/test_agents.py"
echo "  - tests/agent_orchestration/test_workflows.py"
echo ""
echo "Next steps:"
echo "  1. Review generated code"
echo "  2. Run tests: uv run pytest tests/agent_orchestration/ -v --cov=src/agent_orchestration"
echo "  3. Check coverage: Should be 70%+"
echo "  4. Run linting: uv run ruff check src/agent_orchestration/"
echo "  5. Run type checking: uv run pyright src/agent_orchestration/"
echo ""
