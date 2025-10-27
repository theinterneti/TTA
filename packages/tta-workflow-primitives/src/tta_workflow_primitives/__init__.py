"""TTA Workflow Primitives - Composable workflow building blocks."""

from .core.base import LambdaPrimitive, WorkflowContext, WorkflowPrimitive
from .core.conditional import ConditionalPrimitive
from .core.parallel import ParallelPrimitive
from .core.routing import RouterPrimitive
from .core.sequential import SequentialPrimitive
from .performance.cache import CachePrimitive
from .recovery.timeout import TimeoutError, TimeoutPrimitive

# APM support (optional)
try:
    from .apm import setup_apm, get_tracer, get_meter, is_apm_enabled
    from .apm.instrumented import APMWorkflowPrimitive
    from .apm.decorators import trace_workflow, track_metric
    
    _apm_exports = [
        "setup_apm",
        "get_tracer",
        "get_meter",
        "is_apm_enabled",
        "APMWorkflowPrimitive",
        "trace_workflow",
        "track_metric",
    ]
except ImportError:
    # APM dependencies not installed
    _apm_exports = []

__all__ = [
    "WorkflowContext",
    "WorkflowPrimitive",
    "LambdaPrimitive",
    "ConditionalPrimitive",
    "ParallelPrimitive",
    "SequentialPrimitive",
    "RouterPrimitive",
    "CachePrimitive",
    "TimeoutPrimitive",
    "TimeoutError",
] + _apm_exports

__version__ = "0.2.0"

