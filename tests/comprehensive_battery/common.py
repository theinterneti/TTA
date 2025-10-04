"""
Common classes and enums for the comprehensive test battery.

This module contains shared classes and enumerations used across
all test suites and validators to avoid circular imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TestStatus(Enum):
    """Test execution status enumeration."""

    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestCategory(Enum):
    """Test category enumeration."""

    STANDARD = "standard"
    ADVERSARIAL = "adversarial"
    LOAD_STRESS = "load_stress"
    DATA_PIPELINE = "data_pipeline"
    DASHBOARD = "dashboard"


@dataclass
class TestResult:
    """
    Test result data structure.

    Contains all information about a test execution including
    timing, status, results, and any error information.
    """

    test_name: str
    category: TestCategory
    status: TestStatus
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float = 0.0
    passed: bool = False
    error_message: str | None = None
    metrics: dict[str, Any] | None = field(default_factory=dict)
    details: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self):
        """Calculate duration if end_time is set."""
        if self.end_time and self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
