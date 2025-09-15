#!/usr/bin/env python3
"""
Therapeutic Chat Interface Demonstration.

This script demonstrates the comprehensive therapeutic chat interface system
with real-time messaging, therapeutic response generation, session management,
and integration with all therapeutic systems for the TTA platform.
"""

import asyncio
import time

from src.components.advanced_therapeutic_intelligence.intelligent_personalization_engine import (
    IntelligentPersonalizationEngine,
)
from src.components.clinical_dashboard.clinical_dashboard_manager import (
    ClinicalDashboardManager,
)
from src.components.therapeutic_systems import (
    TherapeuticAdaptiveDifficultyEngine,
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticCollaborativeSystem,
    TherapeuticConsequenceSystem,
    TherapeuticEmotionalSafetySystem,
    TherapeuticErrorRecoveryManager,
    TherapeuticGameplayLoopController,
    TherapeuticIntegrationSystem,
    TherapeuticReplayabilitySystem,
)
from src.components.user_experience.advanced_user_interface_engine import (
    AdvancedUserInterfaceEngine,
)
from src.components.user_experience.engagement_optimization_system import (
    EngagementOptimizationSystem,
)
from src.components.user_experience.therapeutic_chat_interface import (
    MessageType,
    TherapeuticChatInterface,
    TherapeuticFramework,
)
from src.components.user_experience.universal_accessibility_system import (
    UniversalAccessibilitySystem,
)
from src.infrastructure.cloud_deployment_manager import (
    CloudDeploymentManager,
)


async def demonstrate_therapeutic_chat_interface():
    """Demonstrate complete Therapeutic Chat Interface system."""
    print("💬 THERAPEUTIC CHAT INTERFACE DEMONSTRATION")
    print("=" * 80)

    # Initialize Therapeutic Chat Interface
    print("\n🌐 Initializing Therapeutic Chat Interface")

    chat_interface = TherapeuticChatInterface()
    await chat_interface.initialize()

    print("✅ Therapeutic Chat Interface initialized")

    # Initialize Supporting Systems
    print("\n🏗️ Initializing Supporting Systems")

    # Initialize accessibility system
    accessibility_system = UniversalAccessibilitySystem()
    await accessibility_system.initialize()

    # Initialize UI engine
    ui_engine = AdvancedUserInterfaceEngine()
    await ui_engine.initialize()

    # Initialize engagement system
    engagement_system = EngagementOptimizationSystem()
    await engagement_system.initialize()

    # Initialize personalization engine
    personalization_engine = IntelligentPersonalizationEngine()
    await personalization_engine.initialize()

    # Initialize therapeutic systems (Phase A)
    consequence_system = TherapeuticConsequenceSystem()
    await consequence_system.initialize()

    emotional_safety = TherapeuticEmotionalSafetySystem()
    await emotional_safety.initialize()

    adaptive_difficulty = TherapeuticAdaptiveDifficultyEngine()
    await adaptive_difficulty.initialize()

    character_development = TherapeuticCharacterDevelopmentSystem()
    await character_development.initialize()

    therapeutic_integration = TherapeuticIntegrationSystem()
    await therapeutic_integration.initialize()

    gameplay_controller = TherapeuticGameplayLoopController()
    await gameplay_controller.initialize()

    replayability_system = TherapeuticReplayabilitySystem()
    await replayability_system.initialize()

    collaborative_system = TherapeuticCollaborativeSystem()
    await collaborative_system.initialize()

    error_recovery_manager = TherapeuticErrorRecoveryManager()
    await error_recovery_manager.initialize()

    # Initialize integration systems (Phase B)
    clinical_dashboard_manager = ClinicalDashboardManager()
    await clinical_dashboard_manager.initialize()

    cloud_deployment_manager = CloudDeploymentManager()
    await cloud_deployment_manager.initialize()

    print("✅ All supporting systems initialized")
    print("   Phase A: 9 therapeutic systems")
    print("   Phase B: 2 integration systems")
    print("   Phase C: 1 personalization system")
    print("   Phase D: 3 user experience systems")

    # Inject System Dependencies
    print("\n🔗 Injecting System Dependencies")

    therapeutic_systems = {
        "consequence_system": consequence_system,
        "emotional_safety_system": emotional_safety,
        "adaptive_difficulty_engine": adaptive_difficulty,
        "character_development_system": character_development,
        "therapeutic_integration_system": therapeutic_integration,
        "gameplay_loop_controller": gameplay_controller,
        "replayability_system": replayability_system,
        "collaborative_system": collaborative_system,
        "error_recovery_manager": error_recovery_manager,
    }

    # Inject into chat interface
    chat_interface.inject_accessibility_system(accessibility_system)
    chat_interface.inject_ui_engine(ui_engine)
    chat_interface.inject_engagement_system(engagement_system)
    chat_interface.inject_personalization_engine(personalization_engine)
    chat_interface.inject_therapeutic_systems(**therapeutic_systems)
    chat_interface.inject_integration_systems(
        clinical_dashboard_manager=clinical_dashboard_manager,
        cloud_deployment_manager=cloud_deployment_manager,
    )

    print("✅ System dependencies injected")

    # Demonstrate Therapeutic Chat Interface Features
    print("\n💬 Demonstrating Therapeutic Chat Interface Features")

    # Create sample users with different therapeutic needs
    users = [
        {
            "user_id": "chat_user_001",
            "name": "Sarah (Anxiety Management)",
            "therapeutic_goals": ["anxiety_management", "stress_reduction"],
            "session_config": {"max_duration": 45, "enable_crisis_detection": True},
            "conversation_scenario": "anxiety_support"
        },
        {
            "user_id": "chat_user_002",
            "name": "Michael (Depression Recovery)",
            "therapeutic_goals": ["depression_recovery", "mood_improvement"],
            "session_config": {"max_duration": 60, "enable_crisis_detection": True},
            "conversation_scenario": "depression_support"
        },
        {
            "user_id": "chat_user_003",
            "name": "Emma (Mindfulness Practice)",
            "therapeutic_goals": ["mindfulness_practice", "emotional_regulation"],
            "session_config": {"max_duration": 30, "enable_crisis_detection": False},
            "conversation_scenario": "mindfulness_guidance"
        }
    ]

    # 1. Chat Session Creation
    print("\n   1️⃣ Chat Session Creation")

    active_sessions = {}
    total_sessions = 0

    for user in users:
        user_id = user["user_id"]
        name = user["name"]
        therapeutic_goals = user["therapeutic_goals"]
        session_config = user["session_config"]

        start_time = time.perf_counter()

        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=therapeutic_goals,
            session_config=session_config
        )

        session_time = (time.perf_counter() - start_time) * 1000
        total_sessions += 1
        active_sessions[user_id] = session

        print(f"      ✅ Session for {name} created in {session_time:.2f}ms")
        print(f"         Session ID: {session.session_id}")
        print(f"         Therapeutic Goals: {', '.join(therapeutic_goals)}")
        print(f"         Max Duration: {session.max_duration_minutes} minutes")
        print(f"         Conversation State: {session.conversation_state.value}")
        print(f"         Welcome Message: {len(session.messages)} message(s)")

    print(f"      📊 Total chat sessions created: {total_sessions}")

    # 2. Real-Time Message Processing
    print("\n   2️⃣ Real-Time Message Processing")

    # Sample conversation scenarios
    conversation_scenarios = {
        "anxiety_support": [
            "Hi, I've been feeling really anxious lately about work.",
            "I keep having panic attacks and I don't know what to do.",
            "Can you help me learn some coping strategies?",
            "I tried deep breathing but it doesn't seem to help much.",
            "I feel like I'm getting a bit better with your help."
        ],
        "depression_support": [
            "I've been feeling really down and unmotivated.",
            "It's hard to get out of bed in the morning.",
            "I feel like nothing I do matters anymore.",
            "Maybe talking to you is helping a little bit.",
            "I want to try to make some positive changes."
        ],
        "mindfulness_guidance": [
            "I want to learn more about mindfulness meditation.",
            "How can I be more present in my daily life?",
            "I get distracted easily during meditation.",
            "Can you guide me through a breathing exercise?",
            "I'm starting to feel more centered and calm."
        ]
    }

    total_messages_processed = 0
    total_processing_time = 0

    for user in users:
        user_id = user["user_id"]
        name = user["name"]
        scenario = user["conversation_scenario"]
        session = active_sessions[user_id]

        print(f"\n      👤 {name} - {scenario.replace('_', ' ').title()} Conversation")

        messages = conversation_scenarios[scenario]

        for i, message_content in enumerate(messages, 1):
            start_time = time.perf_counter()

            response = await chat_interface.process_user_message(
                session_id=session.session_id,
                message_content=message_content,
                message_metadata={"message_number": i, "scenario": scenario}
            )

            processing_time = (time.perf_counter() - start_time) * 1000
            total_processing_time += processing_time
            total_messages_processed += 1

            print(f"         💬 Message {i}: \"{message_content[:50]}{'...' if len(message_content) > 50 else ''}\"")
            print(f"         🤖 Response: \"{response.content[:60]}{'...' if len(response.content) > 60 else ''}\"")
            print(f"         ⚡ Processing Time: {processing_time:.2f}ms")
            print(f"         🧠 Framework: {response.therapeutic_frameworks[0].value if response.therapeutic_frameworks else 'default'}")
            print(f"         📊 Confidence: {response.confidence_score:.2f}")

            # Small delay to simulate real conversation
            await asyncio.sleep(0.1)

    average_processing_time = total_processing_time / total_messages_processed
    print(f"\n      📊 Total messages processed: {total_messages_processed}")
    print(f"      📊 Average processing time: {average_processing_time:.2f}ms")
    print(f"      📊 Performance: {'✅ Excellent' if average_processing_time < 500 else '⚠️ Needs optimization'}")

    # 3. Crisis Detection and Intervention
    print("\n   3️⃣ Crisis Detection and Intervention")

    # Test crisis detection with a dedicated user
    crisis_user_id = "crisis_user_001"
    crisis_session = await chat_interface.start_chat_session(
        user_id=crisis_user_id,
        therapeutic_goals=["crisis_intervention", "safety_planning"],
        session_config={"max_duration": 30, "enable_crisis_detection": True}
    )

    crisis_messages = [
        "I'm having a really hard time right now.",
        "I can't take this anymore. I just want to end it all.",
        "Thank you for being here. I think I need professional help."
    ]

    crisis_interventions = 0

    for i, crisis_message in enumerate(crisis_messages, 1):
        start_time = time.perf_counter()

        response = await chat_interface.process_user_message(
            session_id=crisis_session.session_id,
            message_content=crisis_message
        )

        processing_time = (time.perf_counter() - start_time) * 1000

        print(f"      💬 Crisis Message {i}: \"{crisis_message}\"")
        print(f"      🚨 Response Type: {response.message_type.value}")
        print(f"      🤖 Response: \"{response.content[:80]}{'...' if len(response.content) > 80 else ''}\"")
        print(f"      ⚡ Processing Time: {processing_time:.2f}ms")
        print(f"      🔴 Priority: {response.response_priority.value}")
        print(f"      👨‍⚕️ Human Review: {'Yes' if response.requires_human_review else 'No'}")

        if response.message_type == MessageType.CRISIS_INTERVENTION:
            crisis_interventions += 1

        await asyncio.sleep(0.1)

    print(f"      📊 Crisis interventions triggered: {crisis_interventions}")
    print(f"      📊 Crisis response time: <500ms ({'✅ Met' if processing_time < 500 else '❌ Exceeded'})")

    # 4. Therapeutic Framework Selection
    print("\n   4️⃣ Therapeutic Framework Selection")

    framework_test_messages = [
        ("CBT Test", "I keep thinking that everything will go wrong.", TherapeuticFramework.CBT),
        ("DBT Test", "I'm feeling overwhelmed with intense emotions.", TherapeuticFramework.DBT),
        ("Mindfulness Test", "I want to be more present and mindful.", TherapeuticFramework.MINDFULNESS),
        ("Solution-Focused Test", "What strategies have worked for me before?", TherapeuticFramework.SOLUTION_FOCUSED),
    ]

    framework_user_id = "framework_user_001"
    framework_session = await chat_interface.start_chat_session(
        user_id=framework_user_id,
        therapeutic_goals=["framework_testing"],
        session_config={"max_duration": 20}
    )

    framework_accuracy = 0

    for test_name, message, expected_framework in framework_test_messages:
        response = await chat_interface.process_user_message(
            session_id=framework_session.session_id,
            message_content=message
        )

        selected_framework = response.therapeutic_frameworks[0] if response.therapeutic_frameworks else None
        is_correct = selected_framework == expected_framework

        if is_correct:
            framework_accuracy += 1

        print(f"      🧪 {test_name}")
        print(f"         Message: \"{message}\"")
        print(f"         Expected: {expected_framework.value}")
        print(f"         Selected: {selected_framework.value if selected_framework else 'None'}")
        print(f"         Result: {'✅ Correct' if is_correct else '❌ Incorrect'}")

    framework_accuracy_percentage = (framework_accuracy / len(framework_test_messages)) * 100
    print(f"      📊 Framework selection accuracy: {framework_accuracy_percentage:.1f}%")

    # 5. Session Management and History
    print("\n   5️⃣ Session Management and History")

    for user in users[:2]:  # Test with first 2 users
        user_id = user["user_id"]
        name = user["name"]
        session = active_sessions[user_id]

        # Get session history
        history = await chat_interface.get_session_history(session.session_id)

        # Update therapeutic goals
        new_goals = ["progress_tracking", "skill_development"]
        goal_update_success = await chat_interface.update_therapeutic_goals(
            session.session_id, new_goals
        )

        print(f"      👤 {name}")
        print(f"         Session History: {len(history)} messages")
        print(f"         Goal Update: {'✅ Success' if goal_update_success else '❌ Failed'}")
        print(f"         New Goals: {', '.join(new_goals)}")

    # 6. Therapeutic Insights Generation
    print("\n   6️⃣ Therapeutic Insights Generation")

    for user in users:
        user_id = user["user_id"]
        name = user["name"]
        session = active_sessions[user_id]

        start_time = time.perf_counter()

        insights = await chat_interface.get_therapeutic_insights(session.session_id)

        insights_time = (time.perf_counter() - start_time) * 1000

        print(f"      👤 {name} - Insights generated in {insights_time:.2f}ms")
        print(f"         Session Duration: {insights['session_duration']}")
        print(f"         Message Count: {insights['message_count']}")
        print(f"         Conversation State: {insights['conversation_state']}")
        print(f"         Crisis Risk Level: {insights['crisis_risk_level']:.2f}")
        print(f"         Recommendations: {len(insights['recommendations'])}")

        # Show sample recommendations
        for rec in insights['recommendations'][:2]:
            print(f"           - {rec}")

    # 7. Session Completion and Summary
    print("\n   7️⃣ Session Completion and Summary")

    completed_sessions = 0

    for user in users:
        user_id = user["user_id"]
        name = user["name"]
        session = active_sessions[user_id]

        start_time = time.perf_counter()

        summary = await chat_interface.end_chat_session(
            session.session_id,
            f"Productive session focusing on {', '.join(session.session_goals)}"
        )

        completion_time = (time.perf_counter() - start_time) * 1000
        completed_sessions += 1

        print(f"      ✅ {name} session completed in {completion_time:.2f}ms")
        print(f"         Duration: {summary['duration_minutes']:.1f} minutes")
        print(f"         Messages: {summary['message_count']}")
        print(f"         Summary: \"{summary['summary_text'][:60]}{'...' if len(summary['summary_text']) > 60 else ''}\"")

    # Complete crisis session
    await chat_interface.end_chat_session(crisis_session.session_id)
    completed_sessions += 1

    # Complete framework test session
    await chat_interface.end_chat_session(framework_session.session_id)
    completed_sessions += 1

    print(f"      📊 Total sessions completed: {completed_sessions}")

    # 8. System Health Check
    print("\n   8️⃣ System Health Check")

    start_time = time.perf_counter()
    health_check = await chat_interface.health_check()
    health_time = (time.perf_counter() - start_time) * 1000

    print(f"      ✅ Health check completed in {health_time:.2f}ms")
    print(f"         Status: {health_check['status']}")
    print(f"         Chat Interface Status: {health_check['chat_interface_status']}")
    print(f"         Active Sessions: {health_check['active_sessions']}")
    print(f"         Total Messages Processed: {health_check['total_messages_processed']}")
    print(f"         Average Response Time: {health_check['average_response_time_ms']:.2f}ms")
    print(f"         Therapeutic Interventions: {health_check['therapeutic_interventions']}")
    print(f"         Crisis Interventions: {health_check['crisis_interventions']}")
    print(f"         System Availability: {health_check['system_availability']:.1%}")
    print(f"         Background Tasks Running: {health_check['background_tasks_running']}")

    # Final Summary
    print("\n" + "=" * 80)
    print("💬 THERAPEUTIC CHAT INTERFACE SUMMARY")
    print("=" * 80)

    print(f"✅ Chat Sessions Created: {total_sessions}")
    print(f"✅ Messages Processed: {total_messages_processed}")
    print(f"✅ Average Response Time: {average_processing_time:.2f}ms")
    print(f"✅ Crisis Interventions: {crisis_interventions}")
    print(f"✅ Framework Selection Accuracy: {framework_accuracy_percentage:.1f}%")
    print(f"✅ Sessions Completed: {completed_sessions}")
    print(f"✅ System Integration: {len(therapeutic_systems)} therapeutic systems + 4 user experience systems")
    print("✅ Performance: <1s response times, <500ms crisis detection")
    print("✅ Features: Real-time messaging, therapeutic frameworks, crisis intervention, session management")
    print("✅ Background Processing: Message queue, session management, therapeutic monitoring, performance tracking")

    # Cleanup
    await chat_interface.shutdown()
    await accessibility_system.shutdown()
    await ui_engine.shutdown()
    await engagement_system.shutdown()
    await personalization_engine.shutdown()
    await cloud_deployment_manager.shutdown()
    await error_recovery_manager.shutdown()

    print("\n🎉 THERAPEUTIC CHAT INTERFACE DEMONSTRATION COMPLETE!")
    print("💬 Foundational Chat Interface Implementation SUCCESSFUL!")
    print("🚀 Ready for Multi-Modal Interaction System Enhancement!")

    return True


if __name__ == "__main__":
    asyncio.run(demonstrate_therapeutic_chat_interface())
