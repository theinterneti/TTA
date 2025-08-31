# Performance Monitoring Guidelines

This document outlines performance monitoring standards, metrics, and best practices for the TTA platform.

## 📊 Overview

Performance monitoring is critical for ensuring the TTA platform provides responsive, reliable therapeutic experiences. This guide covers monitoring strategies, key metrics, and optimization approaches.

## 🎯 Performance Objectives

### Response Time Targets
- **API Endpoints**: < 200ms (95th percentile)
- **Database Queries**: < 100ms (95th percentile)
- **LLM Responses**: < 2000ms (95th percentile)
- **Page Load Times**: < 1000ms (95th percentile)
- **Therapeutic Processing**: < 500ms (95th percentile)

### Throughput Targets
- **Concurrent Users**: 1000+ simultaneous sessions
- **API Requests**: 10,000+ requests per minute
- **Database Transactions**: 5,000+ per minute
- **Message Processing**: 1,000+ messages per minute

### Resource Utilization Limits
- **CPU Usage**: < 80% sustained
- **Memory Usage**: < 512MB per process
- **Disk I/O**: < 80% utilization
- **Network Bandwidth**: < 70% utilization

## 📈 Key Performance Metrics

### Application Metrics

#### Response Time Metrics
```python
# Example metrics collection
import time
from functools import wraps
from typing import Callable, Any

def monitor_performance(metric_name: str):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Record success metric
                record_metric(f"{metric_name}.duration", duration)
                record_metric(f"{metric_name}.success", 1)

                return result
            except Exception as e:
                duration = time.time() - start_time

                # Record error metric
                record_metric(f"{metric_name}.duration", duration)
                record_metric(f"{metric_name}.error", 1)

                raise
        return wrapper
    return decorator

@monitor_performance("therapeutic_assessment")
async def process_therapeutic_assessment(user_input: str) -> dict:
    """Process therapeutic assessment with monitoring."""
    # Implementation here
    pass
```

#### Throughput Metrics
- **Requests per second (RPS)**
- **Transactions per second (TPS)**
- **Messages processed per minute**
- **Active user sessions**

#### Error Rate Metrics
- **HTTP 4xx/5xx error rates**
- **Database connection failures**
- **LLM API timeouts**
- **Therapeutic processing errors**

### System Metrics

#### CPU and Memory
```python
import psutil
import asyncio
from typing import Dict

class SystemMonitor:
    """Monitor system resource usage."""

    def __init__(self):
        self.metrics = {}

    async def collect_system_metrics(self) -> Dict[str, float]:
        """Collect current system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": self._get_network_io(),
            "process_count": len(psutil.pids()),
            "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
        }

    def _get_network_io(self) -> Dict[str, int]:
        """Get network I/O statistics."""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
```

#### Database Performance
```python
import time
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

class DatabaseMonitor:
    """Monitor database performance."""

    @asynccontextmanager
    async def monitor_query(self, query_name: str):
        """Context manager to monitor database queries."""
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time
            record_metric(f"db.{query_name}.duration", duration)
            record_metric(f"db.{query_name}.success", 1)
        except Exception as e:
            duration = time.time() - start_time
            record_metric(f"db.{query_name}.duration", duration)
            record_metric(f"db.{query_name}.error", 1)
            raise

# Usage example
async def get_user_profile(user_id: str, session: AsyncSession):
    """Get user profile with monitoring."""
    db_monitor = DatabaseMonitor()

    async with db_monitor.monitor_query("get_user_profile"):
        result = await session.execute(
            select(UserProfile).where(UserProfile.id == user_id)
        )
        return result.scalar_one_or_none()
```

## 🔧 Monitoring Tools and Setup

### Prometheus Integration
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
REQUEST_COUNT = Counter(
    'tta_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'tta_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_SESSIONS = Gauge(
    'tta_active_sessions',
    'Number of active user sessions'
)

THERAPEUTIC_PROCESSING_TIME = Histogram(
    'tta_therapeutic_processing_seconds',
    'Time spent processing therapeutic content',
    ['intervention_type']
)

class PrometheusMonitor:
    """Prometheus metrics collection."""

    def __init__(self, port: int = 8000):
        self.port = port
        start_http_server(port)

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics."""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def update_active_sessions(self, count: int):
        """Update active sessions gauge."""
        ACTIVE_SESSIONS.set(count)

    def record_therapeutic_processing(self, intervention_type: str, duration: float):
        """Record therapeutic processing time."""
        THERAPEUTIC_PROCESSING_TIME.labels(intervention_type=intervention_type).observe(duration)
```

### Logging Configuration
```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class PerformanceLogger:
    """Structured logging for performance monitoring."""

    def __init__(self):
        self.logger = logging.getLogger("performance")
        self.logger.setLevel(logging.INFO)

        # JSON formatter for structured logs
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": %(message)s}'
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_performance_event(self, event_type: str, metrics: Dict[str, Any]):
        """Log performance event with structured data."""
        log_data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
        self.logger.info(json.dumps(log_data))

    def log_slow_query(self, query: str, duration: float, threshold: float = 0.1):
        """Log slow database queries."""
        if duration > threshold:
            self.log_performance_event("slow_query", {
                "query": query[:100] + "..." if len(query) > 100 else query,
                "duration": duration,
                "threshold": threshold
            })
```

## 🚨 Alerting and Thresholds

### Alert Definitions
```yaml
# alerts.yml - Example alert configuration
groups:
  - name: tta_performance
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, tta_request_duration_seconds) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(tta_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighCPUUsage
        expr: cpu_percent > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"

      - alert: HighMemoryUsage
        expr: memory_percent > 85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"
```

### Notification Channels
```python
import asyncio
import aiohttp
from typing import Dict, Any

class AlertManager:
    """Manage performance alerts and notifications."""

    def __init__(self, webhook_url: str, slack_token: str = None):
        self.webhook_url = webhook_url
        self.slack_token = slack_token

    async def send_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Send performance alert notification."""
        alert_data = {
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "TTA"
        }

        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=alert_data)

    async def check_performance_thresholds(self, metrics: Dict[str, float]):
        """Check metrics against thresholds and send alerts."""
        if metrics.get("response_time_95th", 0) > 0.2:
            await self.send_alert(
                "high_response_time",
                f"95th percentile response time: {metrics['response_time_95th']:.3f}s",
                "warning"
            )

        if metrics.get("error_rate", 0) > 0.05:
            await self.send_alert(
                "high_error_rate",
                f"Error rate: {metrics['error_rate']:.2%}",
                "critical"
            )

        if metrics.get("cpu_percent", 0) > 80:
            await self.send_alert(
                "high_cpu_usage",
                f"CPU usage: {metrics['cpu_percent']:.1f}%",
                "warning"
            )
```

## 📊 Performance Dashboards

### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "TTA Performance Dashboard",
    "panels": [
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, tta_request_duration_seconds)",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, tta_request_duration_seconds)",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(tta_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(tta_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors/sec"
          }
        ]
      },
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "cpu_percent",
            "legendFormat": "CPU %"
          },
          {
            "expr": "memory_percent",
            "legendFormat": "Memory %"
          }
        ]
      }
    ]
  }
}
```

## 🔍 Performance Testing

### Load Testing with Locust
```python
from locust import HttpUser, task, between
import json

class TTAUser(HttpUser):
    """Simulate TTA user behavior for load testing."""

    wait_time = between(1, 3)

    def on_start(self):
        """Setup user session."""
        self.client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })

    @task(3)
    def send_message(self):
        """Send therapeutic message."""
        self.client.post("/api/v1/chat/message", json={
            "message": "I'm feeling anxious today",
            "session_id": "test_session"
        })

    @task(1)
    def get_profile(self):
        """Get user profile."""
        self.client.get("/api/v1/user/profile")

    @task(1)
    def get_history(self):
        """Get conversation history."""
        self.client.get("/api/v1/chat/history")
```

### Benchmark Testing
```python
import asyncio
import time
from typing import List, Dict
import statistics

class PerformanceBenchmark:
    """Benchmark performance of critical functions."""

    async def benchmark_function(self, func, *args, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark a function's performance."""
        durations = []

        for _ in range(iterations):
            start_time = time.time()
            await func(*args)
            duration = time.time() - start_time
            durations.append(duration)

        return {
            "mean": statistics.mean(durations),
            "median": statistics.median(durations),
            "p95": statistics.quantiles(durations, n=20)[18],  # 95th percentile
            "p99": statistics.quantiles(durations, n=100)[98],  # 99th percentile
            "min": min(durations),
            "max": max(durations),
            "std_dev": statistics.stdev(durations)
        }

    async def run_benchmarks(self):
        """Run all performance benchmarks."""
        results = {}

        # Benchmark therapeutic processing
        results["therapeutic_processing"] = await self.benchmark_function(
            process_therapeutic_input, "I'm feeling stressed"
        )

        # Benchmark database queries
        results["user_lookup"] = await self.benchmark_function(
            get_user_profile, "test_user_id"
        )

        return results
```

## 🎯 Performance Optimization Strategies

### Caching Strategies
```python
from functools import lru_cache
import redis
import json
from typing import Optional, Any

class PerformanceCache:
    """Multi-level caching for performance optimization."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    @lru_cache(maxsize=1000)
    def get_cached_assessment(self, user_profile_hash: str) -> Optional[Dict]:
        """In-memory cache for frequent assessments."""
        # This will be cached in memory
        return self._compute_assessment(user_profile_hash)

    async def get_cached_user_data(self, user_id: str) -> Optional[Dict]:
        """Redis cache for user data."""
        cached = await self.redis.get(f"user:{user_id}")
        if cached:
            return json.loads(cached)
        return None

    async def set_cached_user_data(self, user_id: str, data: Dict, ttl: int = 3600):
        """Cache user data in Redis."""
        await self.redis.setex(
            f"user:{user_id}",
            ttl,
            json.dumps(data)
        )
```

### Database Optimization
```python
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

class OptimizedQueries:
    """Optimized database queries for better performance."""

    async def get_user_with_sessions(self, user_id: str, session: AsyncSession):
        """Efficiently load user with related sessions."""
        # Use selectinload to avoid N+1 queries
        result = await session.execute(
            select(User)
            .options(selectinload(User.therapeutic_sessions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_session_statistics(self, user_id: str, session: AsyncSession):
        """Get aggregated session statistics efficiently."""
        result = await session.execute(
            select(
                func.count(TherapeuticSession.id).label('total_sessions'),
                func.avg(TherapeuticSession.duration).label('avg_duration'),
                func.max(TherapeuticSession.created_at).label('last_session')
            )
            .where(TherapeuticSession.user_id == user_id)
        )
        return result.first()
```

## 📋 Performance Review Process

### Regular Performance Reviews
1. **Daily**: Monitor key metrics and alerts
2. **Weekly**: Review performance trends and identify issues
3. **Monthly**: Conduct comprehensive performance analysis
4. **Quarterly**: Performance optimization planning and implementation

### Performance Testing Schedule
- **Pre-deployment**: Load testing for all releases
- **Weekly**: Automated performance regression tests
- **Monthly**: Comprehensive benchmark testing
- **Quarterly**: Stress testing and capacity planning

## 🎯 Continuous Improvement

### Performance Optimization Workflow
1. **Identify**: Use monitoring to identify performance bottlenecks
2. **Analyze**: Deep dive into root causes
3. **Plan**: Develop optimization strategy
4. **Implement**: Make performance improvements
5. **Validate**: Measure improvement impact
6. **Monitor**: Ensure sustained performance gains

### Performance Culture
- Regular performance discussions in team meetings
- Performance considerations in code reviews
- Performance training and knowledge sharing
- Recognition for performance improvements

---

## 📚 Resources

### Tools and Libraries
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Performance dashboards and visualization
- **Locust**: Load testing framework
- **py-spy**: Python performance profiling
- **asyncio-mqtt**: Async monitoring integration

### Best Practices References
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [FastAPI Performance](https://fastapi.tiangolo.com/advanced/performance/)
- [Database Performance Tuning](https://use-the-index-luke.com/)
- [Monitoring Best Practices](https://prometheus.io/docs/practices/)

---

*Performance monitoring is an ongoing process. Regular review and optimization ensure the TTA platform continues to provide excellent user experiences.*
