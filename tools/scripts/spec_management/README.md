# TTA Specification Management Tools

This directory contains comprehensive tools for managing TTA project specifications, ensuring quality, alignment, and consistency across all documentation.

## 🎯 Overview

The TTA Specification Management System provides:

- **Standardized Templates**: Consistent specification format across all domains
- **Automated Validation**: Pre-commit hooks and CI/CD integration for quality assurance
- **Alignment Checking**: Verification that specifications match implementations
- **Quality Metrics**: Scoring system for specification completeness and health
- **Interactive Creation**: CLI wizard for guided specification creation

## 📁 Components

### Core Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `spec_validator.py` | Validates specifications against templates | `python spec_validator.py .kiro/specs --recursive` |
| `spec_wizard.py` | Interactive specification creation | `python spec_wizard.py` |
| `alignment_checker.py` | Checks spec-implementation alignment | `python alignment_checker.py --report` |
| `quality_metrics.py` | Calculates quality scores | `python quality_metrics.py --report` |

### Configuration Files

| File | Purpose |
|------|---------|
| `.kiro/templates/specification-template.md` | Standard specification template |
| `.kiro/templates/specification-metadata.yaml` | Metadata template for automation |
| `.kiro/config/quality-standards.yaml` | Quality standards and thresholds |

### CI/CD Integration

| File | Purpose |
|------|---------|
| `.github/workflows/specification-management.yml` | GitHub Actions workflow |
| `.pre-commit-config.yaml` | Pre-commit hooks configuration |

## 🚀 Quick Start

### 1. Create a New Specification

```bash
# Interactive mode (recommended)
python scripts/spec_management/spec_wizard.py

# Non-interactive mode
python scripts/spec_management/spec_wizard.py \
  --name "My New Feature" \
  --category "therapeutic-systems" \
  --owner "developer@example.com" \
  --no-interactive
```

### 2. Validate Existing Specifications

```bash
# Validate all specifications
python scripts/spec_management/spec_validator.py .kiro/specs --recursive

# Validate specific file
python scripts/spec_management/spec_validator.py .kiro/specs/my-spec/my-spec-specification.md

# Validate metadata files
python scripts/spec_management/spec_validator.py .kiro/specs --metadata --recursive
```

### 3. Check Quality Metrics

```bash
# Generate comprehensive quality report
python scripts/spec_management/quality_metrics.py --report

# Check specific specification
python scripts/spec_management/quality_metrics.py --spec .kiro/specs/my-spec/my-spec-specification.md

# JSON output for automation
python scripts/spec_management/quality_metrics.py --report --json
```

### 4. Verify Alignment

```bash
# Full alignment check
python scripts/spec_management/alignment_checker.py --report

# Check specific files (pre-commit mode)
python scripts/spec_management/alignment_checker.py --pre-commit src/my_file.py .kiro/specs/my-spec.md

# JSON output
python scripts/spec_management/alignment_checker.py --report --json
```

## 📊 Quality Standards

### Scoring System

Specifications are scored on four dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Completeness** | 40% | Required sections and content depth |
| **Alignment** | 30% | Implementation references and status accuracy |
| **Freshness** | 20% | Last update and review schedule |
| **Validation** | 10% | Test coverage and acceptance criteria |

### Grade Scale

| Grade | Score Range | Description |
|-------|-------------|-------------|
| A | 90-100 | Excellent - Exemplary specification |
| B | 80-89 | Good - Meets all standards |
| C | 70-79 | Acceptable - Minor improvements needed |
| D | 60-69 | Needs Improvement - Significant gaps |
| F | 0-59 | Failing - Major issues require attention |

### Category-Specific Standards

Different specification categories have tailored requirements:

- **Therapeutic Systems**: Higher standards (95% for Grade A) due to safety requirements
- **Web Interfaces**: Accessibility and authentication documentation required
- **Infrastructure**: Deployment and monitoring documentation required
- **AI Orchestration**: Agent architecture and performance metrics required
- **Shared Components**: API documentation and usage examples required

## 🔧 Development Workflow Integration

### Pre-commit Hooks

The system integrates with pre-commit hooks to validate specifications automatically:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-specifications
      name: Validate TTA Specifications
      entry: python scripts/spec_management/spec_validator.py
      language: system
      files: \.kiro/specs/.*\.md$
```

### GitHub Actions

Automated workflows run on every pull request:

- **Specification Validation**: Ensures all specs meet template requirements
- **Quality Metrics**: Calculates and reports quality scores
- **Alignment Checking**: Verifies spec-implementation consistency
- **Critical System Checks**: Enforces specification updates for therapeutic systems

### IDE Integration

For enhanced developer experience:

- Real-time quality scoring in VS Code
- Inline improvement suggestions
- Template auto-completion
- Reference validation

## 📈 Monitoring and Reporting

### Quality Dashboard

The system provides comprehensive reporting:

- Overall quality trends
- Category performance analysis
- Specification health indicators
- Improvement recommendations

### Automated Notifications

Notifications are triggered for:

- Quality score drops (>10 points)
- Stale specifications (>90 days)
- Critical system issues
- Missing specifications

## 🛠️ Configuration

### Quality Standards

Customize quality standards in `.kiro/config/quality-standards.yaml`:

```yaml
quality_standards:
  score_thresholds:
    excellent: 90
    good: 80
    acceptable: 70
  
  scoring_weights:
    completeness: 0.4
    alignment: 0.3
    freshness: 0.2
    validation: 0.1
```

### Category Standards

Define category-specific requirements:

```yaml
category_standards:
  therapeutic-systems:
    score_thresholds:
      excellent: 95
    additional_requirements:
      - safety_validation_refs: true
      - crisis_handling_docs: true
```

## 🔍 Troubleshooting

### Common Issues

1. **Template Validation Failures**
   - Ensure all required sections are present
   - Check status indicator format
   - Verify implementation references

2. **Alignment Check Failures**
   - Update implementation file paths
   - Verify API endpoint references
   - Check for placeholder content (TBD, TODO)

3. **Quality Score Issues**
   - Add missing content sections
   - Update stale documentation
   - Include test references and acceptance criteria

### Debug Mode

Enable verbose output for detailed diagnostics:

```bash
python scripts/spec_management/spec_validator.py .kiro/specs --verbose
python scripts/spec_management/alignment_checker.py --report --verbose
```

## 📚 Best Practices

### Specification Creation

1. **Use the Wizard**: Always start with `spec_wizard.py` for consistency
2. **Choose Appropriate Category**: Select the most specific category
3. **Assign Clear Ownership**: Ensure someone is responsible for maintenance
4. **Set Realistic Priorities**: Use priority levels to guide review schedules

### Maintenance

1. **Regular Reviews**: Schedule quarterly reviews for all specifications
2. **Update with Changes**: Modify specifications alongside code changes
3. **Monitor Quality**: Track quality metrics and address declining scores
4. **Validate References**: Ensure all file and API references remain valid

### Team Collaboration

1. **Consistent Templates**: Always use standardized templates
2. **Clear Status Indicators**: Keep status indicators current and accurate
3. **Comprehensive Testing**: Include thorough test coverage documentation
4. **Accessible Language**: Write for diverse technical backgrounds

## 🤝 Contributing

To contribute to the specification management system:

1. Follow existing code patterns and documentation standards
2. Add tests for new functionality
3. Update this README for new features
4. Ensure backward compatibility with existing specifications

## 📄 License

This specification management system is part of the TTA project and follows the same licensing terms.
