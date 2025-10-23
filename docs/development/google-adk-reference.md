# Google ADK (Agent Development Kit) Reference for TTA

**Version:** 1.16.0
**Date:** 2025-10-21
**Source:** Context7 Documentation Retrieval
**Purpose:** Quick reference for TTA's Agent Orchestration implementation

---

## Table of Contents
1. [Agent Types](#agent-types)
2. [Session State Management](#session-state-management)
3. [Agent Communication](#agent-communication)
4. [Callbacks](#callbacks)
5. [Tools](#tools)
6. [TTA-Specific Patterns](#tta-specific-patterns)
7. [Common Pitfalls](#common-pitfalls)

---

## Agent Types

### LlmAgent
**Purpose:** Single LLM-powered agent with tool use and dynamic routing

**Parameters:**
- `name` (str): Agent identifier
- `model` (str): Model name (e.g., "gemini-2.0-flash")
- `instruction` (str): Agent's core instructions
- `description` (str): Human-readable description
- `tools` (list): List of tools/functions the agent can use
- `sub_agents` (list): Child agents for hierarchical orchestration
- `output_key` (str, optional): Key to store agent's output in session state
- `before_agent_callback` (callable, optional): Pre-execution callback
- `after_agent_callback` (callable, optional): Post-execution callback

**Example:**
```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="input_processor",
    model="gemini-2.0-flash",
    instruction="Process user input and extract therapeutic intent.",
    description="Processes user input for therapeutic storytelling",
    output_key="processed_input"
)
```

---

### SequentialAgent
**Purpose:** Execute agents in a predefined order (agent1 → agent2 → agent3)

**Parameters:**
- `name` (str): Workflow identifier
- `description` (str): Workflow description
- `sub_agents` (list): List of agents to execute sequentially

**Example:**
```python
from google.adk.agents import SequentialAgent, LlmAgent

# Define agents
agent1 = LlmAgent(name="researcher", model="gemini-2.0-flash", output_key="research")
agent2 = LlmAgent(name="writer", model="gemini-2.0-flash", output_key="draft")
agent3 = LlmAgent(name="editor", model="gemini-2.0-flash", output_key="final")

# Create sequential workflow
workflow = SequentialAgent(
    name="content_pipeline",
    description="Research → Write → Edit content sequentially",
    sub_agents=[agent1, agent2, agent3]
)
```

**TTA Use Case:** IPA → WBA → NGA (sequential processing of user input)

---

### ParallelAgent
**Purpose:** Execute multiple agents concurrently

**Parameters:**
- `name` (str): Workflow identifier
- `description` (str): Workflow description
- `sub_agents` (list): List of agents to execute in parallel

**Example:**
```python
from google.adk.agents import ParallelAgent, LlmAgent

# Define agents that can run concurrently
fact_checker = LlmAgent(name="fact_checker", model="gemini-2.0-flash", output_key="facts")
sentiment = LlmAgent(name="sentiment", model="gemini-2.0-flash", output_key="sentiment")
intent = LlmAgent(name="intent", model="gemini-2.0-flash", output_key="intent")

# Run in parallel
parallel_workflow = ParallelAgent(
    name="content_analyzer",
    description="Analyze content from multiple perspectives simultaneously",
    sub_agents=[fact_checker, sentiment, intent]
)
```

**TTA Use Case:** Parallel validation (therapeutic safety + narrative coherence + world consistency)

---

### LoopAgent
**Purpose:** Iterative refinement with max iterations

**Parameters:**
- `name` (str): Loop identifier
- `description` (str): Loop description
- `sub_agents` (list): Agents to execute in loop (typically one agent)
- `max_iterations` (int): Maximum number of iterations

**Example:**
```python
from google.adk.agents import LoopAgent, LlmAgent
from google.adk.tools import exit_loop

# Define agent that iterates
refiner = LlmAgent(
    name="narrative_refiner",
    model="gemini-2.0-flash",
    instruction="Refine narrative. Call exit_loop when complete.",
    tools=[exit_loop],
    output_key="refined_narrative"
)

# Create loop workflow
iterative_workflow = LoopAgent(
    name="iterative_refiner",
    description="Refine narrative through multiple iterations",
    sub_agents=[refiner],
    max_iterations=3
)
```

**TTA Use Case:** Iterative narrative refinement until quality threshold met

---

## Session State Management

### Accessing State
**In Callbacks:**
```python
from google.adk.agents import CallbackContext

def my_callback(callback_context: CallbackContext):
    # Read state
    user_name = callback_context.state.get("user_name", "Guest")

    # Write state
    callback_context.state["last_action"] = "processed_input"

    # State changes are automatically tracked in event.state_delta
```

**In Tools:**
```python
from google.adk.tools.tool_context import ToolContext

def my_tool(param: str, tool_context: ToolContext) -> str:
    # Read state
    session_id = tool_context.state.get("session_id")

    # Write state
    tool_context.state["last_tool_call"] = "my_tool"

    return "Tool result"
```

### TTA Session State Keys
```python
SESSION_STATE_KEYS = {
    "processed_input": "processed_input",      # From InputProcessorAgent
    "world_state": "world_state",              # From WorldBuilderAgent
    "narrative_response": "narrative_response", # From NarrativeGeneratorAgent
    "user_input": "user_input",                # Original user input
    "session_id": "session_id",                # Session identifier
    "iteration_count": "iteration_count",      # For loop workflows
}
```

---

## Agent Communication

### Hierarchical Multi-Agent Systems
**Pattern:** Parent agent delegates to sub-agents

```python
from google.adk.agents import LlmAgent

# Define specialized agents
greeter = LlmAgent(name="greeter", model="gemini-2.0-flash", ...)
task_executor = LlmAgent(name="task_executor", model="gemini-2.0-flash", ...)

# Create coordinator with sub-agents
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash",
    description="Coordinates greetings and task execution",
    instruction="Delegate to greeter or task_executor as needed.",
    sub_agents=[greeter, task_executor]
)
```

### Output Keys for Agent Communication
**Pattern:** Use `output_key` to store agent results in session state

```python
agent1 = LlmAgent(
    name="agent1",
    model="gemini-2.0-flash",
    instruction="Extract topic from user input.",
    output_key="topic"  # Stores result in session.state["topic"]
)

agent2 = LlmAgent(
    name="agent2",
    model="gemini-2.0-flash",
    instruction="Based on {topic}, generate summary.",  # References state["topic"]
    output_key="summary"
)
```

---

## Callbacks

### Before Agent Callback
**Purpose:** Execute logic before agent runs (can skip agent execution)

```python
from google.adk.agents import CallbackContext
from google.genai import types
from typing import Optional

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Returns:
        None: Allow agent to execute normally
        types.Content: Skip agent execution and use this content instead
    """
    # Check condition
    if callback_context.state.get("skip_agent", False):
        return types.Content(
            parts=[types.Part(text="Agent skipped by callback")],
            role="model"
        )

    # Allow agent to execute
    return None

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.0-flash",
    before_agent_callback=before_agent_callback
)
```

### After Agent Callback
**Purpose:** Execute logic after agent runs (can modify output)

```python
def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Returns:
        None: Use agent's original output
        types.Content: Replace agent's output with this content
    """
    # Check condition
    if callback_context.state.get("add_note", False):
        return types.Content(
            parts=[types.Part(text="Modified output with note")],
            role="model"
        )

    # Use agent's original output
    return None
```

### Tool Callbacks
**Before Tool:**
```python
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any, Optional

def before_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict]:
    """
    Returns:
        None: Execute tool normally
        Dict: Skip tool execution and use this as result
    """
    # Modify args
    if tool.name == "search" and args.get("query") == "blocked":
        return {"result": "Tool execution blocked"}

    # Execute tool normally
    return None
```

**After Tool:**
```python
def after_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    result: Dict
) -> Optional[Dict]:
    """
    Returns:
        None: Use tool's original result
        Dict: Replace tool's result with this
    """
    # Modify result
    if tool.name == "get_weather" and result.get("temperature", 0) < 0:
        result["condition"] = "Freezing"

    return None  # Use modified result
```

---

## Tools

### Function Tools
```python
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

def my_tool(param: str, tool_context: ToolContext) -> str:
    """Tool description for LLM.

    Args:
        param: Parameter description

    Returns:
        Result description
    """
    # Access state
    session_id = tool_context.state.get("session_id")

    # Update state
    tool_context.state["last_tool"] = "my_tool"

    return f"Processed: {param}"

# Create tool
tool = FunctionTool(func=my_tool)

# Add to agent
agent = LlmAgent(
    name="my_agent",
    model="gemini-2.0-flash",
    tools=[tool]
)
```

### Async Tools
```python
import asyncio
from google.adk.tools import FunctionTool

async def async_tool(param: str) -> str:
    """Async tool for external API calls."""
    await asyncio.sleep(0.5)  # Simulate API call
    return f"Async result: {param}"

# ADK handles async execution automatically
tool = FunctionTool(func=async_tool)
```

---

## TTA-Specific Patterns

### Pattern 1: Sequential Therapeutic Workflow
```python
# IPA → WBA → NGA
from google.adk.agents import SequentialAgent, LlmAgent

input_processor = LlmAgent(
    name="InputProcessorAgent",
    model="gemini-2.0-flash",
    instruction="Extract therapeutic intent from user input.",
    output_key="processed_input"
)

world_builder = LlmAgent(
    name="WorldBuilderAgent",
    model="gemini-2.0-flash",
    instruction="Update world state based on {processed_input}.",
    output_key="world_state"
)

narrative_generator = LlmAgent(
    name="NarrativeGeneratorAgent",
    model="gemini-2.0-flash",
    instruction="Generate therapeutic narrative using {world_state}.",
    output_key="narrative_response"
)

tta_workflow = SequentialAgent(
    name="TTAWorkflow",
    description="TTA therapeutic storytelling workflow",
    sub_agents=[input_processor, world_builder, narrative_generator]
)
```

### Pattern 2: Parallel Validation
```python
# Validate narrative from multiple perspectives
from google.adk.agents import ParallelAgent, LlmAgent

safety_validator = LlmAgent(
    name="SafetyValidator",
    model="gemini-2.0-flash",
    instruction="Validate therapeutic safety.",
    output_key="safety_score"
)

coherence_validator = LlmAgent(
    name="CoherenceValidator",
    model="gemini-2.0-flash",
    instruction="Validate narrative coherence.",
    output_key="coherence_score"
)

consistency_validator = LlmAgent(
    name="ConsistencyValidator",
    model="gemini-2.0-flash",
    instruction="Validate world consistency.",
    output_key="consistency_score"
)

validation_workflow = ParallelAgent(
    name="ValidationWorkflow",
    description="Parallel validation of narrative quality",
    sub_agents=[safety_validator, coherence_validator, consistency_validator]
)
```

---

## Common Pitfalls

### 1. Blocking Async Operations
❌ **Wrong:**
```python
import time

def my_tool():
    time.sleep(2)  # Blocks entire event loop!
```

✅ **Correct:**
```python
import asyncio

async def my_tool():
    await asyncio.sleep(2)  # Non-blocking, parallel-friendly
```

### 2. Missing Output Keys
❌ **Wrong:**
```python
agent1 = LlmAgent(name="agent1", model="gemini-2.0-flash")
agent2 = LlmAgent(
    name="agent2",
    model="gemini-2.0-flash",
    instruction="Use {agent1_output}"  # Won't work!
)
```

✅ **Correct:**
```python
agent1 = LlmAgent(
    name="agent1",
    model="gemini-2.0-flash",
    output_key="agent1_output"  # Store in state
)
agent2 = LlmAgent(
    name="agent2",
    model="gemini-2.0-flash",
    instruction="Use {agent1_output}"  # References state
)
```

### 3. Modifying State Outside Callbacks/Tools
❌ **Wrong:**
```python
# Don't modify state directly
session.state["my_key"] = "value"
```

✅ **Correct:**
```python
# Modify state in callbacks or tools
def my_callback(callback_context: CallbackContext):
    callback_context.state["my_key"] = "value"
```

### 4. Forgetting to Return None in Callbacks
❌ **Wrong:**
```python
def my_callback(callback_context: CallbackContext):
    # Do something
    pass  # Implicitly returns None, but unclear
```

✅ **Correct:**
```python
def my_callback(callback_context: CallbackContext):
    # Do something
    return None  # Explicitly allow normal execution
```

---

## Additional Resources

- **Official ADK Documentation:** https://google.github.io/adk-docs/
- **ADK Python Repository:** https://github.com/google/adk-python
- **ADK Samples:** https://github.com/google/adk-samples
- **TTA ADK Configuration:** `src/agent_orchestration/adk_config.py`
- **TTA ADK Tests:** `tests/test_adk_integration.py`

---

**Last Updated:** 2025-10-21
**Maintained By:** TTA Development Team
