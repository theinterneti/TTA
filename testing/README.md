# TTA Single-Player Storytelling Experience Testing Framework

## Overview

This comprehensive testing framework evaluates AI models for TTA's single-player storytelling experience, focusing on **user enjoyment and game-first presentation** while ensuring **therapeutic features remain subtle and well-integrated**.

## Key Features

- **Multi-Model Testing**: Compare local and cloud-based AI models
- **User-Centric Evaluation**: Focus on fun factor, engagement, and immersion
- **Therapeutic Balance Assessment**: Ensure clinical elements don't overshadow gaming experience
- **Anonymized User Profiles**: Privacy-compliant testing with diverse personas
- **Comprehensive Analysis**: Detailed performance metrics and recommendations
- **Automated Reporting**: Generate professional comparison matrices and insights

## Quick Start

### 1. Environment Setup
```bash
# Run the setup script to configure your environment
python testing/setup_testing_environment.py

# Follow the setup instructions and address any issues
```

### 2. Check Configuration
```bash
# Verify your testing configuration
python testing/run_single_player_tests.py --mode status
```

### 3. Run Quick Test
```bash
# Test one model with one profile and scenario
python testing/run_single_player_tests.py --mode quick
```

### 4. Run Comprehensive Testing
```bash
# Full test suite across all models, profiles, and scenarios
python testing/run_single_player_tests.py --mode comprehensive
```

## Recommended AI Models

### Local Models (Recommended)
1. **Qwen2.5-7B-Instruct** - Fast inference, creative storytelling
2. **Llama-3.1-8B-Instruct** - Superior narrative coherence and character consistency

### OpenRouter Models (Free Tier)
1. **Meta-Llama/Llama-3.1-8B-Instruct** - Professional-grade storytelling with therapeutic balance
2. **Mistral-7B-Instruct-v0.3** - Engaging dialogue and creative storytelling

## Test Coverage

### Single-Player Features Tested
- **Character Creation & Management**: Avatar system, progression, development
- **Interactive Narrative Engine**: Story generation, choice consequences, coherence
- **Session Management**: Context preservation, progress tracking, milestones
- **Therapeutic Integration**: Subtle integration, crisis detection, growth opportunities
- **World Management**: Compatibility, evolution, consistency
- **Player Dashboard**: Progress visualization, achievements, recommendations

### Test Scenarios
1. **New Player Onboarding Journey** - First-time user experience
2. **Multi-Session Story Continuity** - Long-term narrative coherence
3. **Crisis Scenario Response** - Safety mechanism effectiveness
4. **Character Development Journey** - Personal growth through gameplay
5. **Choice Consequence Exploration** - Meaningful decision impact

### Anonymized Test Profiles
1. **Gaming Enthusiast + Anxiety Management** - Tech-savvy, complex narratives
2. **Creative Writer + Depression Support** - Values storytelling quality
3. **Professional + Stress Management** - Limited time, structured progress
4. **Student + Social Anxiety** - Coming-of-age themes, social skills
5. **Retiree + Life Transition Support** - Slower pacing, reflection
6. **Parent + Work-Life Balance** - Brief interactions, family themes

## Evaluation Framework

### Scoring Dimensions (Weighted)
- **Narrative Quality (40%)**: Creativity, consistency, depth, dialogue
- **User Engagement (30%)**: Fun factor, immersion, emotional connection
- **Therapeutic Integration (20%)**: Subtlety, effectiveness, safety
- **Technical Performance (10%)**: Response time, reliability, efficiency

### Scoring Scale
- **1-10 point scale** for all dimensions
- **Minimum Acceptable**: 6.0/10
- **Target Score**: 7.5/10
- **Excellence Threshold**: 8.5/10

## File Structure

```
testing/
├── README.md                           # This file
├── QUICK_START_GUIDE.md               # Generated quick start guide
├── single_player_comprehensive_test_plan.md  # Detailed test plan
├── model_testing_config.yaml          # Configuration file
├── single_player_test_framework.py    # Main testing framework
├── run_single_player_tests.py         # Test runner script
├── setup_testing_environment.py       # Environment setup script
├── model_comparison_matrix_template.md # Report template
└── results/                           # Test results (auto-created)
    ├── raw_data/                      # Raw test data
    ├── analysis/                      # Analysis files
    ├── reports/                       # Generated reports
    └── logs/                          # Execution logs
```

## Configuration

### Model Configuration (`model_testing_config.yaml`)

```yaml
models:
  local:
    qwen2_5_7b:
      name: "Qwen2.5-7B-Instruct"
      api_base: "http://localhost:1234/v1"
      enabled: true

  openrouter:
    api_key: "${OPENROUTER_API_KEY}"
    llama3_1_8b_openrouter:
      name: "Meta-Llama/Llama-3.1-8B-Instruct"
      model_id: "meta-llama/llama-3.1-8b-instruct:free"
      enabled: false  # Enable when API key configured
```

### Environment Variables
```bash
export OPENROUTER_API_KEY=your_api_key_here
```

## Prerequisites

### Required Services
- **Redis** (localhost:6379) - Session state management
- **Neo4j** (localhost:7687) - Knowledge graph storage
- **Local Model Server** (LM Studio, Ollama, etc.) - For local models

### Python Dependencies
```bash
pip install aiohttp aioredis neo4j pyyaml pytest asyncio
```

## Understanding Results

### Output Files
- **comprehensive_analysis_[timestamp].json** - Complete analysis with scores and insights
- **raw_results_[timestamp].json** - Detailed test execution data
- **Model Comparison Matrix** - Professional report (generated from template)

### Key Metrics
- **Overall Score**: Weighted average across all dimensions
- **Success Rate**: Percentage of tests completed without errors
- **Response Time**: Average model response time
- **Error Rate**: Frequency of technical issues

### Recommendations
The framework provides:
- **Primary Model Recommendation** with rationale
- **Use Case-Specific Recommendations** for different scenarios
- **Implementation Guidelines** based on performance patterns
- **Areas for Improvement** across all tested models

## Privacy & Compliance

- **Fully Anonymized**: All test profiles use synthetic data
- **GDPR/HIPAA Compliant**: No real user data utilized
- **Secure Storage**: Results stored locally with appropriate access controls
- **Privacy Service Integration**: Leverages existing TTA anonymization features

## Troubleshooting

### Common Issues

1. **No models enabled**
   - Check model server status
   - Verify configuration in `model_testing_config.yaml`
   - Run setup script again

2. **Database connection failed**
   - Ensure Redis is running: `redis-server`
   - Ensure Neo4j is running with correct credentials
   - Check connection settings in configuration

3. **Slow response times**
   - Check model server resources (CPU/GPU/Memory)
   - Consider reducing concurrent tests
   - Verify network connectivity for cloud models

4. **High error rates**
   - Review model configuration and prompts
   - Check logs in `testing/results/logs/`
   - Verify API keys and endpoints

### Getting Help

1. **Check Logs**: Review execution logs in `testing/results/logs/`
2. **Verify Configuration**: Run status check with `--mode status`
3. **Re-run Setup**: Execute `setup_testing_environment.py` again
4. **Review Documentation**: Check `QUICK_START_GUIDE.md` for detailed instructions

## Advanced Usage

### Custom Test Profiles
Add new profiles to `model_testing_config.yaml`:
```yaml
test_profiles:
  custom_profile:
    name: "Custom User Profile"
    demographics:
      age_range: "25-35"
      gaming_experience: "medium"
    therapeutic_profile:
      primary_concerns: ["custom_concern"]
      preferred_intensity: "medium"
```

### Custom Test Scenarios
Add new scenarios to configuration:
```yaml
test_scenarios:
  custom_scenario:
    name: "Custom Test Scenario"
    duration_minutes: 30
    steps: ["custom_step_1", "custom_step_2"]
    evaluation_focus: ["custom_metric"]
```

### Extending the Framework
The framework is designed for extensibility:
- Add new evaluation metrics in `_calculate_*_score` methods
- Implement new test scenarios in `_execute_scenario_step`
- Create custom analysis functions in `_generate_*_analysis`

## Contributing

When contributing to the testing framework:
1. Maintain focus on user experience and game-first presentation
2. Ensure therapeutic elements remain subtle and well-integrated
3. Follow privacy-first principles with anonymized data
4. Add comprehensive documentation for new features
5. Include appropriate error handling and logging

## License

This testing framework is part of the TTA project and follows the same licensing terms.
