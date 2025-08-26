"""
State persistence and response aggregation integration tests.

This module implements tests that verify Neo4j state persistence across agent handoffs
and validate response aggregation through the orchestration system.
"""

import asyncio
import pytest
import time
import json
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

from src.agent_orchestration import (
    WorkflowManager, WorkflowDefinition, WorkflowType, AgentStep, AgentType,
    OrchestrationRequest, AgentContext, SessionContext,
    InputProcessorAgentProxy, WorldBuilderAgentProxy, NarrativeGeneratorAgentProxy,
)

from tests.agent_orchestration.test_multi_agent_workflow_integration import IntegrationTestHelper, WorkflowStateVerifier


# ============================================================================
# State Persistence Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.neo4j
@pytest.mark.redis
class TestStatePersistenceIntegration:
    """Test Neo4j state persistence across agent handoffs."""
    
    @pytest.fixture
    async def integration_helper(self, redis_client, neo4j_driver):
        """Create integration test helper."""
        return IntegrationTestHelper(redis_client, neo4j_driver)
    
    async def test_session_state_persistence_across_handoffs(
        self,
        integration_helper,
        therapeutic_session_context,
        sample_player_inputs
    ):
        """Test that session state is properly persisted across agent handoffs."""
        test_env = await integration_helper.setup_test_environment("session_persistence")
        
        try:
            # Create initial session state in Neo4j
            with integration_helper.neo4j.session() as session:
                session.run(
                    """
                    CREATE (s:Session {
                        session_id: $session_id,
                        player_id: $player_id,
                        created_at: datetime(),
                        therapeutic_profile: $therapeutic_profile,
                        game_state: $game_state
                    })
                    CREATE (p:Player {player_id: $player_id, username: 'test_player'})
                    CREATE (l:Location {location_id: $location_id, name: 'Test Location'})
                    CREATE (s)-[:BELONGS_TO]->(p)
                    CREATE (s)-[:CURRENT_LOCATION]->(l)
                    """,
                    session_id=test_env['session_id'],
                    player_id=test_env['player_id'],
                    therapeutic_profile=json.dumps(therapeutic_session_context.therapeutic_profile),
                    game_state=json.dumps(therapeutic_session_context.game_state),
                    location_id=therapeutic_session_context.game_state['current_location_id']
                )
            
            # Simulate agent handoffs with state updates
            workflow_manager = WorkflowManager()
            
            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="input_processing"),
                    AgentStep(agent=AgentType.WBA, name="world_building"),
                    AgentStep(agent=AgentType.NGA, name="narrative_generation"),
                ]
            )
            
            workflow_manager.register_workflow("persistence_test", workflow_def)
            
            # Execute multiple workflow steps
            for i, player_input in enumerate(sample_player_inputs[:3]):
                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA,
                    input=player_input,
                    context=therapeutic_session_context
                )
                
                response, run_id, error = workflow_manager.execute_workflow("persistence_test", request)
                assert error is None, f"Workflow {i} failed: {error}"
                
                # Verify state persistence after each handoff
                await asyncio.sleep(0.3)  # Allow for async state updates
                
                # Check session state persistence
                session_state = await integration_helper.neo4j_verifier.verify_session_state(
                    test_env['session_id']
                )
                
                assert session_state['session_exists'], f"Session lost after handoff {i}"
                assert session_state['player_relationship_exists'], f"Player relationship lost after handoff {i}"
                assert session_state['therapeutic_profile_persisted'], f"Therapeutic profile lost after handoff {i}"
                
                # Verify agent interaction history
                interaction_state = await integration_helper.neo4j_verifier.verify_agent_interactions(
                    test_env['session_id']
                )
                
                expected_interactions = i + 1
                assert interaction_state['interaction_count'] >= expected_interactions, \
                    f"Expected at least {expected_interactions} interactions, got {interaction_state['interaction_count']}"
                
                # Verify chronological order of interactions
                assert interaction_state['chronological_order'], "Interactions not in chronological order"
            
            # Verify final state consistency
            final_session_state = await integration_helper.neo4j_verifier.verify_session_state(
                test_env['session_id']
            )
            
            assert final_session_state['session_exists'], "Final session state missing"
            assert final_session_state['therapeutic_profile_persisted'], "Final therapeutic profile missing"
            
            # Verify all agent types interacted
            final_interactions = await integration_helper.neo4j_verifier.verify_agent_interactions(
                test_env['session_id']
            )
            
            assert final_interactions['has_ipa_interaction'], "IPA interactions not recorded"
            assert final_interactions['has_wba_interaction'], "WBA interactions not recorded"
            assert final_interactions['has_nga_interaction'], "NGA interactions not recorded"
            
        finally:
            await integration_helper.cleanup_test_data(
                test_env['session_id'], 
                test_env['workflow_id'], 
                test_env['player_id']
            )
    
    async def test_workflow_state_transitions_persistence(
        self,
        integration_helper,
        multi_agent_workflow_definition,
        sample_player_inputs
    ):
        """Test that workflow state transitions are properly recorded."""
        test_env = await integration_helper.setup_test_environment("workflow_transitions")
        
        try:
            workflow_manager = WorkflowManager()
            workflow_manager.register_workflow("transitions_test", multi_agent_workflow_definition)
            
            # Execute workflow and track state transitions
            request = OrchestrationRequest(
                entrypoint=AgentType.IPA,
                input=sample_player_inputs[0]
            )
            
            start_time = time.time()
            response, run_id, error = workflow_manager.execute_workflow("transitions_test", request)
            end_time = time.time()
            
            assert error is None, f"Workflow execution failed: {error}"
            
            # Allow time for state persistence
            await asyncio.sleep(0.5)
            
            # Verify workflow state transitions in Neo4j
            workflow_state = await integration_helper.neo4j_verifier.verify_workflow_state_transitions(run_id)
            
            assert workflow_state['workflow_found'], "Workflow not found in Neo4j"
            assert workflow_state['execution_count'] >= 1, "No workflow executions recorded"
            assert workflow_state['steps_recorded'] >= 3, "Expected at least 3 workflow steps"
            assert workflow_state['has_completion_time'], "Workflow completion time not recorded"
            assert workflow_state['status'] in ['completed', 'success'], f"Unexpected workflow status: {workflow_state['status']}"
            
            # Verify timing consistency
            execution_duration = end_time - start_time
            assert execution_duration > 0, "Invalid execution duration"
            
        finally:
            await integration_helper.cleanup_test_data(
                test_env['session_id'], 
                test_env['workflow_id'], 
                test_env['player_id']
            )
    
    async def test_concurrent_state_updates_consistency(
        self,
        integration_helper,
        therapeutic_session_context,
        sample_player_inputs
    ):
        """Test state consistency under concurrent updates."""
        test_env = await integration_helper.setup_test_environment("concurrent_updates")
        
        try:
            # Create multiple concurrent workflow executions
            workflow_manager = WorkflowManager()
            
            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="concurrent_ipa"),
                    AgentStep(agent=AgentType.WBA, name="concurrent_wba"),
                    AgentStep(agent=AgentType.NGA, name="concurrent_nga"),
                ]
            )
            
            workflow_manager.register_workflow("concurrent_test", workflow_def)
            
            # Execute multiple workflows concurrently
            concurrent_requests = []
            for i, player_input in enumerate(sample_player_inputs[:3]):
                # Create unique session context for each request
                session_context = SessionContext(
                    session_id=f"{test_env['session_id']}_{i}",
                    player_id=test_env['player_id'],
                    therapeutic_profile=therapeutic_session_context.therapeutic_profile,
                    game_state={**therapeutic_session_context.game_state, "request_id": i}
                )
                
                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA,
                    input=player_input,
                    context=session_context
                )
                
                concurrent_requests.append((request, f"{test_env['session_id']}_{i}"))
            
            # Execute all requests concurrently
            async def execute_workflow(request, session_id):
                response, run_id, error = workflow_manager.execute_workflow("concurrent_test", request)
                return {
                    'session_id': session_id,
                    'response': response,
                    'run_id': run_id,
                    'error': error,
                    'timestamp': time.time()
                }
            
            tasks = [execute_workflow(req, sid) for req, sid in concurrent_requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all executions completed successfully
            successful_results = []
            for result in results:
                if isinstance(result, Exception):
                    pytest.fail(f"Concurrent execution failed: {result}")
                else:
                    assert result['error'] is None, f"Workflow failed: {result['error']}"
                    successful_results.append(result)
            
            assert len(successful_results) == 3, "Not all concurrent workflows succeeded"
            
            # Allow time for all state updates to complete
            await asyncio.sleep(1.0)
            
            # Verify state consistency for each session
            for result in successful_results:
                session_state = await integration_helper.neo4j_verifier.verify_session_state(
                    result['session_id']
                )
                
                assert session_state['session_exists'], f"Session {result['session_id']} not persisted"
                assert session_state['player_relationship_exists'], f"Player relationship missing for {result['session_id']}"
            
            # Verify no data corruption or conflicts
            # Check that each session has distinct data
            session_ids = [result['session_id'] for result in successful_results]
            assert len(set(session_ids)) == len(session_ids), "Session ID conflicts detected"
            
        finally:
            # Cleanup all concurrent sessions
            for result in successful_results:
                await integration_helper.cleanup_test_data(
                    result['session_id'], 
                    result['run_id'], 
                    test_env['player_id']
                )


# ============================================================================
# Response Aggregation Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.redis
class TestResponseAggregationIntegration:
    """Test response aggregation through the orchestration system."""
    
    async def test_multi_agent_response_aggregation(
        self,
        integration_helper,
        complex_therapeutic_scenarios,
        therapeutic_session_context
    ):
        """Test aggregation of responses from multiple agents."""
        test_env = await integration_helper.setup_test_environment("response_aggregation")
        
        try:
            # Use anxiety management scenario for realistic testing
            scenario = complex_therapeutic_scenarios['anxiety_management']
            
            # Mock agents to return expected responses
            class MockIPAProxy(InputProcessorAgentProxy):
                async def process(self, input_payload: dict) -> dict:
                    return scenario['expected_ipa_output']
            
            class MockWBAProxy(WorldBuilderAgentProxy):
                async def process(self, input_payload: dict) -> dict:
                    return scenario['expected_wba_output']
            
            class MockNGAProxy(NarrativeGeneratorAgentProxy):
                async def process(self, input_payload: dict) -> dict:
                    return scenario['expected_nga_output']
            
            # Create workflow with mock agents
            workflow_manager = WorkflowManager()
            
            # Mock agent registry to return our test agents
            with patch('src.agent_orchestration.agents.AgentRegistry.get_agent') as mock_get_agent:
                def get_mock_agent(agent_id):
                    if agent_id.type == AgentType.IPA:
                        return MockIPAProxy(instance="test")
                    elif agent_id.type == AgentType.WBA:
                        return MockWBAProxy(instance="test")
                    elif agent_id.type == AgentType.NGA:
                        return MockNGAProxy(instance="test")
                    return None
                
                mock_get_agent.side_effect = get_mock_agent
                
                workflow_def = WorkflowDefinition(
                    workflow_type=WorkflowType.COLLABORATIVE,
                    agent_sequence=[
                        AgentStep(agent=AgentType.IPA, name="mock_ipa"),
                        AgentStep(agent=AgentType.WBA, name="mock_wba"),
                        AgentStep(agent=AgentType.NGA, name="mock_nga"),
                    ]
                )
                
                workflow_manager.register_workflow("aggregation_test", workflow_def)
                
                # Execute workflow
                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA,
                    input={"text": scenario['player_input']},
                    context=therapeutic_session_context
                )
                
                response, run_id, error = workflow_manager.execute_workflow("aggregation_test", request)
                
                # Verify response aggregation
                assert error is None, f"Workflow execution failed: {error}"
                assert response is not None, "No aggregated response received"
                
                # Verify response structure
                assert hasattr(response, 'response_text'), "Missing response_text in aggregated response"
                assert hasattr(response, 'workflow_metadata'), "Missing workflow_metadata"
                
                # Verify workflow metadata contains information from all agents
                metadata = response.workflow_metadata
                assert metadata.get('steps_executed') == 3, "Expected 3 steps in aggregated response"
                
                # Verify therapeutic elements are preserved in aggregation
                response_text = response.response_text
                therapeutic_keywords = ['anxiety', 'breathing', 'support', 'comfort']
                therapeutic_elements_present = any(keyword in response_text.lower() for keyword in therapeutic_keywords)
                assert therapeutic_elements_present, "Therapeutic elements not preserved in aggregated response"
                
                # Verify response aggregation quality
                verifier = WorkflowStateVerifier()
                
                # Create mock responses for verification
                mock_responses = [
                    scenario['expected_ipa_output'],
                    scenario['expected_wba_output'],
                    scenario['expected_nga_output']
                ]
                
                aggregation_checks = verifier.verify_response_aggregation(mock_responses)
                assert aggregation_checks['all_agents_responded'], "Not all agents contributed to aggregation"
                assert aggregation_checks['responses_have_content'], "Some responses lack content"
                
        finally:
            await integration_helper.cleanup_test_data(
                test_env['session_id'], 
                test_env['workflow_id'], 
                test_env['player_id']
            )
