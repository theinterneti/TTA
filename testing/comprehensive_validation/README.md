# Narrative Coherence Validation Component

**Component Type:** Testing Infrastructure
**Status:** Development → Staging Promotion Candidate
**Owner:** theinterneti
**Created:** 2025-10-08

---

## Overview

The Narrative Coherence Validation component is a comprehensive testing framework for evaluating the TTA system's AI storytelling quality against production readiness criteria. It provides automated assessment of narrative coherence, world consistency, and user engagement across diverse story genres.

## Purpose

This component validates that the TTA system's narrative generation capabilities meet established quality targets:
- **Narrative Coherence:** ≥7.5/10 (character consistency, plot logic, temporal consistency)
- **World Consistency:** ≥7.5/10 (setting consistency, rules consistency)
- **User Engagement:** ≥7.0/10 (choice meaningfulness, narrative pacing)

## Features

### Core Capabilities
- **Multi-Scenario Testing:** Validates narrative quality across Fantasy, Mystery, Sci-Fi, and Therapeutic genres
- **Comprehensive Metrics:** Evaluates 7 quality dimensions with detailed scoring
- **Qualitative Analysis:** Extracts specific examples of narrative strengths and weaknesses
- **Production Readiness Assessment:** Determines if system meets quality targets for deployment
- **Automated Reporting:** Generates detailed JSON and Markdown reports

### Quality Metrics

**Narrative Coherence (8 sub-metrics):**
- Character consistency
- Plot logic
- Temporal consistency

**World Consistency (2 sub-metrics):**
- Setting consistency
- Rules consistency

**User Engagement (2 sub-metrics):**
- Choice meaningfulness
- Narrative pacing

## Installation

No additional dependencies required beyond the standard TTA testing framework.

```bash
# Ensure you're in the TTA project root
cd /home/thein/recovered-tta-storytelling

# The component is ready to use
```

## Usage

### Basic Usage

```bash
# Run comprehensive narrative coherence validation
uvx python testing/comprehensive_validation/narrative_coherence_validation.py
```

### Programmatic Usage

```python
import asyncio
from testing.comprehensive_validation.narrative_coherence_validation import (
    NarrativeCoherenceValidator
)

async def main():
    validator = NarrativeCoherenceValidator()
    report = await validator.run_comprehensive_validation()

    print(f"Average Coherence: {report['aggregate_metrics']['average_narrative_coherence']}/10")
    print(f"Production Ready: {report['production_readiness']['production_ready']}")

asyncio.run(main())
```

### Customizing Test Scenarios

```python
from testing.comprehensive_validation.narrative_coherence_validation import (
    NarrativeCoherenceValidator,
    TestScenario
)

validator = NarrativeCoherenceValidator()

# Add custom scenario
custom_scenario = TestScenario(
    name="Horror Survival",
    description="Psychological horror with tension management",
    genre="horror",
    initial_prompt="I'm trapped in an abandoned hospital with strange occurrences.",
    expected_elements=["tension building", "atmosphere", "psychological elements"],
    test_turns=20
)

validator.test_scenarios.append(custom_scenario)
```

## Output

### Generated Artifacts

**JSON Report:**
- Location: `testing/results/narrative_coherence_validation/validation_report_YYYYMMDD_HHMMSS.json`
- Contains: Detailed metrics, scenario results, production readiness assessment

**Markdown Reports:**
- `NARRATIVE_COHERENCE_VALIDATION_REPORT.md` - Comprehensive validation report
- `NARRATIVE_COHERENCE_VALIDATION_SUMMARY.md` - Quick reference summary

### Sample Output

```json
{
  "validation_timestamp": "2025-10-08T10:39:49.227308",
  "quality_targets": {
    "narrative_coherence": 7.5,
    "world_consistency": 7.5,
    "user_engagement": 7.0
  },
  "aggregate_metrics": {
    "average_narrative_coherence": 8.12,
    "average_world_consistency": 7.78,
    "average_user_engagement": 7.32,
    "scenarios_tested": 4,
    "scenarios_passing": 4,
    "overall_pass_rate": 100.0
  },
  "production_readiness": {
    "meets_coherence_target": true,
    "meets_consistency_target": true,
    "meets_engagement_target": true,
    "production_ready": true
  }
}
```

## Configuration

### Quality Targets

Modify quality targets in the validator initialization:

```python
validator = NarrativeCoherenceValidator()
validator.quality_targets = {
    "narrative_coherence": 8.0,  # Raise target to 8.0
    "world_consistency": 8.0,
    "user_engagement": 7.5
}
```

### Test Scenarios

Default scenarios are defined in `_define_test_scenarios()`. Customize by:
1. Modifying existing scenarios
2. Adding new scenarios
3. Adjusting `test_turns` for longer/shorter sessions

## Integration

### CI/CD Integration

```yaml
# .github/workflows/narrative-quality-check.yml
name: Narrative Quality Check

on: [push, pull_request]

jobs:
  validate-narrative-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Narrative Coherence Validation
        run: |
          uvx python testing/comprehensive_validation/narrative_coherence_validation.py
      - name: Check Results
        run: |
          # Parse JSON report and fail if production_ready is false
          python -c "import json; report = json.load(open('testing/results/narrative_coherence_validation/validation_report_*.json')); exit(0 if report['production_readiness']['production_ready'] else 1)"
```

### Staging Environment

The component is designed to run in staging for ongoing quality monitoring:

```bash
# Run in staging environment
ENVIRONMENT=staging uvx python testing/comprehensive_validation/narrative_coherence_validation.py
```

## Testing

### Unit Tests

Currently, the component uses simulated narrative data for validation framework testing. Future enhancements will include:
- Unit tests for metric calculation logic
- Integration tests with live TTA system
- Regression tests for quality baselines

### Running Tests

```bash
# Run component tests (when available)
uv run pytest tests/test_narrative_coherence_validation.py -v
```

## Maintenance

### Regular Validation

Recommended schedule:
- **Development:** Run before major releases
- **Staging:** Run weekly for quality monitoring
- **Production:** Run monthly for quality assurance

### Updating Quality Targets

Quality targets should be reviewed quarterly based on:
- User feedback on narrative quality
- Comparison with industry standards
- System capability improvements

## Troubleshooting

### Common Issues

**Issue:** No test results generated
**Solution:** Check that output directory exists: `mkdir -p testing/results/narrative_coherence_validation`

**Issue:** Import errors
**Solution:** Ensure you're running from project root and virtual environment is activated

**Issue:** Simulated scores don't match expectations
**Solution:** This is expected - component uses simulated data. For real validation, integrate with live TTA system.

## Future Enhancements

- [ ] Integration with live TTA system (replace simulation)
- [ ] Extended session testing (50+ turns)
- [ ] Adversarial user behavior testing
- [ ] Multi-user concurrent narrative validation
- [ ] Real-time quality monitoring dashboard
- [ ] Automated quality regression detection

## Dependencies

**Core:**
- Python 3.12+
- asyncio (standard library)
- dataclasses (standard library)
- pathlib (standard library)

**Testing Framework:**
- Existing TTA testing infrastructure

## License

Part of the TTA (Therapeutic Text Adventure) project.

## Support

For issues or questions:
- Review validation reports in `testing/results/narrative_coherence_validation/`
- Check comprehensive documentation in `NARRATIVE_COHERENCE_VALIDATION_REPORT.md`
- Refer to TTA testing framework documentation

---

**Component Status:** Ready for Staging Promotion
**Last Updated:** 2025-10-08
**Version:** 1.0.0
