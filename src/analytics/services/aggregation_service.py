"""
Advanced Analytics Aggregation Service

This service provides privacy-compliant aggregate user behavior analysis
for the TTA system, enabling cross-user insights while maintaining individual privacy.
"""

import hashlib
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class UserBehaviorPattern:
    """Represents an anonymized user behavior pattern."""

    pattern_id: str
    pattern_type: str  # 'engagement', 'therapeutic_progress', 'session_behavior'
    pattern_data: dict[str, Any]
    confidence_score: float
    user_cohort: str
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


@dataclass
class TherapeuticOutcome:
    """Represents therapeutic outcome data for analysis."""

    outcome_id: str
    user_cohort: str
    session_count: int
    total_duration_hours: float
    engagement_score: float
    progress_markers_count: int
    therapeutic_goals_achieved: int
    outcome_category: str  # 'positive', 'neutral', 'needs_attention'
    created_at: datetime


class PrivacyCompliantAggregator:
    """Handles privacy-compliant data aggregation and anonymization."""

    def __init__(self, salt: str = "tta_analytics_salt_2024"):
        self.salt = salt
        self.scaler = StandardScaler()

    def anonymize_user_id(self, user_id: str) -> str:
        """Create anonymized hash of user ID."""
        return hashlib.sha256(f"{user_id}{self.salt}".encode()).hexdigest()[:16]

    def create_user_cohort(self, user_data: dict[str, Any]) -> str:
        """Assign user to privacy-preserving cohort based on characteristics."""
        # Create cohort based on therapeutic preferences and usage patterns
        therapeutic_focus = user_data.get("therapeutic_focus", "general")
        session_frequency = user_data.get("session_frequency", "medium")
        engagement_level = user_data.get("engagement_level", "medium")

        cohort_key = f"{therapeutic_focus}_{session_frequency}_{engagement_level}"
        return hashlib.md5(cohort_key.encode()).hexdigest()[:8]

    def add_differential_privacy_noise(
        self, value: float, epsilon: float = 1.0
    ) -> float:
        """Add Laplace noise for differential privacy."""
        sensitivity = 1.0  # Adjust based on data sensitivity
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale)
        return max(0, value + noise)  # Ensure non-negative values


class BehaviorPatternDetector:
    """Detects behavioral patterns in user data using ML algorithms."""

    def __init__(self):
        self.engagement_model = KMeans(n_clusters=5, random_state=42)
        self.progress_model = KMeans(n_clusters=4, random_state=42)
        self.session_model = KMeans(n_clusters=6, random_state=42)
        self.scaler = StandardScaler()

    def detect_engagement_patterns(
        self, user_sessions: list[dict[str, Any]]
    ) -> list[UserBehaviorPattern]:
        """Detect user engagement patterns."""
        if len(user_sessions) < 5:  # Need minimum data for pattern detection
            return []

        # Extract engagement features
        features = []
        for session in user_sessions:
            features.append(
                [
                    session.get("duration_minutes", 0),
                    session.get("interaction_count", 0),
                    session.get("therapeutic_interventions_count", 0),
                    session.get("progress_markers_count", 0),
                ]
            )

        if len(features) < 5:
            return []

        # Normalize features
        features_scaled = self.scaler.fit_transform(features)

        # Detect patterns
        clusters = self.engagement_model.fit_predict(features_scaled)

        patterns = []
        for cluster_id in np.unique(clusters):
            cluster_sessions = [
                session
                for i, session in enumerate(user_sessions)
                if clusters[i] == cluster_id
            ]

            pattern = UserBehaviorPattern(
                pattern_id=str(uuid4()),
                pattern_type="engagement",
                pattern_data={
                    "cluster_id": int(cluster_id),
                    "session_count": len(cluster_sessions),
                    "avg_duration": np.mean(
                        [s.get("duration_minutes", 0) for s in cluster_sessions]
                    ),
                    "avg_interactions": np.mean(
                        [s.get("interaction_count", 0) for s in cluster_sessions]
                    ),
                    "engagement_level": self._classify_engagement_level(
                        cluster_sessions
                    ),
                },
                confidence_score=min(
                    1.0, len(cluster_sessions) / 10.0
                ),  # Higher confidence with more data
                user_cohort="engagement_analysis",
                created_at=datetime.utcnow(),
            )
            patterns.append(pattern)

        return patterns

    def detect_therapeutic_progress_patterns(
        self, progress_data: list[dict[str, Any]]
    ) -> list[UserBehaviorPattern]:
        """Detect therapeutic progress patterns."""
        if len(progress_data) < 3:
            return []

        # Extract progress features
        features = []
        for progress in progress_data:
            features.append(
                [
                    progress.get("overall_progress", 0),
                    progress.get("goal_completion_rate", 0),
                    progress.get("engagement_level", 0),
                    progress.get("total_sessions", 0),
                ]
            )

        if len(features) < 3:
            return []

        # Normalize and cluster
        features_scaled = self.scaler.fit_transform(features)
        clusters = self.progress_model.fit_predict(features_scaled)

        patterns = []
        for cluster_id in np.unique(clusters):
            cluster_data = [
                progress
                for i, progress in enumerate(progress_data)
                if clusters[i] == cluster_id
            ]

            pattern = UserBehaviorPattern(
                pattern_id=str(uuid4()),
                pattern_type="therapeutic_progress",
                pattern_data={
                    "cluster_id": int(cluster_id),
                    "user_count": len(cluster_data),
                    "avg_progress": np.mean(
                        [p.get("overall_progress", 0) for p in cluster_data]
                    ),
                    "avg_goal_completion": np.mean(
                        [p.get("goal_completion_rate", 0) for p in cluster_data]
                    ),
                    "progress_category": self._classify_progress_category(cluster_data),
                },
                confidence_score=min(1.0, len(cluster_data) / 20.0),
                user_cohort="progress_analysis",
                created_at=datetime.utcnow(),
            )
            patterns.append(pattern)

        return patterns

    def _classify_engagement_level(self, sessions: list[dict[str, Any]]) -> str:
        """Classify engagement level based on session data."""
        avg_duration = np.mean([s.get("duration_minutes", 0) for s in sessions])
        avg_interactions = np.mean([s.get("interaction_count", 0) for s in sessions])

        if avg_duration > 30 and avg_interactions > 20:
            return "high"
        if avg_duration > 15 and avg_interactions > 10:
            return "medium"
        return "low"

    def _classify_progress_category(self, progress_data: list[dict[str, Any]]) -> str:
        """Classify therapeutic progress category."""
        avg_progress = np.mean([p.get("overall_progress", 0) for p in progress_data])
        avg_completion = np.mean(
            [p.get("goal_completion_rate", 0) for p in progress_data]
        )

        if avg_progress > 0.7 and avg_completion > 0.6:
            return "excellent"
        if avg_progress > 0.5 and avg_completion > 0.4:
            return "good"
        if avg_progress > 0.3 and avg_completion > 0.2:
            return "moderate"
        return "needs_attention"


class AnalyticsAggregationService:
    """Main service for advanced analytics aggregation."""

    def __init__(self):
        self.privacy_aggregator = PrivacyCompliantAggregator()
        self.pattern_detector = BehaviorPatternDetector()
        self.behavior_patterns: list[UserBehaviorPattern] = []
        self.therapeutic_outcomes: list[TherapeuticOutcome] = []

    async def aggregate_user_behavior(
        self, user_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Aggregate user behavior data with privacy compliance."""
        try:
            # Anonymize and group users into cohorts
            cohort_data = {}
            for user in user_data:
                anonymized_id = self.privacy_aggregator.anonymize_user_id(
                    user["user_id"]
                )
                cohort = self.privacy_aggregator.create_user_cohort(user)

                if cohort not in cohort_data:
                    cohort_data[cohort] = []

                # Add anonymized user data to cohort
                anonymized_user = {
                    "anonymized_id": anonymized_id,
                    "sessions": user.get("sessions", []),
                    "progress_data": user.get("progress_data", {}),
                    "therapeutic_metrics": user.get("therapeutic_metrics", {}),
                }
                cohort_data[cohort].append(anonymized_user)

            # Detect patterns for each cohort
            all_patterns = []
            for _, users in cohort_data.items():
                # Aggregate session data for pattern detection
                all_sessions = []
                all_progress = []

                for user in users:
                    all_sessions.extend(user["sessions"])
                    if user["progress_data"]:
                        all_progress.append(user["progress_data"])

                # Detect engagement patterns
                engagement_patterns = self.pattern_detector.detect_engagement_patterns(
                    all_sessions
                )
                all_patterns.extend(engagement_patterns)

                # Detect progress patterns
                progress_patterns = (
                    self.pattern_detector.detect_therapeutic_progress_patterns(
                        all_progress
                    )
                )
                all_patterns.extend(progress_patterns)

            # Store patterns
            self.behavior_patterns.extend(all_patterns)

            return {
                "success": True,
                "patterns_detected": len(all_patterns),
                "cohorts_analyzed": len(cohort_data),
                "total_users": len(user_data),
                "analysis_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in aggregate_user_behavior: {e}")
            return {"success": False, "error": str(e), "patterns_detected": 0}

    async def get_behavior_patterns(
        self, pattern_type: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Retrieve detected behavior patterns."""
        patterns = self.behavior_patterns

        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]

        # Sort by confidence score and creation time
        patterns.sort(key=lambda x: (x.confidence_score, x.created_at), reverse=True)

        return [pattern.to_dict() for pattern in patterns[:limit]]

    async def get_cohort_analysis(self) -> dict[str, Any]:
        """Get aggregate cohort analysis."""
        cohort_stats = {}

        for pattern in self.behavior_patterns:
            cohort = pattern.user_cohort
            if cohort not in cohort_stats:
                cohort_stats[cohort] = {
                    "pattern_count": 0,
                    "avg_confidence": 0.0,
                    "pattern_types": set(),
                }

            cohort_stats[cohort]["pattern_count"] += 1
            cohort_stats[cohort]["avg_confidence"] += pattern.confidence_score
            cohort_stats[cohort]["pattern_types"].add(pattern.pattern_type)

        # Calculate averages and convert sets to lists
        for _, stats in cohort_stats.items():
            if stats["pattern_count"] > 0:
                stats["avg_confidence"] /= stats["pattern_count"]
            stats["pattern_types"] = list(stats["pattern_types"])

        return {
            "total_cohorts": len(cohort_stats),
            "cohort_statistics": cohort_stats,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }


# FastAPI app for the aggregation service
app = FastAPI(title="TTA Analytics Aggregation Service", version="1.0.0")

# Global service instance
aggregation_service = AnalyticsAggregationService()


# API Models
class UserBehaviorRequest(BaseModel):
    """Request model for user behavior aggregation."""

    user_data: list[dict[str, Any]] = Field(
        ..., description="List of user data for aggregation"
    )
    privacy_level: str = Field(default="high", description="Privacy protection level")


class PatternResponse(BaseModel):
    """Response model for behavior patterns."""

    patterns: list[dict[str, Any]]
    total_count: int
    analysis_timestamp: str


@app.post("/aggregate/behavior", response_model=dict[str, Any])
async def aggregate_behavior(request: UserBehaviorRequest):
    """Aggregate user behavior data with privacy compliance."""
    return await aggregation_service.aggregate_user_behavior(request.user_data)


@app.get("/patterns", response_model=PatternResponse)
async def get_patterns(pattern_type: str | None = None, limit: int = 50):
    """Get detected behavior patterns."""
    patterns = await aggregation_service.get_behavior_patterns(pattern_type, limit)
    return PatternResponse(
        patterns=patterns,
        total_count=len(patterns),
        analysis_timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/cohorts/analysis", response_model=dict[str, Any])
async def get_cohort_analysis():
    """Get aggregate cohort analysis."""
    return await aggregation_service.get_cohort_analysis()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics-aggregation",
        "patterns_stored": len(aggregation_service.behavior_patterns),
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8095)
