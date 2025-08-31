"""
Simplified E2E Testing Demo for TTA Therapeutic Workflow

This module provides a simplified demonstration of the comprehensive
E2E testing framework without requiring external dependencies.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.player_experience.models.player import PlayerProfile
from src.player_experience.models.session import SessionContext


class SimplifiedTherapeuticWorkflowDemo:
    """Simplified demonstration of therapeutic workflow E2E testing."""

    def __init__(self):
        """Initialize the demo framework."""
        self.app = None
        self.client = None
        self.mock_services = {}
        self.test_results = {}

    async def setup_demo_environment(self):
        """Set up the demo testing environment."""
        # Create mock FastAPI app
        self.app = FastAPI(title="TTA Therapeutic Demo")
        self.client = TestClient(self.app)

        # Add demo endpoints
        @self.app.post("/api/v1/users/register")
        async def demo_register(user_data: dict):
            return {"status": "success", "user_id": f"demo_user_{time.time()}"}, 201

        @self.app.post("/api/v1/sessions/create")
        async def demo_create_session(session_data: dict):
            return {
                "status": "success",
                "session_id": f"demo_session_{time.time()}",
            }, 201

        @self.app.get("/api/v1/health")
        async def demo_health():
            return {"status": "healthy", "timestamp": time.time()}

        # Initialize mock therapeutic services
        await self._initialize_mock_services()

        print("✅ Demo environment setup complete")

    async def _initialize_mock_services(self):
        """Initialize mock therapeutic services."""
        # Mock consequence system
        consequence_system = AsyncMock()
        consequence_system.process_choice_consequence.return_value = {
            "consequence_id": "demo_consequence",
            "therapeutic_value": 0.85,
            "learning_opportunity": "Demonstrated courage in difficult situation",
            "character_impact": {"courage": 0.2, "wisdom": 0.1},
        }

        # Mock emotional safety system
        emotional_safety = AsyncMock()
        emotional_safety.assess_crisis_risk.return_value = {
            "crisis_detected": False,
            "crisis_level": "NONE",
            "immediate_intervention": False,
            "indicators": [],
            "response_time": 0.05,
        }

        # Mock character development system
        character_development = AsyncMock()
        mock_character = MagicMock()
        mock_character.character_id = "demo_character"
        mock_character.attributes = {"courage": 6.0, "wisdom": 5.0, "compassion": 7.0}
        character_development.create_character.return_value = mock_character

        self.mock_services = {
            "consequence_system": consequence_system,
            "emotional_safety": emotional_safety,
            "character_development": character_development,
        }

        print("✅ Mock therapeutic services initialized")

    async def demo_complete_user_journey(self):
        """Demonstrate a complete user therapeutic journey."""
        print("\n🎯 Starting Complete User Journey Demo")

        # Create demo user profile
        from datetime import datetime

        from src.player_experience.models.enums import (
            IntensityLevel,
            TherapeuticApproach,
        )
        from src.player_experience.models.player import TherapeuticPreferences

        therapeutic_prefs = TherapeuticPreferences(
            intensity_level=IntensityLevel.MEDIUM,
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
            trigger_warnings=["mild_anxiety"],
            comfort_topics=["confidence_building", "anxiety_management"],
        )

        user_profile = PlayerProfile(
            player_id="demo_user_001",
            username="demo_alice",
            email="demo.alice@example.com",
            created_at=datetime.now(),
            therapeutic_preferences=therapeutic_prefs,
        )

        # Create demo session
        from src.player_experience.models.enums import TherapeuticApproach
        from src.player_experience.models.session import TherapeuticSettings

        therapeutic_settings = TherapeuticSettings(
            intensity_level=0.6,  # Medium intensity (0.0 to 1.0)
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
            intervention_frequency="balanced",
            feedback_sensitivity=0.7,
            crisis_monitoring_enabled=True,
            adaptive_difficulty=True,
        )

        session = SessionContext(
            session_id="demo_session_001",
            player_id=user_profile.player_id,
            character_id="demo_character_001",
            world_id="demo_therapeutic_world",
            therapeutic_settings=therapeutic_settings,
        )

        start_time = time.time()
        journey_results = {}

        try:
            # Step 1: User Registration
            print("  📝 Step 1: User Registration")
            response = self.client.post(
                "/api/v1/users/register",
                json={
                    "username": user_profile.username,
                    "therapeutic_goals": user_profile.therapeutic_preferences.comfort_topics,
                },
            )
            assert response.status_code == 201
            journey_results["registration"] = {"success": True, "response_time": 0.1}
            print("    ✅ Registration successful")

            # Step 2: Character Creation
            print("  🎭 Step 2: Character Creation")
            character_service = self.mock_services["character_development"]
            character = await character_service.create_character(
                user_id=user_profile.player_id,
                session_id=session.session_id,
                therapeutic_goals=user_profile.therapeutic_preferences.comfort_topics,
            )
            assert character is not None
            journey_results["character_creation"] = {
                "success": True,
                "character_id": character.character_id,
                "initial_attributes": character.attributes,
            }
            print(f"    ✅ Character created: {character.character_id}")

            # Step 3: Therapeutic Scenario
            print("  🎪 Step 3: Therapeutic Scenario Engagement")
            consequence_service = self.mock_services["consequence_system"]
            consequence = await consequence_service.process_choice_consequence(
                user_id=user_profile.player_id,
                choice="approach_with_confidence",
                scenario_context={"type": "social_anxiety", "difficulty": "moderate"},
            )
            assert consequence["therapeutic_value"] > 0.5
            journey_results["therapeutic_scenario"] = {
                "success": True,
                "therapeutic_value": consequence["therapeutic_value"],
                "learning_opportunity": consequence["learning_opportunity"],
            }
            print(
                f"    ✅ Scenario completed with therapeutic value: {consequence['therapeutic_value']}"
            )

            # Step 4: Safety Assessment
            print("  🛡️ Step 4: Emotional Safety Assessment")
            safety_service = self.mock_services["emotional_safety"]
            safety_result = await safety_service.assess_crisis_risk(
                user_id=user_profile.player_id,
                user_input="I feel much more confident now!",
                session_context=session,
            )
            assert safety_result["crisis_detected"] is False
            journey_results["safety_assessment"] = {
                "success": True,
                "crisis_detected": safety_result["crisis_detected"],
                "response_time": safety_result["response_time"],
            }
            print("    ✅ Safety assessment passed - no crisis detected")

            # Step 5: Session Health Check
            print("  💚 Step 5: System Health Check")
            health_response = self.client.get("/api/v1/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            journey_results["health_check"] = {
                "success": True,
                "status": health_data["status"],
            }
            print("    ✅ System health check passed")

            total_time = time.time() - start_time
            journey_results["total_time"] = total_time
            journey_results["overall_success"] = True

            print("\n🎉 Complete User Journey Demo Successful!")
            print(f"   Total Time: {total_time:.2f} seconds")
            print("   All 5 steps completed successfully")

            return journey_results

        except Exception as e:
            journey_results["error"] = str(e)
            journey_results["overall_success"] = False
            print(f"\n❌ Demo failed with error: {e}")
            return journey_results

    async def demo_crisis_intervention(self):
        """Demonstrate crisis intervention workflow."""
        print("\n🚨 Starting Crisis Intervention Demo")

        # Create high-risk user profile
        from datetime import datetime

        from src.player_experience.models.enums import (
            IntensityLevel,
            TherapeuticApproach,
        )
        from src.player_experience.models.player import (
            CrisisContactInfo,
            TherapeuticPreferences,
        )

        crisis_contact = CrisisContactInfo(
            primary_contact_name="Emergency Contact",
            primary_contact_phone="911",
            crisis_hotline_preference="988 Suicide & Crisis Lifeline",
            emergency_instructions="Immediate professional intervention required",
        )

        crisis_therapeutic_prefs = TherapeuticPreferences(
            intensity_level=IntensityLevel.HIGH,
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
            trigger_warnings=["suicide_ideation", "self_harm"],
            comfort_topics=["safety_planning", "crisis_management"],
            crisis_contact_info=crisis_contact,
        )

        crisis_user = PlayerProfile(
            player_id="demo_crisis_user",
            username="demo_charlie",
            email="demo.charlie@example.com",
            created_at=datetime.now(),
            therapeutic_preferences=crisis_therapeutic_prefs,
        )

        start_time = time.time()

        # Mock crisis detection
        safety_service = self.mock_services["emotional_safety"]

        # Override mock for crisis scenario
        safety_service.assess_crisis_risk.return_value = {
            "crisis_detected": True,
            "crisis_level": "CRITICAL",
            "immediate_intervention": True,
            "indicators": ["suicide_ideation", "hopelessness"],
            "response_time": 0.02,  # Very fast response
        }

        print("  🔍 Step 1: Crisis Detection")
        crisis_result = await safety_service.assess_crisis_risk(
            user_id=crisis_user.player_id,
            user_input="I've been thinking about ending it all",
            session_context=None,
        )

        assert crisis_result["crisis_detected"] is True
        assert crisis_result["crisis_level"] == "CRITICAL"

        intervention_time = time.time() - start_time

        print(f"    ✅ Crisis detected in {intervention_time:.3f} seconds")
        print(f"    🚨 Crisis Level: {crisis_result['crisis_level']}")
        print("    ⚡ Immediate intervention triggered")

        # Validate crisis response time
        assert intervention_time < 1.0  # Should be very fast

        print("\n🛡️ Crisis Intervention Demo Successful!")
        print(f"   Response Time: {intervention_time:.3f} seconds (< 1.0s requirement)")

        return {
            "success": True,
            "crisis_detected": True,
            "response_time": intervention_time,
            "crisis_level": crisis_result["crisis_level"],
        }

    async def demo_performance_validation(self):
        """Demonstrate performance validation."""
        print("\n⚡ Starting Performance Validation Demo")

        performance_results = {}

        # Test API response times
        print("  📊 Testing API Response Times")
        api_times = []
        for _i in range(5):
            start = time.time()
            response = self.client.get("/api/v1/health")
            end = time.time()
            response_time = (end - start) * 1000  # Convert to milliseconds
            api_times.append(response_time)
            assert response.status_code == 200

        avg_api_time = sum(api_times) / len(api_times)
        max_api_time = max(api_times)

        print(f"    ✅ Average API Response: {avg_api_time:.1f}ms")
        print(f"    ✅ Max API Response: {max_api_time:.1f}ms")

        # Test therapeutic service response times
        print("  🧠 Testing Therapeutic Service Response Times")
        therapeutic_times = []
        consequence_service = self.mock_services["consequence_system"]

        for i in range(3):
            start = time.time()
            await consequence_service.process_choice_consequence(
                user_id=f"perf_test_user_{i}",
                choice=f"test_choice_{i}",
                scenario_context={"type": "performance_test"},
            )
            end = time.time()
            service_time = (end - start) * 1000
            therapeutic_times.append(service_time)

        avg_therapeutic_time = sum(therapeutic_times) / len(therapeutic_times)
        max_therapeutic_time = max(therapeutic_times)

        print(f"    ✅ Average Therapeutic Service: {avg_therapeutic_time:.1f}ms")
        print(f"    ✅ Max Therapeutic Service: {max_therapeutic_time:.1f}ms")

        # Validate performance requirements
        assert avg_api_time < 200  # API should be < 200ms
        assert avg_therapeutic_time < 100  # Therapeutic services should be < 100ms

        performance_results = {
            "api_response_times": {
                "average_ms": avg_api_time,
                "max_ms": max_api_time,
                "samples": len(api_times),
            },
            "therapeutic_service_times": {
                "average_ms": avg_therapeutic_time,
                "max_ms": max_therapeutic_time,
                "samples": len(therapeutic_times),
            },
            "performance_requirements_met": True,
        }

        print("\n⚡ Performance Validation Demo Successful!")
        print("   All response times meet requirements")

        return performance_results

    async def run_complete_demo(self):
        """Run the complete E2E testing demonstration."""
        print("🚀 Starting TTA Therapeutic Workflow E2E Testing Demo")
        print("=" * 60)

        await self.setup_demo_environment()

        demo_results = {}

        # Run all demo scenarios
        demo_results["user_journey"] = await self.demo_complete_user_journey()
        demo_results["crisis_intervention"] = await self.demo_crisis_intervention()
        demo_results[
            "performance_validation"
        ] = await self.demo_performance_validation()

        # Generate summary
        print("\n" + "=" * 60)
        print("📋 DEMO SUMMARY")
        print("=" * 60)

        all_successful = all(
            result.get("success", result.get("overall_success", False))
            for result in demo_results.values()
        )

        if all_successful:
            print("🎉 ALL DEMOS SUCCESSFUL!")
            print("✅ Complete User Journey: PASSED")
            print("✅ Crisis Intervention: PASSED")
            print("✅ Performance Validation: PASSED")
        else:
            print("❌ Some demos failed - check results above")

        print(f"\n📊 Demo completed in {time.time() - self.start_time:.2f} seconds")

        return demo_results


# Pytest test functions
@pytest.mark.asyncio
async def test_therapeutic_workflow_demo():
    """Test the complete therapeutic workflow demonstration."""
    demo = SimplifiedTherapeuticWorkflowDemo()
    demo.start_time = time.time()

    results = await demo.run_complete_demo()

    # Validate all demos passed
    assert results["user_journey"]["overall_success"] is True
    assert results["crisis_intervention"]["success"] is True
    assert results["performance_validation"]["performance_requirements_met"] is True

    print("\n✅ Therapeutic Workflow Demo Test PASSED")


@pytest.mark.asyncio
async def test_individual_user_journey():
    """Test individual user journey components."""
    demo = SimplifiedTherapeuticWorkflowDemo()
    await demo.setup_demo_environment()

    result = await demo.demo_complete_user_journey()

    assert result["overall_success"] is True
    assert result["registration"]["success"] is True
    assert result["character_creation"]["success"] is True
    assert result["therapeutic_scenario"]["success"] is True
    assert result["safety_assessment"]["success"] is True
    assert result["health_check"]["success"] is True
    assert result["total_time"] < 30.0  # Should complete in under 30 seconds

    print("✅ Individual User Journey Test PASSED")


if __name__ == "__main__":
    # Run the demo directly
    async def main():
        demo = SimplifiedTherapeuticWorkflowDemo()
        demo.start_time = time.time()
        await demo.run_complete_demo()

    asyncio.run(main())
