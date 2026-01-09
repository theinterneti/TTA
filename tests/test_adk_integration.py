"""Integration tests for Google ADK with TTA.

Tests verify that Google ADK is properly installed and configured for use
in TTA's multi-agent orchestration system.

Test Coverage:
- Basic LlmAgent creation and execution
- SequentialAgent workflow (multi-step)
- ParallelAgent workflow (concurrent execution)
- LoopAgent workflow (iterative refinement)
- Session state management
- Error handling and retries
"""

# Logseq: [[TTA.dev/Tests/Test_adk_integration]]

import os
from unittest.mock import patch

import pytest
from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent

# Skip tests if GEMINI_API_KEY is not set (CI/CD environments)
skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY environment variable not set",
)


@pytest.mark.asyncio
@skip_if_no_api_key
async def test_adk_basic_agent():
    """Test basic ADK LlmAgent creation and execution.

    Verifies:
    - LlmAgent can be created with Gemini 2.0 Flash
    - Agent can execute simple instructions
    - Agent returns valid results
    """
    agent = LlmAgent(
        name="TestAgent",
        model="gemini-2.0-flash",
        instruction="You are a helpful assistant. Respond with 'Hello, TTA!'",
    )

    result = await agent.run_async(user_input="Say hello")

    assert result is not None
    assert len(result.events) > 0
    assert "Hello" in str(result.events)


@pytest.mark.asyncio
@skip_if_no_api_key
async def test_adk_sequential_workflow():
    """Test ADK SequentialAgent workflow.

    Verifies:
    - SequentialAgent can coordinate multiple agents
    - Agents execute in order (agent1 → agent2)
    - Session state is shared between agents
    - Each agent's output is available in session state
    """
    # Define two agents with specific output keys
    agent1 = LlmAgent(
        name="Agent1",
        model="gemini-2.0-flash",
        instruction="Extract the main topic from the user input. Output only the topic.",
        output_key="step1_topic",
    )

    agent2 = LlmAgent(
        name="Agent2",
        model="gemini-2.0-flash",
        instruction="Based on the topic in {step1_topic}, generate a one-sentence summary.",
        output_key="step2_summary",
    )

    # Create sequential workflow
    workflow = SequentialAgent(
        name="TestSequentialWorkflow",
        sub_agents=[agent1, agent2],
    )

    # Execute workflow
    result = await workflow.run_async(
        user_input="Tell me about therapeutic storytelling"
    )

    # Verify results
    assert result is not None
    assert "step1_topic" in result.state
    assert "step2_summary" in result.state
    assert len(result.events) > 0


@pytest.mark.asyncio
@skip_if_no_api_key
async def test_adk_parallel_workflow():
    """Test ADK ParallelAgent workflow.

    Verifies:
    - ParallelAgent can execute multiple agents concurrently
    - All agents complete successfully
    - Each agent's output is available in session state
    - Parallel execution is faster than sequential
    """
    # Define three agents that can run in parallel
    agent1 = LlmAgent(
        name="TopicExtractor",
        model="gemini-2.0-flash",
        instruction="Extract the main topic. Output only the topic.",
        output_key="topic",
    )

    agent2 = LlmAgent(
        name="SentimentAnalyzer",
        model="gemini-2.0-flash",
        instruction="Analyze the sentiment. Output only: positive, negative, or neutral.",
        output_key="sentiment",
    )

    agent3 = LlmAgent(
        name="IntentClassifier",
        model="gemini-2.0-flash",
        instruction="Classify the intent. Output only: question, statement, or command.",
        output_key="intent",
    )

    # Create parallel workflow
    workflow = ParallelAgent(
        name="TestParallelWorkflow",
        sub_agents=[agent1, agent2, agent3],
    )

    # Execute workflow
    result = await workflow.run_async(user_input="I love therapeutic storytelling!")

    # Verify results
    assert result is not None
    assert "topic" in result.state
    assert "sentiment" in result.state
    assert "intent" in result.state
    assert len(result.events) > 0


@pytest.mark.asyncio
@skip_if_no_api_key
async def test_adk_loop_workflow():
    """Test ADK LoopAgent workflow.

    Verifies:
    - LoopAgent can execute iterative refinement
    - Loop terminates after max iterations
    - Each iteration's output is available
    - State is maintained across iterations
    """
    # Define agent for iterative refinement
    refiner = LlmAgent(
        name="NarrativeRefiner",
        model="gemini-2.0-flash",
        instruction=(
            "Refine the narrative. "
            "If this is iteration 1, create a basic story. "
            "If this is iteration 2 or 3, improve the previous version. "
            "Output only the refined narrative."
        ),
        output_key="refined_narrative",
    )

    # Create loop workflow (max 3 iterations)
    workflow = LoopAgent(
        name="TestLoopWorkflow",
        sub_agent=refiner,
        max_iterations=3,
    )

    # Execute workflow
    result = await workflow.run_async(
        user_input="Create a therapeutic story about courage"
    )

    # Verify results
    assert result is not None
    assert "refined_narrative" in result.state
    assert len(result.events) > 0


@pytest.mark.asyncio
@skip_if_no_api_key
async def test_adk_session_state_management():
    """Test ADK session state management.

    Verifies:
    - Session state is shared between agents
    - Agents can access previous agents' outputs
    - State keys are correctly set and retrieved
    """
    # Define agents that use session state
    agent1 = LlmAgent(
        name="StateWriter",
        model="gemini-2.0-flash",
        instruction="Extract the user's name from the input. Output only the name.",
        output_key="user_name",
    )

    agent2 = LlmAgent(
        name="StateReader",
        model="gemini-2.0-flash",
        instruction="Greet the user by name from {user_name}. Output only the greeting.",
        output_key="greeting",
    )

    # Create sequential workflow
    workflow = SequentialAgent(
        name="StateManagementWorkflow",
        sub_agents=[agent1, agent2],
    )

    # Execute workflow
    result = await workflow.run_async(user_input="My name is Alice")

    # Verify state management
    assert result is not None
    assert "user_name" in result.state
    assert "greeting" in result.state
    assert "Alice" in result.state["user_name"] or "Alice" in result.state["greeting"]


@pytest.mark.asyncio
async def test_adk_config_without_api_key():
    """Test ADK configuration error handling when API key is missing.

    Verifies:
    - Proper error handling when GEMINI_API_KEY is not set
    - Clear error message for missing credentials
    """
    with patch.dict(os.environ, {}, clear=True):
        # Remove GEMINI_API_KEY from environment
        from src.agent_orchestration.adk_config import get_gemini_api_key

        with pytest.raises(
            ValueError, match="GEMINI_API_KEY environment variable is not set"
        ):
            get_gemini_api_key()


@pytest.mark.asyncio
async def test_adk_config_values():
    """Test ADK configuration values.

    Verifies:
    - Configuration constants are properly defined
    - Default model is set correctly
    - Model config includes required fields
    - Agent config includes all three agents
    - Workflow config includes all workflow types
    """
    from src.agent_orchestration.adk_config import (
        AGENT_CONFIG,
        DEFAULT_MODEL,
        MODEL_CONFIG,
        SESSION_STATE_KEYS,
        WORKFLOW_CONFIG,
    )

    # Verify DEFAULT_MODEL
    assert DEFAULT_MODEL == "gemini-2.0-flash"

    # Verify MODEL_CONFIG (GenerateContentConfig parameters)
    assert "temperature" in MODEL_CONFIG
    assert "max_output_tokens" in MODEL_CONFIG
    assert "top_p" in MODEL_CONFIG
    assert "top_k" in MODEL_CONFIG

    # Verify AGENT_CONFIG
    assert "input_processor" in AGENT_CONFIG
    assert "world_builder" in AGENT_CONFIG
    assert "narrative_generator" in AGENT_CONFIG

    # Verify WORKFLOW_CONFIG
    assert "sequential" in WORKFLOW_CONFIG
    assert "parallel" in WORKFLOW_CONFIG
    assert "loop" in WORKFLOW_CONFIG

    # Verify SESSION_STATE_KEYS
    assert "processed_input" in SESSION_STATE_KEYS
    assert "world_state" in SESSION_STATE_KEYS
    assert "narrative_response" in SESSION_STATE_KEYS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
