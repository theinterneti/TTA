# Adding Models to the OpenHands Registry

**Audience:** Developers and non-developers
**Difficulty:** Beginner
**Time Required:** 10-15 minutes

## Overview

The OpenHands model registry is a YAML-based system that allows you to add new models **without writing any code**. Simply edit the YAML file, test the model, and commit your changes.

### When to Add a Model

Add a model to the registry when:
- You discover a new free OpenRouter model
- You want to test an existing model's compatibility
- You need to update a model's metadata (e.g., status, known issues)

### Benefits

- **No code changes required** - Just edit YAML
- **Automatic integration** - Models are immediately available
- **Intelligent fallback** - System automatically prioritizes models
- **Easy testing** - Built-in compatibility testing script

## Prerequisites

1. **OpenRouter Account**
   - Sign up at https://openrouter.ai
   - Get your API key from https://openrouter.ai/keys

2. **Environment Setup**
   ```bash
   # Set your API key
   export OPENROUTER_API_KEY="your-key-here"

   # Or add to .env file
   echo "OPENROUTER_API_KEY=your-key-here" >> .env
   ```

3. **Find a Model**
   - Browse free models at https://openrouter.ai/models?free=true
   - Note the model ID (e.g., `deepseek/deepseek-chat`)

## Step-by-Step Guide

### Step 1: Find the Model ID

1. Go to https://openrouter.ai/models?free=true
2. Find a model you want to add
3. Click on the model to view details
4. Copy the model ID (e.g., `deepseek/deepseek-chat`)

**Important:** The model ID in the registry must include the `openrouter/` prefix!

### Step 2: Open the Registry File

```bash
# Open the registry file in your editor
code src/agent_orchestration/openhands_integration/free_models_registry.yaml
```

### Step 3: Add Your Model Entry

Add a new entry under the `models:` section. Use this template:

```yaml
  openrouter/provider/model-name:free:
    model_id: "openrouter/provider/model-name:free"
    display_name: "Human-Readable Model Name"
    provider: "ProviderName"
    compatibility_status: "untested"  # Start with "untested"
    quality_tier: "medium"  # Conservative estimate
    context_window: 32000  # Check model docs
    supports_system_prompt: true  # Usually true
    known_issues: []
    last_tested: null
    validation_notes: "Newly added, not yet tested"
    expected_latency_ms: null
    capabilities: ["code", "reasoning"]  # Based on model description
```

**Example:**

```yaml
  openrouter/qwen/qwen-2.5-72b-instruct:free:
    model_id: "openrouter/qwen/qwen-2.5-72b-instruct:free"
    display_name: "Qwen 2.5 72B Instruct (Free)"
    provider: "Qwen"
    compatibility_status: "untested"
    quality_tier: "high"
    context_window: 32000
    supports_system_prompt: true
    known_issues: []
    last_tested: null
    validation_notes: "High-priority untested model. Strong reasoning capabilities expected."
    expected_latency_ms: null
    capabilities: ["code", "reasoning", "multilingual"]
```

### Step 4: Fill in Metadata

#### Required Fields

- **model_id**: Full OpenRouter ID with `openrouter/` prefix
- **display_name**: Human-readable name (check OpenRouter website)
- **provider**: Model provider (DeepSeek, Qwen, Mistral, Google, Meta, etc.)
- **compatibility_status**: Start with `"untested"`
- **quality_tier**: Conservative estimate (`"medium"` is safe)
- **context_window**: Check model documentation
- **supports_system_prompt**: Usually `true` (OpenHands requires this)

#### Optional Fields

- **known_issues**: List of known problems (empty list `[]` if none)
- **last_tested**: ISO date `"YYYY-MM-DD"` or `null`
- **validation_notes**: Notes about testing or expectations
- **expected_latency_ms**: Response time in milliseconds or `null`
- **capabilities**: List like `["code", "reasoning", "multilingual", "vision"]`

### Step 5: Validate YAML Syntax

```bash
# Test YAML syntax
python -c "import yaml; yaml.safe_load(open('src/agent_orchestration/openhands_integration/free_models_registry.yaml'))"

# If successful, you'll see no output
# If there's an error, fix the YAML syntax
```

### Step 6: Test the Model

```bash
# Test your specific model
uv run python scripts/test_model_compatibility.py --model openrouter/provider/model-name:free

# This will:
# 1. Run 4 test tasks
# 2. Measure execution time
# 3. Detect errors (rate limits, content moderation, etc.)
# 4. Generate a compatibility report
```

### Step 7: Update Status Based on Results

After testing, update the model entry:

**If all tests passed:**
```yaml
compatibility_status: "verified"
last_tested: "2025-10-25"
validation_notes: "100% success rate (4/4 tasks), avg 4.5s execution time"
expected_latency_ms: 4500
```

**If rate-limited:**
```yaml
compatibility_status: "rate_limited"
known_issues:
  - "Upstream rate limiting (429 errors)"
last_tested: "2025-10-25"
validation_notes: "50% success rate (2/4 tasks), 2 tasks failed with rate limit errors"
```

**If incompatible:**
```yaml
compatibility_status: "incompatible"
supports_system_prompt: false  # If this is the issue
known_issues:
  - "No system prompt support"
  - "Error: developer instruction is not enabled for this model"
last_tested: "2025-10-25"
validation_notes: "Model architecture does not support system prompts"
```

### Step 8: Commit Your Changes

```bash
# Add the file
git add src/agent_orchestration/openhands_integration/free_models_registry.yaml

# Commit with descriptive message
git commit -m "Add Qwen 2.5 72B Instruct to model registry (verified)"

# Push to your branch
git push origin your-branch-name
```

## Status Classification Guidelines

### `verified` - Fully Working
- All test tasks passed
- No errors or warnings
- Recommended for production use
- Example: `openrouter/deepseek/deepseek-chat`

### `untested` - Not Yet Tested
- Newly added model
- No compatibility data available
- Use with caution
- Should be tested before production use

### `rate_limited` - Works But Limited
- Model works correctly
- May hit rate limits under load
- Suitable for fallback chains
- Example: `openrouter/qwen/qwen3-coder:free`

### `incompatible` - Known Issues
- Model has compatibility problems
- Should not be used with OpenHands
- Document specific issues in `known_issues`
- Example: `openrouter/google/gemma-3n-e4b-it:free` (no system prompts)

## Troubleshooting

### YAML Syntax Errors

**Error:** `yaml.scanner.ScannerError: mapping values are not allowed here`

**Solution:** Check indentation (use 2 spaces, not tabs)

```yaml
# ❌ Wrong (tabs or wrong indentation)
  model_id:"openrouter/test"

# ✅ Correct (2 spaces, space after colon)
  model_id: "openrouter/test"
```

### Model ID Format Errors

**Error:** Model not found or config error

**Solution:** Ensure `openrouter/` prefix is included

```yaml
# ❌ Wrong (missing prefix)
model_id: "deepseek/deepseek-chat"

# ✅ Correct (with prefix)
model_id: "openrouter/deepseek/deepseek-chat"
```

### Testing Failures

**Error:** `ContentPolicyViolationError`

**Solution:** Model has aggressive content moderation
```yaml
compatibility_status: "incompatible"
known_issues:
  - "Content moderation blocks OpenHands system prompt"
```

**Error:** `429 Too Many Requests`

**Solution:** Model is rate-limited
```yaml
compatibility_status: "rate_limited"
known_issues:
  - "Upstream rate limiting (429 errors)"
```

**Error:** `developer instruction is not enabled`

**Solution:** Model doesn't support system prompts
```yaml
compatibility_status: "incompatible"
supports_system_prompt: false
known_issues:
  - "No system prompt support"
```

## Examples

### Example 1: Verified High-Quality Model

```yaml
  openrouter/deepseek/deepseek-chat:
    model_id: "openrouter/deepseek/deepseek-chat"
    display_name: "DeepSeek Chat"
    provider: "DeepSeek"
    compatibility_status: "verified"
    quality_tier: "high"
    context_window: 64000
    supports_system_prompt: true
    known_issues: []
    last_tested: "2025-10-24"
    validation_notes: "100% success rate (4/4 tasks), avg 4.5s execution time, quality score 0.07"
    expected_latency_ms: 4500
    capabilities: ["code", "reasoning", "multilingual"]
```

### Example 2: Untested Model

```yaml
  openrouter/qwen/qwen-2.5-72b-instruct:free:
    model_id: "openrouter/qwen/qwen-2.5-72b-instruct:free"
    display_name: "Qwen 2.5 72B Instruct (Free)"
    provider: "Qwen"
    compatibility_status: "untested"
    quality_tier: "high"
    context_window: 32000
    supports_system_prompt: true
    known_issues: []
    last_tested: null
    validation_notes: "High-priority untested model. Strong reasoning capabilities expected."
    expected_latency_ms: null
    capabilities: ["code", "reasoning", "multilingual"]
```

### Example 3: Incompatible Model

```yaml
  openrouter/google/gemma-3n-e4b-it:free:
    model_id: "openrouter/google/gemma-3n-e4b-it:free"
    display_name: "Google Gemma 3N E4B IT (Free)"
    provider: "Google"
    compatibility_status: "incompatible"
    quality_tier: "low"
    context_window: 8000
    supports_system_prompt: false
    known_issues:
      - "No system prompt support"
      - "Error: developer instruction is not enabled for this model"
    last_tested: "2025-10-24"
    validation_notes: "Gemma architecture does not support system prompts, which OpenHands requires"
    expected_latency_ms: null
    capabilities: ["code"]
```

## Next Steps

After adding your model:

1. **Run Full Test Suite**
   ```bash
   uv run pytest tests/integration/openhands/test_registry.py -v
   ```

2. **Test Model Selection**
   ```python
   from src.agent_orchestration.openhands_integration.config import get_fallback_model_chain

   # Your model should appear in the fallback chain
   chain = get_fallback_model_chain(max_models=10)
   print(chain)
   ```

3. **Create Pull Request**
   - Include test results in PR description
   - Link to OpenRouter model page
   - Explain why this model is useful

## Related Documentation

- **Registry Design:** `docs/openhands/model-registry-design.md`
- **Testing Guide:** `docs/openhands/free-model-registry.md`
- **Configuration:** `src/agent_orchestration/openhands_integration/config.py`

---

**Questions?** Open an issue or ask in the project Discord.
