# OpenHands Free Model Registry

**Last Updated:** 2025-10-24
**Validation Date:** 2025-10-24
**Models Tested:** 8
**Models Working:** 1 (12.5%)
**Purpose:** Comprehensive guide to free OpenRouter models for OpenHands integration

---

## Executive Summary

During end-to-end validation of the OpenHands integration, **8 different model configurations were tested**. Only **1 model** (`openrouter/deepseek/deepseek-chat`) works reliably with the OpenHands SDK and TTA integration.

**Key Findings:**
- ✅ **1 Working Model:** DeepSeek Chat (verified, reliable)
- ⚠️ **1 Rate-Limited Model:** Qwen Coder (works when not rate-limited)
- ❌ **2 Incompatible Models:** Llama (content moderation), Gemma (no system prompts)
- ❌ **4 Configuration Errors:** Models without `openrouter/` prefix

**Recommendation:** Use `openrouter/deepseek/deepseek-chat` for all OpenHands tasks.

---

## Quick Reference Table

| Model | Status | Context | Cost | Best For |
|-------|--------|---------|------|----------|
| `openrouter/deepseek/deepseek-chat` | ✅ Working | 65K / 4K | Free | General development, code generation |
| `openrouter/qwen/qwen3-coder:free` | ⚠️ Rate Limited | - | Free | Coding (when available) |
| `openrouter/meta-llama/llama-3.3-8b-instruct:free` | ❌ Blocked | - | Free | Not compatible |
| `openrouter/google/gemma-3n-e4b-it:free` | ❌ Incompatible | - | Free | Not compatible |
| `deepseek/deepseek-v3:free` | ❌ Config Error | - | - | Invalid (missing prefix) |
| `deepseek/deepseek-chat-v3.1:free` | ❌ Config Error | - | - | Invalid (missing prefix) |
| `deepseek/deepseek-chat` | ❌ Config Error | - | - | Invalid (missing prefix) |
| `google/gemma-3n-e4b-it:free` | ❌ Config Error | - | - | Invalid (missing prefix) |

---

## ✅ Working Models

### openrouter/deepseek/deepseek-chat

**Status:** ✅ **Verified Working** (2025-10-24) | 🧪 **Tested** (2025-10-24)

**Model Details:**
- **Provider:** DeepSeek via OpenRouter
- **Context Window:** 65,536 input tokens / 4,096 output tokens
- **Cost:** Free via OpenRouter
- **Strengths:**
  - Supports system prompts (no content moderation issues)
  - Good for coding tasks (code generation, debugging, analysis)
  - Reliable availability (not frequently rate-limited)
  - Fast response times (~4.5s average for test tasks)

**Empirical Test Results:**
- **Success Rate:** 100% (4/4 tasks completed)
- **Average Execution Time:** 4.5 seconds
- **Average Quality Score:** 0.07/1.0 (low due to limited tool access)
- **Rate Limit Hits:** 0
- **Errors:** 0
- **Test Date:** 2025-10-24
- **Test Report:** `docs/openhands/model-compatibility-results.md`
- **Limitations:**
  - 4K output token limit (requires `max_output_tokens=4096`)
  - Extended thinking can exceed token budget (requires `extended_thinking_budget=0`)

**Configuration Example:**

```python
from pydantic import SecretStr
from src.agent_orchestration.openhands_integration import OpenHandsConfig

config = OpenHandsConfig(
    api_key=SecretStr("your-openrouter-api-key"),
    model="openrouter/deepseek/deepseek-chat",  # MUST include openrouter/ prefix
    base_url="https://openrouter.ai/api/v1",
    workspace_path="/path/to/workspace",
    timeout_seconds=300.0,
)
```

**Client Configuration (Required):**

```python
# In src/agent_orchestration/openhands_integration/client.py

self._llm = LLM(
    model=self.config.model,  # openrouter/deepseek/deepseek-chat
    api_key=self.config.api_key.get_secret_value(),
    base_url=self.config.base_url,
    custom_llm_provider="openrouter",  # REQUIRED for litellm
    openrouter_site_url="https://github.com/theinterneti/TTA",
    openrouter_app_name="TTA-OpenHands-Integration",
    max_output_tokens=4096,  # REQUIRED to prevent token budget errors
    extended_thinking_budget=0,  # REQUIRED to prevent excessive token requests
)
```

**Validation Results:**
- ✅ Task execution successful (51.83s)
- ✅ API authentication working
- ✅ System prompts supported
- ✅ No content moderation issues
- ⚠️ Agent proposes code but doesn't create files (tool configuration issue, not model issue)

**Recommended Use Cases:**
- General development tasks
- Code generation and refactoring
- Debugging and analysis
- Documentation generation
- Test writing

**Troubleshooting:**

*Issue:* "requested about 1003154 tokens... Please reduce the length"
*Solution:* Set `max_output_tokens=4096` and `extended_thinking_budget=0`

*Issue:* "LLM Provider NOT provided"
*Solution:* Ensure model name includes `openrouter/` prefix

*Issue:* "No auth credentials found"
*Solution:* Verify API key is valid and not expired

---

## ⚠️ Rate-Limited Models

### openrouter/qwen/qwen3-coder:free

**Status:** ⚠️ **Rate Limited** (tested 2025-10-24) | 🧪 **Tested** (2025-10-24)

**Model Details:**
- **Provider:** Qwen via OpenRouter
- **Cost:** Free (with rate limits)
- **Strengths:**
  - Good for coding tasks when available
  - Supports system prompts
- **Limitations:**
  - Frequent rate limiting on free tier
  - Unpredictable availability

**Empirical Test Results:**
- **Success Rate:** 50% (2/4 tasks completed, 2 rate-limited)
- **Average Execution Time:** 7.3 seconds (for successful tasks)
- **Average Quality Score:** 0.00/1.0 (low due to limited tool access)
- **Rate Limit Hits:** 2 (tasks 2 and 4 failed with 429 errors)
- **Errors:** 2 (both rate limiting)
- **Test Date:** 2025-10-24
- **Test Report:** `docs/openhands/model-compatibility-results.md`

**Error Message:**
```
litellm.RateLimitError: RateLimitError: OpenRouterException -
{"error":{"message":"upstream rate limited","code":429}}
```

**Recommendation:** Use as fallback when DeepSeek is unavailable, but expect rate limiting.

**Configuration:** Same as DeepSeek (replace model name only)

---

## ❌ Incompatible Models

### openrouter/meta-llama/llama-3.3-8b-instruct:free

**Status:** ❌ **Content Moderation Blocks System Prompts**

**Issue:** OpenHands system prompt is flagged by Llama's content moderation as "misc" content violation.

**Error Message:**
```
litellm.ContentPolicyViolationError: ContentPolicyViolationError: LlamaException -
{"error":{"message":"This content may violate our content policy","code":400,"metadata":{"reasons":["misc"]}}}
```

**Root Cause:** Llama models have aggressive content moderation that blocks OpenHands' system prompt.

**Recommendation:** ❌ Not compatible with OpenHands integration. Use DeepSeek instead.

---

### openrouter/google/gemma-3n-e4b-it:free

**Status:** ❌ **No Developer Instructions Support**

**Issue:** Gemma models don't support "developer instructions" (system prompts).

**Error Message:**
```
litellm.BadRequestError: BadRequestError: GeminiException -
{"error":{"message":"developer instruction is not enabled for this model","code":400}}
```

**Root Cause:** Gemma model architecture doesn't support system prompts, which OpenHands requires.

**Recommendation:** ❌ Not compatible with OpenHands integration. Use DeepSeek instead.

---

## ❌ Configuration Errors

### Models Without `openrouter/` Prefix

**Affected Models:**
- `deepseek/deepseek-v3:free`
- `deepseek/deepseek-chat-v3.1:free`
- `deepseek/deepseek-chat`
- `google/gemma-3n-e4b-it:free`

**Issue:** litellm requires `openrouter/` prefix to recognize OpenRouter as the provider.

**Error Messages:**
```
litellm.exceptions.BadRequestError: litellm.BadRequestError:
LLM Provider NOT provided. Pass in the LLM provider you are trying to call.
```

```
litellm.exceptions.BadRequestError: litellm.BadRequestError:
deepseek/deepseek-v3:free is not a valid model ID
```

**Solution:** Add `openrouter/` prefix to model name:

```python
# ❌ Wrong
model = "deepseek/deepseek-chat"

# ✅ Correct
model = "openrouter/deepseek/deepseek-chat"
```

**Why:** litellm uses the prefix to determine which API provider to use. Without the prefix, it doesn't know to use OpenRouter.

---

## Model Selection Strategy

### Decision Tree

```
Need to execute OpenHands task?
├─ Yes → Use openrouter/deepseek/deepseek-chat
│   ├─ Task succeeds → ✅ Done
│   ├─ Rate limited → Wait and retry OR use qwen/qwen3-coder:free
│   └─ API error → Check API key, verify configuration
│
└─ Testing new model?
    ├─ MUST include openrouter/ prefix
    ├─ MUST set max_output_tokens=4096
    ├─ MUST set extended_thinking_budget=0
    ├─ MUST set custom_llm_provider="openrouter"
    └─ Test with simple task first
```

### Task Type Recommendations

| Task Type | Primary Model | Fallback |
|-----------|---------------|----------|
| Code Generation | `openrouter/deepseek/deepseek-chat` | `openrouter/qwen/qwen3-coder:free` |
| Debugging | `openrouter/deepseek/deepseek-chat` | `openrouter/qwen/qwen3-coder:free` |
| Analysis | `openrouter/deepseek/deepseek-chat` | `openrouter/qwen/qwen3-coder:free` |
| Documentation | `openrouter/deepseek/deepseek-chat` | `openrouter/qwen/qwen3-coder:free` |

**Note:** All task types use the same model because only DeepSeek is reliably compatible.

---

## Configuration Checklist

Before using any OpenRouter model with OpenHands:

- [ ] Model name includes `openrouter/` prefix
- [ ] API key is valid and not expired
- [ ] `custom_llm_provider="openrouter"` is set
- [ ] `max_output_tokens=4096` is set
- [ ] `extended_thinking_budget=0` is set
- [ ] `openrouter_site_url` is set (optional but recommended)
- [ ] `openrouter_app_name` is set (optional but recommended)
- [ ] Base URL is `https://openrouter.ai/api/v1`

---

## Testing New Models

### Validation Process

1. **Add `openrouter/` prefix** to model name
2. **Configure token limits** (`max_output_tokens=4096`, `extended_thinking_budget=0`)
3. **Test with simple task** ("Return the string 'Hello, World!'")
4. **Check for errors:**
   - Content moderation → Model not compatible
   - No system prompts → Model not compatible
   - Rate limiting → Model works but has limits
   - Success → Model is compatible
5. **Test with moderate task** (code generation)
6. **Document results** in this registry

### Test Script

```bash
# Use scripts/test_model_compatibility.py (coming soon)
uv run python scripts/test_model_compatibility.py --model openrouter/new-model-name
```

---

## References

- **Validation Report:** `docs/validation/openhands-integration-validation-2025-10-24.md`
- **Tool Configuration:** `docs/openhands/tool-configuration-research.md`
- **Integration README:** `src/agent_orchestration/openhands_integration/README.md`
- **OpenRouter Models:** https://openrouter.ai/models
- **OpenRouter API Keys:** https://openrouter.ai/keys

---

**Status:** Complete (8 models documented)
**Recommendation:** Use `openrouter/deepseek/deepseek-chat` for all tasks
**Next Steps:** Test additional models as they become available, update registry
