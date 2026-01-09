"""

# Logseq: [[TTA.dev/Tests/Integration/Test_progress_tracking_integration]]
Integration tests for progress tracking and analytics system.

Tests the complete progress tracking workflow including:
- Progress visualization data generation
- Therapeutic metrics calculation
- Milestone detection
- Progress summary computation
- Integration with session data
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.player_experience.api.app import app
from src.player_experience.database.session_repository import SessionRepository
from src.player_experience.managers.progress_tracking_service import (
    ProgressTrackingService,
)
from src.player_experience.models.enums import (
    ProgressMarkerType,
    SessionStatus,
    TherapeuticApproach,
)
from src.player_experience.models.session import (
    ProgressMarker,
    SessionContext,
    TherapeuticSettings,
)


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers(test_client):
    """Get authentication headers for API requests."""
    import uuid

    # Use unique username to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    username = f"progress_test_{unique_id}"

    # Register and login a test user
    register_response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "TestPassword123!",
        },
    )
    assert register_response.status_code in [200, 201]

    login_response = test_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def session_repository():
    """Create a session repository for testing."""
    return SessionRepository()


@pytest.fixture
def progress_service(session_repository):
    """Create a progress tracking service for testing."""
    return ProgressTrackingService(session_repository)


@pytest.fixture
async def sample_sessions(session_repository):
    """Create sample session data for testing."""
    player_id = "test_player_progress"
    sessions = []

    # Create 5 sessions with varying progress markers
    for i in range(5):
        session = SessionContext(
            session_id=f"session_{i}",
            player_id=player_id,
            character_id=f"char_{i}",
            world_id="world_mindfulness_garden",
            status=SessionStatus.ACTIVE if i == 4 else SessionStatus.COMPLETED,
            therapeutic_settings=TherapeuticSettings(
                preferred_approaches=[
                    TherapeuticApproach.MINDFULNESS,
                    TherapeuticApproach.CBT,
                ],
                intensity_level=0.5,
                intervention_frequency="balanced",
            ),
            created_at=datetime.utcnow() - timedelta(days=10 - i * 2),
            last_interaction=datetime.utcnow() - timedelta(days=10 - i * 2),
            total_duration_minutes=30 + i * 10,
            interaction_count=10 + i * 5,
            progress_markers=[
                ProgressMarker(
                    marker_id=f"marker_skill_{i}",
                    marker_type=ProgressMarkerType.SKILL_ACQUIRED,
                    description=f"Learned skill {i}",
                    therapeutic_value=0.8,
                    achieved_at=datetime.utcnow() - timedelta(days=10 - i * 2),
                ),
                ProgressMarker(
                    marker_id=f"marker_goal_{i}",
                    marker_type=ProgressMarkerType.THERAPEUTIC_GOAL,
                    description=f"Met goal {i}",
                    therapeutic_value=1.0,
                    achieved_at=datetime.utcnow() - timedelta(days=10 - i * 2),
                ),
            ],
        )
        await session_repository.create_session(session)
        sessions.append(session)

    return sessions


class TestProgressVisualization:
    """Tests for progress visualization endpoints."""

    @pytest.mark.asyncio
    async def test_get_progress_viz_requires_authentication(self, test_client):
        """Test that progress visualization requires authentication."""
        response = test_client.get("/api/v1/players/test_player/progress/viz")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_progress_viz_with_authentication(
        self, test_client, auth_headers, sample_sessions
    ):
        """Test getting progress visualization data with valid authentication."""
        response = test_client.get(
            "/api/v1/players/test_player_progress/progress/viz?days=14",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = response.json()
        assert "time_buckets" in data
        assert "series" in data
        assert "meta" in data

        # Verify time buckets are present
        assert isinstance(data["time_buckets"], list)

        # Verify series data structure
        assert isinstance(data["series"], list)

    @pytest.mark.asyncio
    async def test_progress_viz_with_different_timeframes(
        self, test_client, auth_headers, sample_sessions
    ):
        """Test progress visualization with different time ranges."""
        for days in [7, 14, 30, 60]:
            response = test_client.get(
                f"/api/v1/players/test_player_progress/progress/viz?days={days}",
                headers=auth_headers,
            )
            assert response.status_code == 200

            data = response.json()
            assert "time_buckets" in data
            assert "series" in data


class TestProgressSummary:
    """Tests for progress summary computation."""

    @pytest.mark.asyncio
    async def test_compute_progress_summary(self, progress_service, sample_sessions):
        """Test computing comprehensive progress summary."""
        summary = await progress_service.compute_progress_summary(
            "test_player_progress", summaries_limit=30
        )

        # Verify engagement metrics
        assert summary.engagement_metrics is not None
        assert summary.engagement_metrics.total_sessions >= 5
        assert summary.engagement_metrics.total_time_minutes > 0

        # Verify milestones
        assert isinstance(summary.milestones_achieved, list)
        assert isinstance(summary.active_milestones, list)

        # Verify highlights
        assert isinstance(summary.recent_highlights, list)

    @pytest.mark.asyncio
    async def test_milestone_detection(self, progress_service, sample_sessions):
        """Test milestone detection based on progress markers."""
        summary = await progress_service.compute_progress_summary(
            "test_player_progress"
        )

        # Should detect milestones for session count
        milestone_types = [m.milestone_type for m in summary.milestones_achieved]
        assert len(milestone_types) > 0

        # Verify milestone structure
        for milestone in summary.milestones_achieved:
            assert milestone.milestone_id is not None
            assert milestone.milestone_type is not None
            assert milestone.title is not None
            assert milestone.achieved_at is not None

    @pytest.mark.asyncio
    async def test_therapeutic_metrics_calculation(
        self, progress_service, sample_sessions
    ):
        """Test calculation of therapeutic effectiveness metrics."""
        report = await progress_service.compute_therapeutic_effectiveness(
            "test_player_progress"
        )

        # Verify report structure
        assert report.player_id == "test_player_progress"
        assert report.overall_effectiveness_score >= 0.0
        assert report.overall_effectiveness_score <= 1.0

        # Verify therapeutic metrics
        assert isinstance(report.therapeutic_metrics, list)
        assert len(report.therapeutic_metrics) > 0

        # Verify each metric has required fields
        for metric in report.therapeutic_metrics:
            assert metric.metric_name is not None
            assert metric.value >= 0.0
            assert metric.measured_at is not None


class TestProgressInsights:
    """Tests for progress insights and recommendations."""

    @pytest.mark.asyncio
    async def test_progress_trend_analysis(self, progress_service, sample_sessions):
        """Test progress trend analysis."""
        summary = await progress_service.compute_progress_summary(
            "test_player_progress"
        )

        # Verify trend analysis
        assert summary.progress_trend in ["improving", "stable", "declining", "unknown"]
        assert summary.engagement_trend in [
            "increasing",
            "stable",
            "decreasing",
            "unknown",
        ]

    @pytest.mark.asyncio
    async def test_strength_and_challenge_identification(
        self, progress_service, sample_sessions
    ):
        """Test identification of strength and challenge areas."""
        summary = await progress_service.compute_progress_summary(
            "test_player_progress"
        )

        # Verify strength areas
        assert isinstance(summary.strength_areas, list)

        # Verify challenge areas
        assert isinstance(summary.challenge_areas, list)

    @pytest.mark.asyncio
    async def test_therapeutic_momentum_calculation(
        self, progress_service, sample_sessions
    ):
        """Test therapeutic momentum calculation."""
        summary = await progress_service.compute_progress_summary(
            "test_player_progress"
        )

        # Verify therapeutic momentum
        assert summary.therapeutic_momentum >= 0.0
        assert summary.therapeutic_momentum <= 1.0

    @pytest.mark.asyncio
    async def test_readiness_for_advancement(self, progress_service, sample_sessions):
        """Test readiness for advancement calculation."""
        summary = await progress_service.compute_progress_summary(
            "test_player_progress"
        )

        # Verify readiness score
        assert summary.readiness_for_advancement >= 0.0
        assert summary.readiness_for_advancement <= 1.0


class TestProgressWithRealData:
    """Tests for progress tracking with real session data from Phase 1."""

    @pytest.mark.asyncio
    async def test_progress_tracking_end_to_end(
        self, test_client, auth_headers, sample_sessions
    ):
        """Test complete progress tracking workflow end-to-end."""
        # Get progress visualization
        viz_response = test_client.get(
            "/api/v1/players/test_player_progress/progress/viz?days=14",
            headers=auth_headers,
        )
        assert viz_response.status_code == 200

        viz_data = viz_response.json()
        assert "time_buckets" in viz_data
        assert "series" in viz_data
        assert "meta" in viz_data

        # Verify data structure
        assert isinstance(viz_data["time_buckets"], list)
        assert isinstance(viz_data["series"], list)