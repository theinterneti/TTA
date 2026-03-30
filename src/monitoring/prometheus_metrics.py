"""

# Logseq: [[TTA.dev/Monitoring/Prometheus_metrics]]
Comprehensive Prometheus metrics collection for TTA application.

This module provides standardized metrics collection patterns for all TTA services,
including application performance, user interactions, story generation, and model comparisons.
"""

import functools
import logging
import time
from collections.abc import Callable
from contextlib import contextmanager

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

logger = logging.getLogger(__name__)

# Global registry for TTA metrics
TTA_REGISTRY = CollectorRegistry()

# Application Performance Metrics
http_requests_total = Counter(
    "tta_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "service"],
    registry=TTA_REGISTRY,
)

http_request_duration_seconds = Histogram(
    "tta_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "service"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=TTA_REGISTRY,
)

active_connections = Gauge(
    "tta_active_connections",
    "Number of active connections",
    ["service"],
    registry=TTA_REGISTRY,
)

# Story Generation Metrics
story_generation_requests_total = Counter(
    "tta_story_generation_requests_total",
    "Total story generation requests",
    ["model_type", "success"],
    registry=TTA_REGISTRY,
)

story_generation_duration_seconds = Histogram(
    "tta_story_generation_duration_seconds",
    "Story generation duration in seconds",
    ["model_type"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
    registry=TTA_REGISTRY,
)

story_quality_score = Histogram(
    "tta_story_quality_score",
    "Story quality assessment score",
    ["model_type"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    registry=TTA_REGISTRY,
)

# Model Performance Metrics
model_requests_total = Counter(
    "tta_model_requests_total",
    "Total model requests",
    ["model_name", "model_provider", "success"],
    registry=TTA_REGISTRY,
)

model_response_time_seconds = Histogram(
    "tta_model_response_time_seconds",
    "Model response time in seconds",
    ["model_name", "model_provider"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
    registry=TTA_REGISTRY,
)

model_token_usage = Counter(
    "tta_model_token_usage_total",
    "Total tokens used by models",
    ["model_name", "model_provider", "token_type"],
    registry=TTA_REGISTRY,
)

model_cost_usd = Counter(
    "tta_model_cost_usd_total",
    "Total cost in USD for model usage",
    ["model_name", "model_provider"],
    registry=TTA_REGISTRY,
)

# User Interaction Metrics
user_sessions_total = Counter(
    "tta_user_sessions_total",
    "Total user sessions",
    ["session_type"],
    registry=TTA_REGISTRY,
)

user_interactions_total = Counter(
    "tta_user_interactions_total",
    "Total user interactions",
    ["interaction_type", "success"],
    registry=TTA_REGISTRY,
)

session_duration_seconds = Histogram(
    "tta_session_duration_seconds",
    "User session duration in seconds",
    ["session_type"],
    buckets=[60, 300, 600, 1800, 3600, 7200],
    registry=TTA_REGISTRY,
)

# Test Execution Metrics
test_executions_total = Counter(
    "tta_test_executions_total",
    "Total test executions",
    ["test_category", "test_result"],
    registry=TTA_REGISTRY,
)

test_duration_seconds = Histogram(
    "tta_test_duration_seconds",
    "Test execution duration in seconds",
    ["test_category"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
    registry=TTA_REGISTRY,
)

test_coverage_percentage = Gauge(
    "tta_test_coverage_percentage",
    "Test coverage percentage",
    ["component"],
    registry=TTA_REGISTRY,
)

# System Health Metrics
system_cpu_usage_percent = Gauge(
    "tta_system_cpu_usage_percent",
    "System CPU usage percentage",
    ["service"],
    registry=TTA_REGISTRY,
)

system_memory_usage_percent = Gauge(
    "tta_system_memory_usage_percent",
    "System memory usage percentage",
    ["service"],
    registry=TTA_REGISTRY,
)

system_disk_usage_percent = Gauge(
    "tta_system_disk_usage_percent",
    "System disk usage percentage",
    ["service"],
    registry=TTA_REGISTRY,
)

# Agent Orchestration Metrics
agent_messages_total = Counter(
    "tta_agent_messages_total",
    "Total agent messages",
    ["agent_type", "message_type", "status"],
    registry=TTA_REGISTRY,
)

agent_processing_time_seconds = Histogram(
    "tta_agent_processing_time_seconds",
    "Agent processing time in seconds",
    ["agent_type"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=TTA_REGISTRY,
)

workflow_executions_total = Counter(
    "tta_workflow_executions_total",
    "Total workflow executions",
    ["workflow_type", "status"],
    registry=TTA_REGISTRY,
)

# Authentication & Player Profile Metrics
jwt_token_generation_total = Counter(
    "tta_jwt_token_generation_total",
    "Total JWT token generation attempts",
    ["service", "result"],  # result: success, failure
    registry=TTA_REGISTRY,
)

jwt_token_generation_duration_seconds = Histogram(
    "tta_jwt_token_generation_duration_seconds",
    "JWT token generation duration in seconds",
    ["service"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
    registry=TTA_REGISTRY,
)

jwt_token_verification_total = Counter(
    "tta_jwt_token_verification_total",
    "Total JWT token verification attempts",
    ["service", "result"],  # result: success, failure, missing_player_id
    registry=TTA_REGISTRY,
)

player_id_field_presence_total = Counter(
    "tta_player_id_field_presence_total",
    "Total requests with player_id field presence tracking",
    ["endpoint", "has_player_id"],  # has_player_id: true, false
    registry=TTA_REGISTRY,
)

player_id_presence_rate = Gauge(
    "tta_player_id_presence_rate_percent",
    "Percentage of requests with valid player_id field",
    ["endpoint"],
    registry=TTA_REGISTRY,
)

player_profile_autocreation_total = Counter(
    "tta_player_profile_autocreation_total",
    "Total player profile auto-creation attempts",
    [
        "trigger",
        "result",
    ],  # trigger: oauth_signin, first_login, etc; result: success, failure
    registry=TTA_REGISTRY,
)

player_profile_autocreation_duration_seconds = Histogram(
    "tta_player_profile_autocreation_duration_seconds",
    "Player profile auto-creation duration in seconds",
    ["trigger"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=TTA_REGISTRY,
)

player_profile_autocreation_errors_total = Counter(
    "tta_player_profile_autocreation_errors_total",
    "Total player profile auto-creation errors by category",
    [
        "error_category"
    ],  # error_category: validation_error, database_error, duplicate_user, etc
    registry=TTA_REGISTRY,
)


class TTAMetricsCollector:
    """Centralized metrics collector for TTA application."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.registry = TTA_REGISTRY

    def record_http_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics."""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
            service=self.service_name,
        ).inc()

        http_request_duration_seconds.labels(
            method=method, endpoint=endpoint, service=self.service_name
        ).observe(duration)

    def record_story_generation(
        self,
        model_type: str,
        duration: float,
        success: bool,
        quality_score: float | None = None,
    ):
        """Record story generation metrics."""
        story_generation_requests_total.labels(
            model_type=model_type, success=str(success).lower()
        ).inc()

        if success:
            story_generation_duration_seconds.labels(model_type=model_type).observe(
                duration
            )

            if quality_score is not None:
                story_quality_score.labels(model_type=model_type).observe(quality_score)

    def record_model_usage(
        self,
        model_name: str,
        provider: str,
        response_time: float,
        success: bool,
        tokens_used: int,
        cost: float,
        token_type: str = "total",
    ):
        """Record model usage metrics."""
        model_requests_total.labels(
            model_name=model_name, model_provider=provider, success=str(success).lower()
        ).inc()

        if success:
            model_response_time_seconds.labels(
                model_name=model_name, model_provider=provider
            ).observe(response_time)

            model_token_usage.labels(
                model_name=model_name, model_provider=provider, token_type=token_type
            ).inc(tokens_used)

            model_cost_usd.labels(model_name=model_name, model_provider=provider).inc(
                cost
            )

    def record_user_interaction(self, interaction_type: str, success: bool):
        """Record user interaction metrics."""
        user_interactions_total.labels(
            interaction_type=interaction_type, success=str(success).lower()
        ).inc()

    def record_test_execution(self, test_category: str, duration: float, result: str):
        """Record test execution metrics."""
        test_executions_total.labels(
            test_category=test_category, test_result=result
        ).inc()

        test_duration_seconds.labels(test_category=test_category).observe(duration)

    def update_system_metrics(
        self, cpu_percent: float, memory_percent: float, disk_percent: float
    ):
        """Update system health metrics."""
        system_cpu_usage_percent.labels(service=self.service_name).set(cpu_percent)
        system_memory_usage_percent.labels(service=self.service_name).set(
            memory_percent
        )
        system_disk_usage_percent.labels(service=self.service_name).set(disk_percent)

    def record_jwt_token_generation(self, success: bool, duration: float):
        """Record JWT token generation metrics."""
        result = "success" if success else "failure"
        jwt_token_generation_total.labels(
            service=self.service_name, result=result
        ).inc()

        if success:
            jwt_token_generation_duration_seconds.labels(
                service=self.service_name
            ).observe(duration)

    def record_jwt_token_verification(self, success: bool, has_player_id: bool):
        """Record JWT token verification metrics."""
        if not success:
            result = "failure"
        elif not has_player_id:
            result = "missing_player_id"
        else:
            result = "success"

        jwt_token_verification_total.labels(
            service=self.service_name, result=result
        ).inc()

    def record_player_id_presence(self, endpoint: str, has_player_id: bool):
        """Record player_id field presence in requests."""
        player_id_field_presence_total.labels(
            endpoint=endpoint, has_player_id=str(has_player_id).lower()
        ).inc()

    def update_player_id_presence_rate(self, endpoint: str, rate_percent: float):
        """Update player_id presence rate gauge."""
        player_id_presence_rate.labels(endpoint=endpoint).set(rate_percent)

    def record_player_profile_autocreation(
        self,
        trigger: str,
        success: bool,
        duration: float,
        error_category: str | None = None,
    ):
        """Record player profile auto-creation metrics."""
        result = "success" if success else "failure"
        player_profile_autocreation_total.labels(trigger=trigger, result=result).inc()

        player_profile_autocreation_duration_seconds.labels(trigger=trigger).observe(
            duration
        )

        if not success and error_category:
            player_profile_autocreation_errors_total.labels(
                error_category=error_category
            ).inc()

    @contextmanager
    def time_operation(self, operation_name: str, labels: dict[str, str] | None = None):
        """Context manager to time operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            # This is a generic timing context - specific metrics should be recorded by the caller
            logger.debug(f"Operation {operation_name} took {duration:.3f} seconds")

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        return generate_latest(self.registry).decode("utf-8")


# Global metrics collector instance
_metrics_collector: TTAMetricsCollector | None = None


def get_metrics_collector(service_name: str = "tta") -> TTAMetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = TTAMetricsCollector(service_name)
    return _metrics_collector


def metrics_endpoint():
    """FastAPI endpoint for Prometheus metrics."""
    collector = get_metrics_collector()
    return collector.get_metrics()


def track_http_requests(service_name: str = "tta"):
    """Decorator to automatically track HTTP request metrics."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            collector = get_metrics_collector(service_name)
            start_time = time.time()

            # Extract request info from FastAPI request object
            request = None
            for arg in args:
                if hasattr(arg, "method") and hasattr(arg, "url"):
                    request = arg
                    break

            try:
                response = await func(*args, **kwargs)
                duration = time.time() - start_time

                if request:
                    collector.record_http_request(
                        method=request.method,
                        endpoint=request.url.path,
                        status_code=getattr(response, "status_code", 200),
                        duration=duration,
                    )

                return response
            except Exception:
                duration = time.time() - start_time

                if request:
                    collector.record_http_request(
                        method=request.method,
                        endpoint=request.url.path,
                        status_code=500,
                        duration=duration,
                    )

                raise

        return wrapper

    return decorator
