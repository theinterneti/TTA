"""
Integration tests for Phase 2A TTA Platform components
Tests multi-stakeholder web interfaces, AI/ML integration, and Neo4j living worlds
"""

import asyncio
import json
from datetime import datetime
from typing import Any

import aiohttp
import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from neo4j import AsyncGraphDatabase

from src.ai_components.langgraph_integration import TherapeuticWorkflowManager
from src.components.therapeutic_systems_enhanced.therapeutic_integration_system import (
    TherapeuticIntegrationSystem,
)
from src.living_worlds.neo4j_integration import LivingWorldsManager


class TestPhase2AIntegration:
    """Integration tests for Phase 2A components"""

    @pytest_asyncio.fixture
    async def setup_test_environment(self, neo4j_config, redis_config):
        """Set up test environment with all Phase 2A services"""
        # Build Redis URL with password if provided
        redis_url = f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
        if redis_config.get('password'):
            redis_url = f"redis://:{redis_config['password']}@{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"

        # Initialize test databases
        self.redis = aioredis.from_url(redis_url)
        self.neo4j_driver = AsyncGraphDatabase.driver(
            neo4j_config["uri"], auth=(neo4j_config["user"], neo4j_config["password"])
        )

        # Initialize managers
        self.living_worlds = LivingWorldsManager(
            neo4j_uri=neo4j_config["uri"],
            neo4j_user=neo4j_config["user"],
            neo4j_password=neo4j_config["password"],
            redis_url=redis_url,
        )

        self.workflow_manager = TherapeuticWorkflowManager(
            openai_api_key="test-key", redis_url=redis_url
        )

        self.therapeutic_system = TherapeuticIntegrationSystem()

        # Initialize all systems
        await self.living_worlds.initialize()
        await self.workflow_manager.initialize()

        yield

        # Cleanup
        # Note: Skip flushdb in staging as dangerous commands are disabled
        # await self.redis.flushdb()
        await self.redis.close()
        await self.neo4j_driver.close()
        await self.living_worlds.close()

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Patient interface API endpoints not yet implemented")
    async def test_patient_interface_integration(self, setup_test_environment, api_base_url):
        """Test patient interface integration with backend services"""
        patient_id = "test_patient_123"

        # Test session creation
        session_data = {
            "patient_id": patient_id,
            "therapeutic_framework": "Narrative",
            "initial_difficulty": 3,
            "goals": ["emotional_regulation", "coping_skills"],
        }

        # Simulate API call to create session
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_base_url}/api/v1/sessions",
                json=session_data,
                headers={"Authorization": "Bearer test_token"},
            ) as response:
                assert response.status == 200
                session_response = await response.json()
                assert session_response["patient_id"] == patient_id
                assert session_response["status"] == "active"
                assert "current_scenario" in session_response

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Living worlds system not fully implemented")
    async def test_living_worlds_integration(self, setup_test_environment):
        """Test Neo4j living worlds system integration"""
        patient_id = "test_patient_123"

        # Create a character in the living world
        character = await self.living_worlds.create_character(
            character_id="char_001",
            name="Dr. Sarah",
            personality_traits={"empathy": 0.9, "wisdom": 0.8, "patience": 0.85},
            background="A compassionate therapist who specializes in narrative therapy",
            therapeutic_role="primary_therapist",
            patient_id=patient_id,
        )

        assert character.id == "char_001"
        assert character.type == "character"
        assert character.properties["name"] == "Dr. Sarah"

        # Create a narrative thread
        narrative = await self.living_worlds.create_narrative_thread(
            thread_id="narrative_001",
            title="Journey of Self-Discovery",
            description="A therapeutic narrative focused on emotional regulation",
            therapeutic_goals=["emotional_regulation", "self_awareness"],
            patient_id=patient_id,
            difficulty_level=3,
        )

        assert narrative.id == "narrative_001"
        assert narrative.type == "narrative_thread"

        # Test relationship creation
        relationship = await self.living_worlds.create_relationship(
            source_id="char_001",
            target_id=patient_id,
            relationship_type="therapeutic_alliance",
            strength=0.7,
            properties={"trust_level": "building", "rapport": "good"},
        )

        assert relationship.relationship_type == "therapeutic_alliance"
        assert relationship.strength == 0.7

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="AI workflow integration not fully implemented")
    async def test_ai_workflow_integration(self, setup_test_environment):
        """Test LangGraph AI workflow integration"""
        patient_id = "test_patient_123"
        session_id = "test_session_456"

        # Test therapeutic conversation workflow
        therapeutic_context = {
            "framework": "CBT",
            "emotional_state": {"valence": -0.3, "arousal": 0.6, "crisis_risk": "low"},
            "current_scenario": "Patient expressing anxiety about work",
            "safety_level": "safe",
        }

        feature_flags = {
            "ai_narrative_enhancement": True,
            "living_worlds_system": True,
            "crisis_support": True,
        }

        # Process patient input through AI workflow
        response = await self.workflow_manager.process_patient_input(
            patient_id=patient_id,
            session_id=session_id,
            user_message="I'm feeling really anxious about my presentation tomorrow",
            therapeutic_context=therapeutic_context,
            feature_flags=feature_flags,
        )

        assert "response" in response
        assert "emotional_state" in response
        assert "safety_level" in response
        assert response["safety_level"] in ["safe", "needs_support", "crisis"]

        # Verify response is therapeutic and appropriate
        assert len(response["response"]) > 0
        assert isinstance(response["emotional_state"], dict)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Clinical dashboard not yet implemented")
    async def test_clinical_dashboard_integration(self, setup_test_environment):
        """Test clinical dashboard real-time monitoring"""
        clinician_id = "clinician_001"

        # Test dashboard data retrieval
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:8002/api/clinical/dashboard/{clinician_id}",
                headers={"Authorization": "Bearer test_token"},
            ) as response:
                assert response.status == 200
                dashboard_data = await response.json()

                assert "patients" in dashboard_data
                assert "alerts" in dashboard_data
                assert "metrics" in dashboard_data
                assert "schedule" in dashboard_data

                # Verify metrics structure
                metrics = dashboard_data["metrics"]
                assert "totalPatients" in metrics
                assert "activePatients" in metrics
                assert "averageEngagement" in metrics
                assert "crisisInterventions" in metrics

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Therapeutic systems integration not fully implemented")
    async def test_therapeutic_systems_integration(self, setup_test_environment):
        """Test integration between therapeutic systems"""
        patient_id = "test_patient_123"
        session_id = "test_session_456"

        # Initialize therapeutic session
        session_config = {
            "session_id": session_id,
            "patient_id": patient_id,
            "therapeutic_framework": "Narrative",
            "initial_difficulty": 3,
            "goals": ["emotional_regulation"],
        }

        await self.therapeutic_system.initialize_session(session_config)

        # Test progress update
        progress_data = {
            "emotional_state": {"valence": 0.2, "arousal": 0.4, "dominance": 0.6},
            "engagement_level": 75,
            "user_choices": [
                {
                    "choice_id": "choice_001",
                    "choice_text": "I want to talk about my feelings",
                    "emotional_impact": 0.3,
                }
            ],
            "session_duration": 1800,  # 30 minutes
        }

        result = await self.therapeutic_system.update_progress(
            session_id=session_id, patient_id=patient_id, progress_data=progress_data
        )

        assert result["status"] == "updated"
        assert "safety_assessment" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Crisis intervention workflow not fully implemented")
    async def test_crisis_intervention_workflow(self, setup_test_environment):
        """Test crisis intervention across all systems"""
        patient_id = "test_patient_123"
        session_id = "test_session_456"

        # Simulate crisis scenario
        crisis_message = "I can't take this anymore, I want to end it all"

        therapeutic_context = {
            "framework": "Crisis",
            "emotional_state": {
                "valence": -0.9,
                "arousal": 0.8,
                "crisis_risk": "crisis",
            },
            "safety_level": "crisis",
        }

        feature_flags = {
            "ai_narrative_enhancement": True,
            "crisis_support": True,
            "emergency_contacts": True,
        }

        # Process through AI workflow
        response = await self.workflow_manager.process_patient_input(
            patient_id=patient_id,
            session_id=session_id,
            user_message=crisis_message,
            therapeutic_context=therapeutic_context,
            feature_flags=feature_flags,
        )

        # Verify crisis response
        assert response["safety_level"] == "crisis"
        assert len(response["interventions_triggered"]) > 0
        assert "crisis" in response["response"].lower()

        # Verify crisis intervention was logged
        intervention = response["interventions_triggered"][0]
        assert intervention["type"] == "crisis_intervention"
        assert "timestamp" in intervention

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Feature flag system not fully implemented")
    async def test_feature_flag_integration(self, setup_test_environment):
        """Test feature flag system across all interfaces"""
        # Test feature flags in patient interface

        # Verify feature flags affect behavior
        patient_id = "test_patient_123"
        session_id = "test_session_456"

        # Test with AI enhancement enabled
        response_with_ai = await self.workflow_manager.process_patient_input(
            patient_id=patient_id,
            session_id=session_id,
            user_message="How are you today?",
            therapeutic_context={"framework": "CBT"},
            feature_flags={"ai_narrative_enhancement": True},
        )

        # Test with AI enhancement disabled
        response_without_ai = await self.workflow_manager.process_patient_input(
            patient_id=patient_id,
            session_id=session_id,
            user_message="How are you today?",
            therapeutic_context={"framework": "CBT"},
            feature_flags={"ai_narrative_enhancement": False},
        )

        # Responses should differ based on feature flags
        assert response_with_ai != response_without_ai

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Microservices communication not fully implemented")
    async def test_microservices_communication(self, setup_test_environment):
        """Test communication between microservices"""
        # Test patient API -> LangGraph service communication
        async with aiohttp.ClientSession() as session:
            # Create session via patient API
            session_data = {
                "patient_id": "test_patient_123",
                "therapeutic_framework": "Narrative",
            }

            async with session.post(
                "http://localhost:8001/api/patient/sessions",
                json=session_data,
                headers={"Authorization": "Bearer test_token"},
            ) as response:
                assert response.status == 200
                session_response = await response.json()
                session_id = session_response["id"]

            # Update progress via patient API (should trigger AI workflow)
            progress_data = {
                "emotional_state": {"valence": 0.5, "arousal": 0.3},
                "engagement_level": 80,
                "user_choices": [],
                "session_duration": 900,
            }

            async with session.patch(
                f"http://localhost:8001/api/patient/sessions/{session_id}/progress",
                json=progress_data,
                headers={"Authorization": "Bearer test_token"},
            ) as response:
                assert response.status == 200
                progress_response = await response.json()
                assert "safety_assessment" in progress_response

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Data consistency testing not fully implemented")
    async def test_data_consistency_across_services(self, setup_test_environment):
        """Test data consistency across Redis, Neo4j, and PostgreSQL"""
        patient_id = "test_patient_123"

        # Create data in Neo4j (living worlds)
        await self.living_worlds.create_character(
            character_id="char_consistency_test",
            name="Test Character",
            personality_traits={"empathy": 0.8},
            background="Test character for consistency",
            therapeutic_role="support",
            patient_id=patient_id,
        )

        # Verify data exists in Neo4j
        world_data = await self.living_worlds.get_patient_world(patient_id)
        assert len(world_data["characters"]) > 0
        assert any(c["id"] == "char_consistency_test" for c in world_data["characters"])

        # Create session data that should be cached in Redis
        session_data = {
            "session_id": "consistency_test_session",
            "patient_id": patient_id,
            "character_interactions": ["char_consistency_test"],
        }

        # Cache in Redis
        await self.redis.setex(
            f"session:{session_data['session_id']}", 3600, json.dumps(session_data)
        )

        # Verify data exists in Redis
        cached_data = await self.redis.get(f"session:{session_data['session_id']}")
        assert cached_data is not None
        cached_session = json.loads(cached_data)
        assert cached_session["patient_id"] == patient_id

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Accessibility features not fully implemented")
    async def test_accessibility_compliance(self, setup_test_environment):
        """Test accessibility features across interfaces"""
        # Test patient interface accessibility
        async with aiohttp.ClientSession() as session:
            # Test high contrast mode endpoint
            async with session.get(
                "http://localhost:3002/api/accessibility/high-contrast",
                headers={"Authorization": "Bearer test_token"},
            ) as response:
                assert response.status == 200
                accessibility_data = await response.json()
                assert "high_contrast_enabled" in accessibility_data

            # Test screen reader compatibility
            async with session.get(
                "http://localhost:3002/api/accessibility/screen-reader",
                headers={"Authorization": "Bearer test_token"},
            ) as response:
                assert response.status == 200
                screen_reader_data = await response.json()
                assert "aria_labels" in screen_reader_data
                assert "semantic_structure" in screen_reader_data

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Performance testing not yet implemented")
    async def test_performance_under_load(self, setup_test_environment):
        """Test system performance under concurrent load"""
        # Simulate multiple concurrent sessions
        tasks = []

        for i in range(10):  # 10 concurrent sessions
            task = self._create_test_session(f"load_test_patient_{i}")
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all sessions were created successfully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 10

        # Verify response times are reasonable (< 5 seconds)
        for result in successful_results:
            assert result["response_time"] < 5.0

    async def _create_test_session(self, patient_id: str) -> dict[str, Any]:
        """Helper method to create a test session"""
        start_time = datetime.utcnow()

        session_data = {
            "patient_id": patient_id,
            "therapeutic_framework": "CBT",
            "initial_difficulty": 3,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/api/patient/sessions",
                json=session_data,
                headers={"Authorization": "Bearer test_token"},
            ) as response:
                result = await response.json()
                end_time = datetime.utcnow()

                result["response_time"] = (end_time - start_time).total_seconds()
                return result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
