# AI Development Toolkit

Reusable development infrastructure for AI projects.

## What's Included

### Workflow Primitives (tta-workflow-primitives)
- Router, Cache, Timeout, Retry patterns
- Composition operators
- 30-40% cost optimization

### Development Primitives (dev-primitives)
- Error recovery patterns
- Development utilities

### OpenHands Integration Tools
- Testing and validation framework
- Batch execution
- Diagnostics and monitoring

### Monitoring & Observability
- Prometheus/Grafana integration
- Component maturity tracking
- Development metrics

### Workflow Management
- Quality gates
- Stage handlers
- Spec-to-production automation

## Quick Start

```bash
# Install the toolkit
pip install -e packages/ai-dev-toolkit

# Or use individual packages
pip install -e packages/tta-workflow-primitives
pip install -e packages/dev-primitives
```

## Documentation

See `docs/` for complete documentation:
- [Agentic Primitives](../../docs/agentic-primitives/)
- [OpenHands Tools](../../docs/development/OPENHANDS_DEV_TOOLS.md)
- [Monitoring](../../docs/guides/MONITORING_QUICKSTART.md)

## Components

This toolkit bundles:
1. **tta-workflow-primitives** - Core workflow patterns
2. **dev-primitives** - Development utilities
3. **Scripts** - Development automation
4. **Monitoring** - Observability stack

## Usage

### Workflow Primitives
```python
from tta_workflow_primitives.core import RouterPrimitive
from tta_workflow_primitives.performance import CachePrimitive

workflow = (
    RouterPrimitive(routes={'fast': local, 'premium': openai}) >>
    CachePrimitive(processor, ttl_seconds=3600)
)
```

### OpenHands Tools
```bash
# Test workflows
python scripts/test_openhands_workflow.py

# Run batch execution
python scripts/phase7_batch_execution_final.py

# Monitor progress
python scripts/monitor_batch_progress.py
```

### Monitoring
```bash
# Start monitoring stack
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# View dashboards
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

## Benefits

- ✅ Reusable across AI projects
- ✅ Production-ready patterns
- ✅ 30-40% cost reduction
- ✅ Comprehensive testing
- ✅ Full observability

## License

MIT
