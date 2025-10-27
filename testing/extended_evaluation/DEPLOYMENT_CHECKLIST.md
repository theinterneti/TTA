# TTA Extended Evaluation - Production Deployment Checklist

## 🚀 Pre-Deployment Setup

### ✅ Environment Setup
- [ ] **Python Environment**: Set up virtual environment
  ```bash
  ./testing/extended_evaluation/setup_venv.sh
  ```
- [ ] **Dependencies**: Verify all required packages installed
- [ ] **Permissions**: Ensure scripts are executable
- [ ] **Directories**: Create results and reports directories

### ✅ Configuration
- [ ] **Model Configuration**: Update `production_extended_evaluation.yaml` with your models
- [ ] **Database Connections**: Verify Neo4j and Redis connectivity
- [ ] **API Keys**: Ensure AI model API keys are configured
- [ ] **Resource Limits**: Set appropriate memory and timeout limits

### ✅ Integration Testing
- [ ] **Framework Status**: Run status check successfully
  ```bash
  python testing/run_extended_evaluation.py --mode status --config testing/configs/production_extended_evaluation.yaml
  ```
- [ ] **Quick Sample**: Complete one quick sample test
- [ ] **Data Collection**: Verify data is being saved correctly
- [ ] **Analysis**: Confirm analysis and reporting works

## 📊 Initial Baseline Establishment

### Phase 1: Single Model Baseline (4-6 hours)
**Objective**: Establish quality baselines with your most reliable model

**Configuration**:
```yaml
# Use only your best/most stable model
primary_models: ["your_most_reliable_model"]
scenarios: ["fantasy_baseline", "contemporary_baseline"]  # 2 scenarios
profiles: ["typical_user"]  # 1 profile
```

**Expected Tests**: 2 scenarios × 1 profile × 1 model = 2 tests

**Success Criteria**:
- [ ] All tests complete without critical errors
- [ ] Narrative coherence ≥ 7.0/10
- [ ] World consistency ≥ 7.5/10
- [ ] User engagement ≥ 6.5/10
- [ ] Technical performance ≥ 7.0/10

### Phase 2: Multi-Profile Testing (8-12 hours)
**Objective**: Test how different user types perform with your model

**Configuration**:
```yaml
primary_models: ["your_most_reliable_model"]
scenarios: ["fantasy_baseline", "contemporary_baseline"]
profiles: ["typical_user", "engaged_user"]  # 2 profiles
```

**Expected Tests**: 2 scenarios × 2 profiles × 1 model = 4 tests

**Success Criteria**:
- [ ] Consistent performance across user profiles
- [ ] No significant quality degradation with different user types
- [ ] Profile-specific insights generated

### Phase 3: Multi-Model Comparison (12-24 hours)
**Objective**: Compare performance across your available models

**Configuration**:
```yaml
primary_models: ["model_1", "model_2", "model_3"]  # Your models
scenarios: ["fantasy_baseline", "contemporary_baseline"]
profiles: ["typical_user", "engaged_user"]
```

**Expected Tests**: 2 scenarios × 2 profiles × 3 models = 12 tests

**Success Criteria**:
- [ ] Clear model rankings established
- [ ] Best performing model identified for each scenario type
- [ ] Performance differences documented

## 🎯 Model Configuration Recommendations

### Initial Baseline Settings
```yaml
# Conservative settings for reliable baselines
model_settings:
  temperature: 0.7          # Balanced creativity/consistency
  max_tokens: 2048         # Sufficient for detailed responses
  timeout_seconds: 30      # Reasonable timeout
  retry_attempts: 2        # Allow retries for reliability

# Resource management
extended_evaluation:
  max_concurrent_sessions: 1    # Start with 1 for stability
  session_timeout_minutes: 300  # 5 hours max
  checkpoint_interval_turns: 10 # Save progress frequently
```

### Model Selection Priority
1. **Primary Model**: Your most stable, production-ready model
2. **Backup Model**: Secondary model for comparison
3. **Experimental Models**: Only after baseline established

### Recommended Test Sequence
```bash
# 1. Status check
python testing/run_extended_evaluation.py --mode status --config testing/configs/production_extended_evaluation.yaml

# 2. Quick sample (30-60 min)
python testing/run_extended_evaluation.py --mode quick-sample --config testing/configs/production_extended_evaluation.yaml

# 3. Single model baseline (4-6 hours)
# Edit config to use only one model, then:
python testing/run_extended_evaluation.py --mode comprehensive --config testing/configs/production_extended_evaluation.yaml

# 4. Analysis
python testing/run_extended_evaluation.py --mode analysis-only
```

## 📈 Quality Metrics Interpretation Guide

### 🎯 Target Baselines for Production

| Metric | Minimum | Good | Excellent | Action Required If Below |
|--------|---------|------|-----------|-------------------------|
| **Narrative Coherence** | 6.5 | 7.5 | 8.5 | Review prompts, adjust temperature |
| **World Consistency** | 7.0 | 8.0 | 9.0 | Fix state management, enhance tracking |
| **User Engagement** | 6.0 | 7.0 | 8.0 | Improve choices, enhance pacing |
| **Technical Performance** | 6.5 | 7.5 | 8.5 | Optimize infrastructure, reduce latency |

### 🚨 Critical Issues (Immediate Action Required)
- **Error Rate > 10%**: Fix critical bugs before proceeding
- **Response Time > 5s**: Optimize model calls and infrastructure
- **Narrative Coherence < 6.0**: Major prompt revision needed
- **World Consistency < 6.5**: Overhaul state management system

### ⚠️ Performance Issues (Address Within Week)
- **Quality declining over turns**: Investigate memory/context issues
- **Inconsistent performance**: Standardize configurations
- **High memory usage**: Optimize data structures

### 💡 Optimization Opportunities (Address Within Month)
- **Good but not excellent scores**: Fine-tune prompts and parameters
- **Minor performance improvements**: Reduce latency, optimize calls
- **Feature enhancements**: Add new capabilities based on insights

## 🔧 Acting on Analysis Results

### High Priority Actions
1. **Review Comprehensive Report**: Focus on lowest-scoring metrics
2. **Identify Patterns**: Look for consistent issues across tests
3. **Prioritize Fixes**: Address critical issues first
4. **Implement Changes**: Make targeted, measurable improvements
5. **Re-test**: Validate improvements with focused tests

### Quality Improvement Workflow
```
Identify Issue → Hypothesize Cause → Implement Fix → Test Change → Validate Improvement
```

### Common Issues and Solutions

| Issue | Likely Cause | Recommended Action |
|-------|--------------|-------------------|
| Low narrative coherence | Unclear prompts, high temperature | Clarify prompts, reduce temperature to 0.5-0.6 |
| Poor world consistency | State management bugs | Review world state logic, add validation |
| Low engagement | Boring choices, poor pacing | Enhance choice meaningfulness, adjust pacing |
| Technical problems | Infrastructure issues | Optimize model calls, increase timeouts |

## 📋 Post-Deployment Monitoring

### Regular Evaluation Schedule
- **Weekly**: Quick sample tests to monitor stability
- **Monthly**: Comprehensive evaluation with full scenario matrix
- **Quarterly**: Deep analysis and baseline updates

### Key Metrics to Track
- **Quality Trends**: Are scores improving or declining over time?
- **Error Rates**: Are technical issues increasing?
- **Performance**: Are response times staying consistent?
- **User Satisfaction**: How do real users compare to simulated profiles?

### Alerting Thresholds
```yaml
alert_thresholds:
  narrative_coherence_drop: 1.5  # Alert if drops by 1.5 points
  error_rate_spike: 0.1          # Alert if error rate exceeds 10%
  response_time_spike: 5.0       # Alert if response time exceeds 5s
```

## 🎉 Success Indicators

### Short-term (First Month)
- [ ] Baseline quality metrics established
- [ ] Framework running reliably without critical errors
- [ ] Clear understanding of model strengths and weaknesses
- [ ] Actionable improvement recommendations identified

### Medium-term (3 Months)
- [ ] Quality improvements implemented and validated
- [ ] Regular evaluation schedule established
- [ ] Integration with development workflow
- [ ] Trend analysis showing stable or improving quality

### Long-term (6+ Months)
- [ ] Consistent high-quality performance across all scenarios
- [ ] Automated quality monitoring and alerting
- [ ] Quality metrics integrated into development decisions
- [ ] Framework expanded to cover additional use cases

## 🆘 Troubleshooting

### Common Setup Issues
```bash
# Virtual environment issues
python3 -m venv venv --clear  # Recreate if corrupted

# Permission issues
chmod +x testing/extended_evaluation/*.sh

# Configuration issues
python -c "import yaml; yaml.safe_load(open('testing/configs/production_extended_evaluation.yaml'))"
```

### Performance Issues
- **Memory**: Reduce concurrent sessions, enable memory optimization
- **Speed**: Increase timeouts, reduce scenario complexity
- **Reliability**: Enable checkpointing, increase retry attempts

### Getting Help
1. **Check Logs**: `testing/extended_evaluation_execution.log`
2. **Validate Config**: Ensure YAML syntax is correct
3. **Test Components**: Use `example_usage.py` for isolated testing
4. **Monitor Resources**: Check system CPU, memory, disk usage
5. **Start Simple**: Begin with minimal configuration and scale up

---

**Ready for Production**: ✅ All checklist items completed, baselines established, monitoring in place
