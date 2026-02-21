# TTA Extended Evaluation - Quick Start Guide

## 🚀 Getting Started in 5 Steps

### Step 1: Setup Dependencies
```bash
# Run the setup script
./testing/extended_evaluation/setup.sh

# Or install manually:
pip3 install aiohttp PyYAML psutil pandas numpy matplotlib
```

### Step 2: Configure Your Models
Edit `testing/configs/production_extended_evaluation.yaml`:

```yaml
# Update with your actual model configurations
recommended_model_settings:
  primary_models:
    - "your_primary_model"    # Replace with your model name
    - "your_backup_model"     # Replace with backup model
```

### Step 3: Run Initial Status Check
```bash
python3 testing/run_extended_evaluation.py --mode status --config testing/configs/production_extended_evaluation.yaml
```

### Step 4: Run Quick Sample Test (30-60 minutes)
```bash
python3 testing/run_extended_evaluation.py --mode quick-sample --config testing/configs/production_extended_evaluation.yaml
```

### Step 5: Analyze Results
```bash
python3 testing/run_extended_evaluation.py --mode analysis-only
```

## 📊 Establishing Quality Baselines

### Recommended Approach for First Evaluation

1. **Start Small**: Use the production config with 20-25 turn scenarios
2. **Test One Model**: Begin with your most reliable model
3. **Use Representative Profiles**: Start with "typical_user" profile
4. **Monitor Closely**: Watch for errors or performance issues

### Initial Baseline Run
```bash
# This will run 2 scenarios × 2 profiles × 1 model = 4 tests (~2-4 hours)
python3 testing/run_extended_evaluation.py --mode comprehensive --config testing/configs/production_extended_evaluation.yaml
```

### Expected Initial Results
- **Narrative Coherence**: Target 7.5+/10 (excellent: 8.0+)
- **World Consistency**: Target 8.0+/10 (excellent: 8.5+)
- **User Engagement**: Target 7.0+/10 (excellent: 7.8+)
- **Technical Performance**: Target 7.5+/10 (excellent: 8.0+)

## 🎯 Model Configuration Recommendations

### For Initial Baseline Testing

```yaml
# Conservative settings for reliable baselines
model_settings:
  temperature: 0.7          # Balanced creativity/consistency
  max_tokens: 2048         # Sufficient detail
  timeout_seconds: 30      # Reasonable timeout
  retry_attempts: 2        # Allow retries
```

### Model Selection Priority
1. **Most Stable Model**: Your most reliable, tested model
2. **Best Performing Model**: Highest quality in existing tests
3. **Production Model**: Currently used in production
4. **Experimental Models**: Only after baseline established

### Recommended Test Sequence
1. **Single Model Baseline** (4-6 hours)
2. **Multi-Model Comparison** (12-24 hours)
3. **Extended Scenarios** (24-48 hours)
4. **Full Evaluation Matrix** (48+ hours)

## 📈 Interpreting Quality Metrics

### Narrative Coherence (35% weight)
- **8.5+**: Excellent - Stories maintain perfect consistency
- **7.5-8.4**: Good - Minor inconsistencies, overall coherent
- **6.5-7.4**: Acceptable - Some issues but usable
- **<6.5**: Poor - Significant coherence problems

**Action Items by Score:**
- **8.5+**: Maintain current approach
- **7.5-8.4**: Monitor for patterns, minor tuning
- **6.5-7.4**: Review prompts, adjust temperature
- **<6.5**: Major prompt revision needed

### World Consistency (25% weight)
- **9.0+**: Excellent - Perfect world state tracking
- **8.0-8.9**: Good - Reliable with minor issues
- **7.0-7.9**: Acceptable - Some state inconsistencies
- **<7.0**: Poor - Major world state problems

**Action Items by Score:**
- **9.0+**: Document successful patterns
- **8.0-8.9**: Fine-tune world state prompts
- **7.0-7.9**: Review state management logic
- **<7.0**: Overhaul world state system

### User Engagement (25% weight)
- **8.0+**: Excellent - Highly engaging throughout
- **7.0-7.9**: Good - Maintains interest well
- **6.0-6.9**: Acceptable - Some engagement drops
- **<6.0**: Poor - Fails to maintain engagement

**Action Items by Score:**
- **8.0+**: Analyze successful engagement patterns
- **7.0-7.9**: Enhance choice meaningfulness
- **6.0-6.9**: Improve pacing and variety
- **<6.0**: Redesign interaction patterns

### Technical Performance (15% weight)
- **8.5+**: Excellent - Fast, reliable, efficient
- **7.5-8.4**: Good - Minor performance issues
- **6.5-7.4**: Acceptable - Some slowdowns/errors
- **<6.5**: Poor - Significant technical problems

## 🔧 Acting on Recommendations

### High Priority Actions (Address Immediately)
- **Error Rate >10%**: Fix critical bugs
- **Response Time >5s**: Optimize model calls
- **Coherence <6.5**: Revise core prompts
- **Engagement <6.0**: Redesign interaction flow

### Medium Priority Actions (Address Within Week)
- **Quality Trends Declining**: Investigate causes
- **Memory Usage High**: Optimize data structures
- **Inconsistent Performance**: Standardize configurations

### Low Priority Actions (Address Within Month)
- **Minor Quality Improvements**: Fine-tune prompts
- **Performance Optimizations**: Reduce latency
- **Feature Enhancements**: Add new capabilities

## 📋 Quality Improvement Workflow

### 1. Identify Issues
- Review comprehensive analysis report
- Focus on lowest-scoring metrics
- Look for consistent patterns across tests

### 2. Hypothesize Causes
- **Low Coherence**: Prompt clarity, model temperature
- **Poor Consistency**: State management, memory
- **Low Engagement**: Choice design, pacing
- **Technical Issues**: Infrastructure, optimization

### 3. Implement Changes
- Make targeted, measurable changes
- Test changes in isolation when possible
- Document all modifications

### 4. Re-evaluate
- Run focused tests on changed areas
- Compare before/after metrics
- Validate improvements are sustained

### 5. Iterate
- Continue cycle until targets met
- Establish new baselines after improvements
- Monitor for regression

## 🚨 Troubleshooting Common Issues

### Framework Won't Start
```bash
# Check dependencies
python3 -c "import aiohttp, yaml, psutil; print('Dependencies OK')"

# Check configuration
python3 testing/run_extended_evaluation.py --mode status
```

### Tests Fail or Timeout
- Reduce `max_concurrent_sessions` to 1
- Increase `session_timeout_minutes`
- Check model connectivity
- Review error logs

### Poor Quality Scores
- Start with shorter scenarios (15-20 turns)
- Use lower temperature (0.5-0.6)
- Simplify initial prompts
- Test with single user profile

### Memory Issues
- Reduce concurrent sessions
- Enable memory optimization
- Clear old results regularly
- Monitor system resources

## 📞 Getting Help

1. **Check Logs**: `testing/extended_evaluation_execution.log`
2. **Review Configuration**: Validate YAML syntax
3. **Test Components**: Use `example_usage.py` for isolated testing
4. **Monitor Resources**: Check CPU, memory, disk usage
5. **Gradual Scaling**: Start small, increase complexity gradually

---

**Next Steps After Baseline:**
1. Analyze initial results thoroughly
2. Implement highest-priority improvements
3. Expand to full scenario matrix
4. Establish regular evaluation schedule
5. Integrate insights into development workflow


---
**Logseq:** [[TTA.dev/Testing/Extended_evaluation/Quick_start]]
