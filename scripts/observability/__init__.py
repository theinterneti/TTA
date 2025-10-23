"""
Agentic Primitives - Development Observability

Track and visualize development operation metrics.

Quick Start:
    from observability import track_execution, get_collector, generate_dashboard

    @track_execution("my_operation")
    def my_function():
        # Your code here
        pass

    # View metrics
    collector = get_collector()
    summary = collector.get_metrics_summary(days=7)

    # Generate dashboard
    generate_dashboard("dashboard.html")

For more details, see scripts/observability/README.md
"""

from .dev_metrics import (
    # Core classes
    ExecutionMetric,
    DevMetricsCollector,

    # Decorator
    track_execution,

    # Global collector
    get_collector,
)

from .dashboard import (
    # Dashboard generation
    generate_dashboard,
)

__all__ = [
    # Core classes
    "ExecutionMetric",
    "DevMetricsCollector",

    # Decorator
    "track_execution",

    # Global collector
    "get_collector",

    # Dashboard
    "generate_dashboard",
]

__version__ = "1.0.0"
