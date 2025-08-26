"""
Response time monitoring system for agent orchestration optimization.

This module provides comprehensive response time collection and analysis
for all system components to enable performance optimization.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Callable, Deque
from uuid import uuid4
from enum import Enum

logger = logging.getLogger(__name__)


class ResponseTimeCategory(str, Enum):
    """Categories of response time measurements."""
    MESSAGE_PROCESSING = "message_processing"
    WORKFLOW_EXECUTION = "workflow_execution"
    AGENT_RESPONSE = "agent_response"
    WEBSOCKET_CONNECTION = "websocket_connection"
    DATABASE_OPERATION = "database_operation"
    REDIS_OPERATION = "redis_operation"
    API_REQUEST = "api_request"
    SYSTEM_OPERATION = "system_operation"


@dataclass
class ResponseTimeMetric:
    """Individual response time measurement."""
    metric_id: str
    category: ResponseTimeCategory
    operation: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        category: ResponseTimeCategory,
        operation: str,
        start_time: float,
        end_time: Optional[float] = None,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ResponseTimeMetric:
        """Create a response time metric."""
        if end_time is None:
            end_time = time.time()
        
        return cls(
            metric_id=uuid4().hex,
            category=category,
            operation=operation,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            success=success,
            metadata=metadata or {},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metric_id": self.metric_id,
            "category": self.category.value,
            "operation": self.operation,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "success": self.success,
            "metadata": self.metadata,
        }


@dataclass
class ResponseTimeStats:
    """Statistical analysis of response times."""
    category: ResponseTimeCategory
    operation: str
    sample_count: int
    mean_duration: float
    median_duration: float
    p95_duration: float
    p99_duration: float
    min_duration: float
    max_duration: float
    success_rate: float
    last_updated: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "category": self.category.value,
            "operation": self.operation,
            "sample_count": self.sample_count,
            "mean_duration": self.mean_duration,
            "median_duration": self.median_duration,
            "p95_duration": self.p95_duration,
            "p99_duration": self.p99_duration,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "success_rate": self.success_rate,
            "last_updated": self.last_updated,
        }


class ResponseTimeCollector:
    """Collects response time metrics from system components."""
    
    def __init__(
        self,
        max_metrics_per_operation: int = 1000,
        cleanup_interval: float = 300.0,  # 5 minutes
        metric_retention_hours: float = 24.0,
    ):
        self.max_metrics_per_operation = max_metrics_per_operation
        self.cleanup_interval = cleanup_interval
        self.metric_retention_seconds = metric_retention_hours * 3600
        
        # Metric storage: category -> operation -> deque of metrics
        self.metrics: Dict[ResponseTimeCategory, Dict[str, Deque[ResponseTimeMetric]]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=max_metrics_per_operation))
        )
        
        # Active timing contexts
        self.active_timings: Dict[str, float] = {}  # context_id -> start_time
        
        # Statistics cache
        self.stats_cache: Dict[str, ResponseTimeStats] = {}
        self.stats_cache_ttl: float = 60.0  # 1 minute
        self.last_stats_update: Dict[str, float] = {}
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Callbacks for real-time notifications
        self.metric_callbacks: Set[Callable[[ResponseTimeMetric], None]] = set()
        
        logger.info("ResponseTimeCollector initialized")
    
    async def start(self) -> None:
        """Start the response time collector."""
        if self._is_running:
            return
        
        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("ResponseTimeCollector started")
    
    async def stop(self) -> None:
        """Stop the response time collector."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("ResponseTimeCollector stopped")
    
    def start_timing(
        self,
        category: ResponseTimeCategory,
        operation: str,
        context_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Start timing an operation."""
        if context_id is None:
            context_id = uuid4().hex
        
        self.active_timings[context_id] = time.time()
        
        # Store metadata for later use
        if metadata:
            self.active_timings[f"{context_id}_metadata"] = metadata
        
        self.active_timings[f"{context_id}_category"] = category
        self.active_timings[f"{context_id}_operation"] = operation
        
        return context_id
    
    def end_timing(
        self,
        context_id: str,
        success: bool = True,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ResponseTimeMetric]:
        """End timing an operation and record the metric."""
        start_time = self.active_timings.pop(context_id, None)
        if start_time is None:
            logger.warning(f"No active timing found for context: {context_id}")
            return None
        
        # Get stored context information
        category = self.active_timings.pop(f"{context_id}_category", ResponseTimeCategory.SYSTEM_OPERATION)
        operation = self.active_timings.pop(f"{context_id}_operation", "unknown")
        metadata = self.active_timings.pop(f"{context_id}_metadata", {})
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Create metric
        metric = ResponseTimeMetric.create(
            category=category,
            operation=operation,
            start_time=start_time,
            success=success,
            metadata=metadata,
        )
        
        # Store metric
        self.record_metric(metric)
        
        return metric
    
    def record_metric(self, metric: ResponseTimeMetric) -> None:
        """Record a response time metric."""
        # Store in appropriate category and operation
        self.metrics[metric.category][metric.operation].append(metric)
        
        # Invalidate stats cache for this operation
        cache_key = f"{metric.category.value}:{metric.operation}"
        self.last_stats_update.pop(cache_key, None)
        
        # Notify callbacks
        self._notify_callbacks(metric)
        
        logger.debug(f"Recorded metric: {metric.category.value}:{metric.operation} - {metric.duration:.3f}s")
    
    def record_duration(
        self,
        category: ResponseTimeCategory,
        operation: str,
        duration: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ResponseTimeMetric:
        """Record a duration directly without timing context."""
        end_time = time.time()
        start_time = end_time - duration
        
        metric = ResponseTimeMetric.create(
            category=category,
            operation=operation,
            start_time=start_time,
            end_time=end_time,
            success=success,
            metadata=metadata,
        )
        
        self.record_metric(metric)
        return metric
    
    def get_stats(
        self,
        category: ResponseTimeCategory,
        operation: str,
        force_refresh: bool = False,
    ) -> Optional[ResponseTimeStats]:
        """Get statistical analysis for a specific operation."""
        cache_key = f"{category.value}:{operation}"
        
        # Check cache
        if not force_refresh and cache_key in self.stats_cache:
            last_update = self.last_stats_update.get(cache_key, 0)
            if time.time() - last_update < self.stats_cache_ttl:
                return self.stats_cache[cache_key]
        
        # Get metrics for this operation
        metrics = list(self.metrics[category][operation])
        if not metrics:
            return None
        
        # Calculate statistics
        durations = [m.duration for m in metrics]
        success_count = sum(1 for m in metrics if m.success)
        
        stats = ResponseTimeStats(
            category=category,
            operation=operation,
            sample_count=len(metrics),
            mean_duration=statistics.mean(durations),
            median_duration=statistics.median(durations),
            p95_duration=self._percentile(durations, 95),
            p99_duration=self._percentile(durations, 99),
            min_duration=min(durations),
            max_duration=max(durations),
            success_rate=success_count / len(metrics) if metrics else 0.0,
        )
        
        # Cache results
        self.stats_cache[cache_key] = stats
        self.last_stats_update[cache_key] = time.time()
        
        return stats
    
    def get_all_stats(self, force_refresh: bool = False) -> Dict[str, ResponseTimeStats]:
        """Get statistics for all operations."""
        all_stats = {}
        
        for category, operations in self.metrics.items():
            for operation in operations:
                stats = self.get_stats(category, operation, force_refresh)
                if stats:
                    key = f"{category.value}:{operation}"
                    all_stats[key] = stats
        
        return all_stats
    
    def get_recent_metrics(
        self,
        category: Optional[ResponseTimeCategory] = None,
        operation: Optional[str] = None,
        limit: int = 100,
        since: Optional[float] = None,
    ) -> List[ResponseTimeMetric]:
        """Get recent metrics with optional filtering."""
        all_metrics = []
        
        # Determine which categories to check
        categories = [category] if category else list(self.metrics.keys())
        
        for cat in categories:
            if cat not in self.metrics:
                continue
            
            # Determine which operations to check
            operations = [operation] if operation else list(self.metrics[cat].keys())
            
            for op in operations:
                if op not in self.metrics[cat]:
                    continue
                
                # Get metrics for this operation
                metrics = list(self.metrics[cat][op])
                
                # Filter by time if specified
                if since:
                    metrics = [m for m in metrics if m.end_time >= since]
                
                all_metrics.extend(metrics)
        
        # Sort by end time (most recent first) and limit
        all_metrics.sort(key=lambda m: m.end_time, reverse=True)
        return all_metrics[:limit]
    
    def add_callback(self, callback: Callable[[ResponseTimeMetric], None]) -> None:
        """Add a callback for new metrics."""
        self.metric_callbacks.add(callback)
    
    def remove_callback(self, callback: Callable[[ResponseTimeMetric], None]) -> None:
        """Remove a callback."""
        self.metric_callbacks.discard(callback)
    
    def _notify_callbacks(self, metric: ResponseTimeMetric) -> None:
        """Notify all callbacks of a new metric."""
        for callback in self.metric_callbacks:
            try:
                callback(metric)
            except Exception as e:
                logger.error(f"Error in metric callback: {e}")
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    async def _cleanup_loop(self) -> None:
        """Background task to clean up old metrics."""
        while self._is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = time.time()
                cutoff_time = current_time - self.metric_retention_seconds
                
                total_removed = 0
                
                # Clean up old metrics
                for category in self.metrics:
                    for operation in self.metrics[category]:
                        metrics_deque = self.metrics[category][operation]
                        
                        # Remove old metrics from the front of the deque
                        while metrics_deque and metrics_deque[0].end_time < cutoff_time:
                            metrics_deque.popleft()
                            total_removed += 1
                
                # Clean up orphaned active timings (older than 1 hour)
                orphaned_contexts = []
                for context_id, start_time in self.active_timings.items():
                    if isinstance(start_time, float) and current_time - start_time > 3600:
                        orphaned_contexts.append(context_id)
                
                for context_id in orphaned_contexts:
                    self.active_timings.pop(context_id, None)
                    # Also clean up associated metadata
                    self.active_timings.pop(f"{context_id}_metadata", None)
                    self.active_timings.pop(f"{context_id}_category", None)
                    self.active_timings.pop(f"{context_id}_operation", None)
                
                if total_removed > 0 or orphaned_contexts:
                    logger.debug(f"Cleaned up {total_removed} old metrics and {len(orphaned_contexts)} orphaned contexts")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get collector statistics."""
        total_metrics = sum(
            len(operations[op]) 
            for operations in self.metrics.values() 
            for op in operations
        )
        
        return {
            "is_running": self._is_running,
            "total_metrics": total_metrics,
            "active_timings": len([k for k in self.active_timings.keys() if not k.endswith(('_metadata', '_category', '_operation'))]),
            "categories": len(self.metrics),
            "operations": sum(len(operations) for operations in self.metrics.values()),
            "callbacks": len(self.metric_callbacks),
            "configuration": {
                "max_metrics_per_operation": self.max_metrics_per_operation,
                "cleanup_interval": self.cleanup_interval,
                "metric_retention_hours": self.metric_retention_seconds / 3600,
                "stats_cache_ttl": self.stats_cache_ttl,
            }
        }
