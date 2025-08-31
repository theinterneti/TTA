"""
Test fixtures and mock data for integration testing.

This module provides realistic test data and fixtures for comprehensive
testing of the AI Agent Orchestration system.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class TestUser:
    """Test user data structure."""

    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = "test_user"
    email: str = "test@example.com"
    full_name: str = "Test User"
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    preferences: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "preferences": self.preferences,
        }


@dataclass
class TestSession:
    """Test session data structure."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(hours=24)
    )
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for cache storage."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata,
        }


@dataclass
class TestAgent:
    """Test agent data structure."""

    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "test_agent"
    agent_type: str = "conversational"
    status: str = "active"
    capabilities: list[str] = field(default_factory=list)
    configuration: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities,
            "configuration": self.configuration,
            "created_at": self.created_at.isoformat(),
        }


class MockDataGenerator:
    """Generator for realistic mock data."""

    @staticmethod
    def create_test_users(count: int = 5) -> list[TestUser]:
        """Create multiple test users."""
        users = []
        for i in range(count):
            user = TestUser(
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                full_name=f"Test User {i}",
                preferences={
                    "theme": "dark" if i % 2 == 0 else "light",
                    "notifications": True,
                    "language": "en",
                },
            )
            users.append(user)
        return users

    @staticmethod
    def create_test_sessions(
        user_ids: list[str], count_per_user: int = 2
    ) -> list[TestSession]:
        """Create test sessions for users."""
        sessions = []
        for user_id in user_ids:
            for i in range(count_per_user):
                session = TestSession(
                    user_id=user_id,
                    metadata={
                        "ip_address": f"192.168.1.{i + 1}",
                        "user_agent": "Mozilla/5.0 Test Browser",
                        "login_method": "password",
                    },
                )
                sessions.append(session)
        return sessions

    @staticmethod
    def create_test_agents(count: int = 3) -> list[TestAgent]:
        """Create test agents."""
        agents = []
        agent_types = ["conversational", "analytical", "creative"]

        for i in range(count):
            agent = TestAgent(
                name=f"agent_{i}",
                agent_type=agent_types[i % len(agent_types)],
                capabilities=[
                    "text_generation",
                    "conversation",
                    "analysis" if i % 2 == 0 else "creativity",
                ],
                configuration={
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "model": "gpt-3.5-turbo",
                },
            )
            agents.append(agent)
        return agents

    @staticmethod
    def create_conversation_data() -> dict[str, Any]:
        """Create realistic conversation data."""
        return {
            "conversation_id": str(uuid.uuid4()),
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": "Hello, I need help with my project.",
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "role": "assistant",
                    "content": "I'd be happy to help you with your project. What specific area do you need assistance with?",
                    "timestamp": (datetime.now() + timedelta(seconds=2)).isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": "I'm working on a FastAPI application and need to implement authentication.",
                    "timestamp": (datetime.now() + timedelta(seconds=30)).isoformat(),
                },
            ],
            "metadata": {
                "topic": "software_development",
                "complexity": "intermediate",
                "estimated_duration": "15_minutes",
            },
        }

    @staticmethod
    def create_performance_test_data(
        operation_count: int = 100,
    ) -> list[dict[str, Any]]:
        """Create data for performance testing."""
        operations = []
        operation_types = ["create", "read", "update", "delete"]

        for i in range(operation_count):
            operation = {
                "id": str(uuid.uuid4()),
                "type": operation_types[i % len(operation_types)],
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "key": f"test_key_{i}",
                    "value": f"test_value_{i}",
                    "metadata": {"operation_index": i, "batch_id": str(uuid.uuid4())},
                },
            }
            operations.append(operation)

        return operations


class TestScenarios:
    """Predefined test scenarios for integration testing."""

    @staticmethod
    def user_registration_scenario() -> dict[str, Any]:
        """User registration test scenario."""
        user = TestUser(
            username="new_user", email="new_user@example.com", full_name="New User"
        )

        return {
            "scenario": "user_registration",
            "steps": [
                {
                    "action": "create_user",
                    "data": user.to_dict(),
                    "expected_result": "user_created",
                },
                {
                    "action": "verify_user_exists",
                    "data": {"username": user.username},
                    "expected_result": "user_found",
                },
                {
                    "action": "create_session",
                    "data": {"user_id": user.user_id},
                    "expected_result": "session_created",
                },
            ],
            "cleanup": [
                {"action": "delete_session", "data": {"user_id": user.user_id}},
                {"action": "delete_user", "data": {"user_id": user.user_id}},
            ],
        }

    @staticmethod
    def agent_interaction_scenario() -> dict[str, Any]:
        """Agent interaction test scenario."""
        user = TestUser()
        agent = TestAgent()
        conversation = MockDataGenerator.create_conversation_data()

        return {
            "scenario": "agent_interaction",
            "participants": {"user": user.to_dict(), "agent": agent.to_dict()},
            "steps": [
                {
                    "action": "initialize_conversation",
                    "data": conversation,
                    "expected_result": "conversation_started",
                },
                {
                    "action": "process_user_message",
                    "data": conversation["messages"][0],
                    "expected_result": "message_processed",
                },
                {
                    "action": "generate_agent_response",
                    "data": {"context": conversation},
                    "expected_result": "response_generated",
                },
                {
                    "action": "store_conversation_history",
                    "data": conversation,
                    "expected_result": "history_stored",
                },
            ],
            "validation": [
                {
                    "check": "conversation_exists",
                    "data": {"conversation_id": conversation["conversation_id"]},
                },
                {"check": "message_count", "expected": len(conversation["messages"])},
            ],
        }

    @staticmethod
    def system_health_scenario() -> dict[str, Any]:
        """System health monitoring test scenario."""
        return {
            "scenario": "system_health",
            "checks": [
                {
                    "service": "neo4j",
                    "action": "health_check",
                    "expected_result": "healthy",
                },
                {
                    "service": "redis",
                    "action": "health_check",
                    "expected_result": "healthy",
                },
                {
                    "service": "api",
                    "action": "health_check",
                    "expected_result": "healthy",
                },
            ],
            "metrics": ["response_time", "success_rate", "error_rate", "throughput"],
            "thresholds": {
                "max_response_time_ms": 100,
                "min_success_rate": 0.99,
                "max_error_rate": 0.01,
            },
        }

    @staticmethod
    def load_test_scenario(
        concurrent_users: int = 10, duration_seconds: int = 60
    ) -> dict[str, Any]:
        """Load testing scenario."""
        return {
            "scenario": "load_test",
            "parameters": {
                "concurrent_users": concurrent_users,
                "duration_seconds": duration_seconds,
                "ramp_up_seconds": 10,
            },
            "operations": [
                {"name": "user_login", "weight": 30, "endpoint": "/auth/login"},
                {
                    "name": "create_conversation",
                    "weight": 25,
                    "endpoint": "/conversations",
                },
                {
                    "name": "send_message",
                    "weight": 35,
                    "endpoint": "/conversations/{id}/messages",
                },
                {
                    "name": "get_history",
                    "weight": 10,
                    "endpoint": "/conversations/{id}/history",
                },
            ],
            "success_criteria": {
                "max_avg_response_time_ms": 200,
                "min_success_rate": 0.95,
                "max_error_rate": 0.05,
            },
        }


# Convenience functions for test setup
def get_sample_users(count: int = 3) -> list[TestUser]:
    """Get sample users for testing."""
    return MockDataGenerator.create_test_users(count)


def get_sample_agents(count: int = 2) -> list[TestAgent]:
    """Get sample agents for testing."""
    return MockDataGenerator.create_test_agents(count)


def get_sample_conversation() -> dict[str, Any]:
    """Get sample conversation data."""
    return MockDataGenerator.create_conversation_data()


# Export commonly used fixtures
__all__ = [
    "TestUser",
    "TestSession",
    "TestAgent",
    "MockDataGenerator",
    "TestScenarios",
    "get_sample_users",
    "get_sample_agents",
    "get_sample_conversation",
]
