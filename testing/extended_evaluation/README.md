# TTA Extended Session Quality Evaluation Framework

A comprehensive testing framework for evaluating the TTA storytelling system through extended sessions (20-50+ turns) with focus on living worlds consistency, narrative coherence, and user engagement over time.

## Overview

This framework extends the existing TTA testing infrastructure to provide:

- **Extended Session Testing**: 20-50+ turn story sessions with realistic user simulation
- **Living Worlds Evaluation**: Comprehensive assessment of world state consistency and evolution
- **Narrative Quality Analysis**: Advanced analysis of story coherence, character development, and creative quality
- **User Engagement Simulation**: Sophisticated behavioral modeling for realistic testing
- **Comprehensive Data Collection**: Detailed logging and monitoring of all aspects of system performance
- **Advanced Analytics**: Pattern recognition, trend analysis, and quality baseline establishment

## Key Features

### 1. Extended Session Scenarios
- **Epic Fantasy Adventure**: 35 turns, complex world-building
- **Modern Mystery Investigation**: 28 turns, psychological elements
- **Sci-Fi Space Exploration**: 42 turns, ethical dilemmas
- **Slice of Life Drama**: 25 turns, strong therapeutic integration

### 2. Enhanced User Profiles
- **Analytical Gamer**: Methodical, enjoys complex decisions
- **Creative Storyteller**: Imaginative, adds creative elements
- **Cautious Explorer**: Careful, prefers safe choices
- **Goal-Oriented Achiever**: Focused on objectives and efficiency

### 3. Comprehensive Metrics
- **Narrative Coherence**: Character consistency, plot logic, world consistency
- **World State Management**: State persistence, choice impact tracking, world evolution
- **User Engagement**: Choice meaningfulness, narrative immersion, pacing quality
- **Technical Performance**: Response time, error rate, memory efficiency

### 4. Advanced Analysis
- **Quality Trend Analysis**: Track quality changes over extended sessions
- **Pattern Recognition**: Identify system strengths and limitations
- **Comparative Analysis**: Compare models across different scenarios and profiles
- **Baseline Establishment**: Set quantitative benchmarks for future improvements

## Architecture

```
ExtendedSessionTestFramework (Main Orchestrator)
├── SimulatedUserProfile (Behavioral Modeling)
├── LivingWorldsEvaluator (World State Analysis)
├── NarrativeAnalyzer (Story Quality Assessment)
├── ComprehensiveDataCollector (Data Logging)
└── QualityAnalysisReporter (Analysis & Reporting)
```

## Installation and Setup

### Prerequisites
- Python 3.8+
- TTA system dependencies
- Additional packages: `matplotlib`, `pandas`, `numpy`, `psutil`

### Installation
```bash
# Install additional dependencies
pip install matplotlib pandas numpy psutil

# Ensure TTA system is properly configured
# (Follow main TTA setup instructions)
```

### Configuration
The framework uses `testing/configs/extended_evaluation_config.yaml` for configuration:

```yaml
# Key configuration sections:
extended_scenarios:      # 20-50+ turn scenarios
enhanced_user_profiles:  # Sophisticated user behavior models
quality_metrics:         # Evaluation criteria and weights
data_collection:         # Logging and monitoring settings
```

## Usage

### Quick Start
```bash
# Check framework status
python testing/run_extended_evaluation.py --mode status

# Run a quick sample test (one model/profile/scenario)
python testing/run_extended_evaluation.py --mode quick-sample

# Run comprehensive evaluation (all combinations)
python testing/run_extended_evaluation.py --mode comprehensive

# Analyze existing data
python testing/run_extended_evaluation.py --mode analysis-only
```

### Command Line Options
- `--mode`: Evaluation mode (status, quick-sample, comprehensive, analysis-only)
- `--config`: Path to configuration file
- `--verbose`: Enable verbose logging
- `--force`: Skip confirmation prompts

### Expected Runtime
- **Quick Sample**: 30-60 minutes (1 test)
- **Comprehensive**: 8-24 hours (all combinations)
- **Analysis Only**: 5-15 minutes

## Output and Results

### Data Collection
Results are saved to `testing/results/extended_evaluation/`:
```
extended_evaluation/
├── session_[id]/
│   ├── session_summary.json      # Session overview
│   ├── turns.csv                 # Turn-by-turn metrics
│   └── detailed_turns.jsonl      # Detailed turn data
├── reports/
│   ├── [report_id].json          # Comprehensive analysis
│   └── visualizations/           # Charts and graphs
└── performance_history.csv       # System performance data
```

### Analysis Reports
Comprehensive reports include:
- **Model Performance Analysis**: Quality metrics, trends, strengths/weaknesses
- **Profile Performance Analysis**: How different user types perform with each model
- **Quality Baselines**: Established benchmarks for narrative coherence, world consistency, user engagement
- **Improvement Recommendations**: Actionable insights for system enhancement

### Visualizations
Generated charts include:
- Model performance comparisons
- Quality trends over extended sessions
- Profile-specific performance analysis
- System performance metrics

## Key Metrics

### Narrative Coherence (Weight: 35%)
- Character consistency across turns
- Plot logic and progression
- World consistency maintenance
- Temporal consistency

### World State Management (Weight: 25%)
- State persistence accuracy
- Choice impact tracking effectiveness
- World evolution naturalness

### User Engagement (Weight: 25%)
- Choice meaningfulness
- Narrative immersion quality
- Pacing appropriateness

### Technical Performance (Weight: 15%)
- Response time consistency
- Error rate minimization
- Memory usage efficiency

## Success Criteria

### Quality Thresholds
- **Narrative Coherence**: ≥8.5/10 (Excellence), ≥6.0/10 (Minimum)
- **World Consistency**: ≥8.8/10 (Excellence), ≥7.0/10 (Minimum)
- **User Engagement**: ≥8.0/10 (Excellence), ≥6.5/10 (Minimum)
- **Technical Performance**: ≥8.5/10 (Excellence), ≥7.0/10 (Minimum)

### Extended Session Goals
- Maintain narrative coherence above 8.0/10 over 50+ turns
- Achieve world state consistency above 9.0/10 throughout sessions
- Keep user engagement simulation above 7.5/10 average
- Zero critical errors or system failures

## Integration with TTA System

The framework integrates with existing TTA components:
- **Session Management**: Uses existing session lifecycle management
- **World State System**: Leverages living worlds infrastructure
- **Neo4j/Redis**: Utilizes existing persistence layers
- **Privacy Service**: Maintains anonymization compliance
- **Model Configuration**: Extends existing model management

## Extending the Framework

### Adding New Scenarios
1. Define scenario in `extended_evaluation_config.yaml`
2. Specify turn count, decision points, and milestones
3. Set evaluation criteria and success metrics

### Adding New User Profiles
1. Create profile in configuration with behavioral patterns
2. Define decision-making style, interaction preferences
3. Set demographic and therapeutic characteristics

### Adding New Metrics
1. Extend evaluator classes with new metric calculations
2. Update configuration weights and thresholds
3. Modify reporting to include new metrics

## Troubleshooting

### Common Issues
- **Memory Usage**: Extended sessions can be memory-intensive; monitor system resources
- **Long Runtime**: Comprehensive evaluation takes many hours; use quick-sample for testing
- **Configuration Errors**: Validate YAML syntax and required fields
- **Model Connectivity**: Ensure AI models are accessible and configured correctly

### Performance Optimization
- Reduce concurrent sessions for memory-constrained systems
- Use shorter scenarios for initial testing
- Enable performance monitoring to identify bottlenecks

## Contributing

When contributing to the extended evaluation framework:
1. Maintain compatibility with existing TTA infrastructure
2. Follow established patterns for data collection and analysis
3. Add comprehensive tests for new functionality
4. Update documentation for new features

## License

This framework is part of the TTA project and follows the same licensing terms.

---

For questions or support, refer to the main TTA documentation or contact the development team.
