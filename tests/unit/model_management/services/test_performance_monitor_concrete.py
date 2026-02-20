"""

# Logseq: [[TTA.dev/Tests/Unit/Model_management/Services/Test_performance_monitor_concrete]]
Concrete Value Tests for PerformanceMonitor Service.

This module contains concrete value tests with hardcoded expected values
to achieve high mutation testing scores by validating specific calculations.
"""

import asyncio
from datetime import datetime

import pytest
from tta_ai.models.models import PerformanceMetrics
from tta_ai.models.services import PerformanceMonitor


@pytest.mark.unit
class TestPerformanceMonitorConcrete:
    """Concrete value tests for PerformanceMonitor service."""

    def test_basic_metrics_aggregation_with_three_metrics(self):
        """Test aggregation with 3 metrics - hardcoded expected values."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=50,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=200,
                tokens_per_second=20,
                total_tokens=100,
                error_count=1,
                success_rate=0.95,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=300,
                tokens_per_second=30,
                total_tokens=150,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - hardcoded expected values
        assert stats["total_requests"] == 3
        assert stats["total_tokens"] == 300  # 50 + 100 + 150
        assert stats["total_errors"] == 1  # 0 + 1 + 0
        assert stats["average_response_time_ms"] == 200.0  # (100 + 200 + 300) / 3
        assert stats["min_response_time_ms"] == 100
        assert stats["max_response_time_ms"] == 300
        assert stats["average_tokens_per_second"] == 20.0  # (10 + 20 + 30) / 3
        assert stats["max_tokens_per_second"] == 30
        assert (
            abs(stats["success_rate"] - 0.9833333333333333) < 1e-10
        )  # (1.0 + 0.95 + 1.0) / 3

    def test_percentile_calculation_with_ten_values(self):
        """Test percentile calculations with 10 known values."""
        # Arrange
        monitor = PerformanceMonitor()

        # Create 10 metrics with response times: 100, 200, 300, ..., 1000
        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=float(i * 100),
                tokens_per_second=10,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            )
            for i in range(1, 11)
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - hardcoded expected percentiles
        # Sorted: [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        # P95 index: int(0.95 * 10) = 9, min(9, 9) = 9 -> sorted_data[9] = 1000
        # P99 index: int(0.99 * 10) = 9, min(9, 9) = 9 -> sorted_data[9] = 1000
        assert stats["p95_response_time_ms"] == 1000.0
        assert stats["p99_response_time_ms"] == 1000.0
        assert stats["average_response_time_ms"] == 550.0  # (100+200+...+1000) / 10

    def test_quality_score_aggregation_with_four_scores(self):
        """Test quality score aggregation with 4 specific scores."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                quality_score=7.5,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                quality_score=8.0,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                quality_score=9.0,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                quality_score=6.5,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - hardcoded expected values
        assert stats["average_quality_score"] == 7.75  # (7.5 + 8.0 + 9.0 + 6.5) / 4
        assert stats["min_quality_score"] == 6.5
        assert stats["max_quality_score"] == 9.0

    def test_success_rate_calculation_with_four_rates(self):
        """Test success rate calculation with 4 specific rates."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                error_count=1,
                success_rate=0.95,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                error_count=0,
                success_rate=0.98,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - hardcoded expected value
        assert (
            abs(stats["success_rate"] - 0.9825) < 1e-10
        )  # (1.0 + 0.95 + 0.98 + 1.0) / 4

    def test_default_values_applied_when_fields_missing(self):
        """Test that default values are applied when optional fields are missing."""
        # Arrange
        monitor = PerformanceMonitor()

        # Metrics dict with minimal fields
        metrics_dict = {
            "total_tokens": 100,
        }

        # Act
        asyncio.run(monitor.record_metrics("test-model", metrics_dict))

        # Assert - check default values were applied
        stored_metric = monitor._metrics_cache["test-model"][0]
        assert stored_metric.response_time_ms == 0  # Default
        assert stored_metric.tokens_per_second == 0  # Default
        assert stored_metric.success_rate == 1.0  # Default
        assert stored_metric.error_count == 0  # Default
        assert stored_metric.quality_score is None  # No default
        assert stored_metric.metadata == {}  # Default empty dict

    def test_empty_metrics_list_returns_empty_dict(self):
        """Test that empty metrics list returns empty dict."""
        # Arrange
        monitor = PerformanceMonitor()

        # Act
        stats = monitor._calculate_aggregated_stats([])

        # Assert
        assert stats == {}

    def test_resource_usage_statistics_with_three_metrics(self):
        """Test resource usage statistics with 3 metrics."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                memory_usage_mb=512.0,
                gpu_memory_usage_mb=2048.0,
                cpu_usage_percent=25.0,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                memory_usage_mb=768.0,
                gpu_memory_usage_mb=3072.0,
                cpu_usage_percent=50.0,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                memory_usage_mb=1024.0,
                gpu_memory_usage_mb=4096.0,
                cpu_usage_percent=75.0,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - hardcoded expected values
        assert stats["average_memory_usage_mb"] == 768.0  # (512 + 768 + 1024) / 3
        assert stats["peak_memory_usage_mb"] == 1024.0
        assert (
            stats["average_gpu_memory_usage_mb"] == 3072.0
        )  # (2048 + 3072 + 4096) / 3
        assert stats["peak_gpu_memory_usage_mb"] == 4096.0
        assert stats["average_cpu_usage_percent"] == 50.0  # (25 + 50 + 75) / 3
        assert stats["peak_cpu_usage_percent"] == 75.0

    def test_model_usage_stats_calculation_with_known_performance_data(self):
        """Test model usage stats calculation with known performance data."""
        # Arrange
        monitor = PerformanceMonitor()

        # Record 5 metrics: 4 successful, 1 failed
        metrics_list = [
            {
                "response_time_ms": 100,
                "total_tokens": 50,
                "error_count": 0,
                "success_rate": 1.0,
            },
            {
                "response_time_ms": 150,
                "total_tokens": 75,
                "error_count": 0,
                "success_rate": 1.0,
            },
            {
                "response_time_ms": 200,
                "total_tokens": 100,
                "error_count": 1,
                "success_rate": 0.0,
            },
            {
                "response_time_ms": 120,
                "total_tokens": 60,
                "error_count": 0,
                "success_rate": 1.0,
            },
            {
                "response_time_ms": 180,
                "total_tokens": 90,
                "error_count": 0,
                "success_rate": 1.0,
            },
        ]

        for metrics in metrics_list:
            asyncio.run(monitor.record_metrics("test-model", metrics))

        # Act
        usage_stats = asyncio.run(monitor.get_model_usage_stats("test-model", 24))

        # Assert - hardcoded expected values
        assert usage_stats.total_requests == 5
        assert usage_stats.total_tokens_generated == 375  # 50 + 75 + 100 + 60 + 90
        assert usage_stats.failed_requests == 1
        assert usage_stats.successful_requests == 4  # 5 - 1
        assert usage_stats.average_tokens_per_request == 75.0  # 375 / 5
        assert (
            usage_stats.average_response_time_ms == 150.0
        )  # (100+150+200+120+180) / 5

    def test_token_throughput_statistics_with_four_metrics(self):
        """Test token throughput statistics with 4 metrics."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10.0,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=20.0,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=30.0,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=40.0,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - hardcoded expected values
        assert stats["average_tokens_per_second"] == 25.0  # (10 + 20 + 30 + 40) / 4
        assert stats["max_tokens_per_second"] == 40.0

    def test_mixed_optional_fields_some_none_some_values(self):
        """Test aggregation when some metrics have optional fields and some don't."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                quality_score=8.0,  # Has quality score
                therapeutic_safety_score=9.0,  # Has safety score
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=200,
                tokens_per_second=20,
                total_tokens=200,
                quality_score=None,  # No quality score
                therapeutic_safety_score=None,  # No safety score
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=300,
                tokens_per_second=30,
                total_tokens=300,
                quality_score=6.0,  # Has quality score
                therapeutic_safety_score=7.0,  # Has safety score
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - averages calculated only from non-None values
        assert stats["average_quality_score"] == 7.0  # (8.0 + 6.0) / 2 (excludes None)
        assert stats["min_quality_score"] == 6.0
        assert stats["max_quality_score"] == 8.0
        assert stats["average_safety_score"] == 8.0  # (9.0 + 7.0) / 2 (excludes None)
        assert stats["min_safety_score"] == 7.0
        assert stats["max_safety_score"] == 9.0
        # All metrics have response times
        assert stats["average_response_time_ms"] == 200.0  # (100 + 200 + 300) / 3

    def test_percentile_with_single_value_returns_that_value(self):
        """Test percentile calculation with single value."""
        # Arrange
        monitor = PerformanceMonitor()

        # Act
        result = monitor._percentile([42.5], 95)

        # Assert
        assert result == 42.5

    def test_percentile_with_empty_list_returns_zero(self):
        """Test percentile calculation with empty list."""
        # Arrange
        monitor = PerformanceMonitor()

        # Act
        result = monitor._percentile([], 95)

        # Assert
        assert result == 0.0

    def test_safety_score_aggregation_with_three_scores(self):
        """Test therapeutic safety score aggregation with 3 specific scores."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                therapeutic_safety_score=8.5,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                therapeutic_safety_score=9.0,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=100,
                therapeutic_safety_score=7.5,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - hardcoded expected values
        assert (
            stats["average_safety_score"] == 8.333333333333334
        )  # (8.5 + 9.0 + 7.5) / 3
        assert stats["min_safety_score"] == 7.5
        assert stats["max_safety_score"] == 9.0

    def test_zero_response_times_excluded_from_statistics(self):
        """Test that zero response times are excluded from statistics."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=0,  # Zero - should be excluded
                tokens_per_second=10,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,  # Non-zero
                tokens_per_second=10,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=200,  # Non-zero
                tokens_per_second=10,
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - average calculated only from non-zero values
        assert (
            stats["average_response_time_ms"] == 150.0
        )  # (100 + 200) / 2 (excludes 0)
        assert stats["min_response_time_ms"] == 100
        assert stats["max_response_time_ms"] == 200

    def test_zero_tokens_per_second_excluded_from_statistics(self):
        """Test that zero tokens_per_second are excluded from statistics."""
        # Arrange
        monitor = PerformanceMonitor()

        metrics = [
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=0,  # Zero - should be excluded
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=15.0,  # Non-zero
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
            PerformanceMetrics(
                model_id="test-model",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=25.0,  # Non-zero
                total_tokens=100,
                error_count=0,
                success_rate=1.0,
            ),
        ]

        # Act
        stats = monitor._calculate_aggregated_stats(metrics)

        # Assert - average calculated only from non-zero values
        assert stats["average_tokens_per_second"] == 20.0  # (15 + 25) / 2 (excludes 0)
        assert stats["max_tokens_per_second"] == 25.0
