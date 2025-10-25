# OpenHands Integration - Quick Start Guide

## Overview

The OpenHands integration enables TTA (Text-based Adventure) to leverage the OpenHands Python SDK for development tasks such as code generation, debugging, and file manipulation. This integration follows TTA's agent proxy pattern and uses OpenRouter's free LLM models for cost-effective AI-powered development assistance.

**Current Status:** ⚠️ **Manual Instantiation Required**

The OpenHands integration is **functionally complete** but **not yet registered** in the OrchestrationService. This means you must manually instantiate the `OpenHandsAgentProxy` to use it. Full orchestration integration is planned for a future release.

## Prerequisites

1. **Install Dependencies**
   ```bash
   uv sync
   ```

2. **Get an OpenRouter API Key**
   - Visit: https://openrouter.ai/keys
   - Sign up for a free account
   - Generate an API key
   - OpenRouter provides free access to several models (DeepSeek V3, Gemini Flash, etc.)

## Environment Setup

1. **Create `.env` file** (if it doesn't exist):
   ```bash
   cp .env.example .env
   ```

2. **Set your OpenRouter API key** in `.env`:
   ```bash
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

3. **Optional Configuration** (with defaults):
   ```bash
   # Model to use (default: openrouter/deepseek/deepseek-chat)
   # IMPORTANT: Use openrouter/ prefix for litellm provider recognition
   OPENHANDS_MODEL=openrouter/deepseek/deepseek-chat

   # API base URL (default: https://openrouter.ai/api/v1)
   OPENHANDS_BASE_URL=https://openrouter.ai/api/v1

   # Workspace directory (default: ./openhands_workspace)
   OPENHANDS_WORKSPACE_ROOT=./openhands_workspace

   # Default timeout in seconds (default: 300.0)
   OPENHANDS_TIMEOUT=300.0

   # Enable circuit breaker (default: true)
   OPENHANDS_ENABLE_CIRCUIT_BREAKER=true
   ```

## Quick Start Example

### Basic Usage (Manual Instantiation)

```python
import asyncio
from src.agent_orchestration.openhands_integration import (
    OpenHandsIntegrationConfig,
    OpenHandsAgentProxy,
)

async def main():
    # Load configuration from environment
    config = OpenHandsIntegrationConfig.from_env()

    # Create proxy (without full orchestration)
    proxy = OpenHandsAgentProxy(
        openhands_config=config,
        enable_real_agent=True,  # Use real OpenHands SDK
        fallback_to_mock=False,  # No fallback to mock responses
    )

    # Execute a development task
    result = await proxy.execute_development_task(
        "Write a Python function to calculate the nth Fibonacci number"
    )

    print(f"Success: {result.success}")
    print(f"Output:\n{result.output}")
    if result.error:
        print(f"Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Using with Custom Configuration

```python
from pathlib import Path
from pydantic import SecretStr
from src.agent_orchestration.openhands_integration import (
    OpenHandsIntegrationConfig,
    OpenHandsAgentProxy,
)

# Create configuration programmatically
config = OpenHandsIntegrationConfig(
    api_key=SecretStr("your-api-key"),
    model_preset="openrouter/deepseek/deepseek-chat",  # Validated working model
    workspace_root=Path("./my_workspace"),
    default_timeout_seconds=600.0,
    circuit_breaker_enabled=True,
)

# Create proxy
proxy = OpenHandsAgentProxy(openhands_config=config)

# Use proxy...
```

## Available Free Models

**⚠️ IMPORTANT:** Based on end-to-end validation (2025-10-24), only **1 out of 8 tested models** works reliably with OpenHands integration.

### ✅ Working Models

| Model | Context | Status | Best For |
|-------|---------|--------|----------|
| `openrouter/deepseek/deepseek-chat` | 65K input / 4K output | ✅ **Verified Working** | General development tasks, code generation |

**Configuration Requirements:**
- **MUST** use `openrouter/` prefix (litellm requirement)
- **MUST** set `max_output_tokens=4096` (prevent token budget errors)
- **MUST** set `extended_thinking_budget=0` (prevent excessive token requests)
- **MUST** set `custom_llm_provider="openrouter"` (litellm provider recognition)

### ⚠️ Models with Issues

| Model | Issue | Status |
|-------|-------|--------|
| `openrouter/qwen/qwen3-coder:free` | Rate limiting | ⚠️ Works when not rate-limited |
| `openrouter/meta-llama/llama-3.3-8b-instruct:free` | Content moderation blocks system prompts | ❌ Not compatible |
| `openrouter/google/gemma-3n-e4b-it:free` | No developer instructions support | ❌ Not compatible |
| Models without `openrouter/` prefix | litellm provider errors | ❌ Invalid configuration |

**See:** `docs/openhands/free-model-registry.md` for detailed model compatibility information.

## Current Limitations

⚠️ **Important:** The OpenHands integration is not yet fully integrated into TTA's orchestration system. Current limitations:

1. **Manual Instantiation Required**
   - `OpenHandsAgentProxy` is NOT registered in `OrchestrationService`
   - Must manually create and manage proxy instances
   - No automatic lifecycle management

2. **No Message Coordination**
   - Cannot use with TTA's message coordinator
   - Direct proxy usage only

3. **Timeout Not Enforced**
   - Client timeout is configured but not yet enforced
   - Tasks could potentially run longer than specified timeout

4. **Result Parsing Incomplete**
   - Returns placeholder "Task completed" instead of actual output
   - Full conversation parsing not yet implemented

5. **Test Coverage**
   - Current coverage: ~40%
   - Missing tests for proxy and error recovery components

6. **⚠️ No File Creation Tools** (Discovered 2025-10-24)
   - OpenHands agent proposes code but **doesn't create files**
   - Only 2 tools available: `finish` and `think`
   - No bash/file operation tools configured
   - **Impact:** Agent can analyze and propose solutions but cannot implement them
   - **Root Cause:** Integration uses OpenHands SDK (simplified wrapper) which has limited tool access
   - **Solution:** Configure runtime environment with bash tools or explore MCP integration
   - **See:** `docs/openhands/tool-configuration-research.md` for detailed findings

7. **Limited Model Compatibility** (Validated 2025-10-24)
   - Only 1 out of 8 tested models works reliably
   - Most free models have compatibility issues (content moderation, no system prompts, rate limiting)
   - **Recommended:** Use `openrouter/deepseek/deepseek-chat` (verified working)
   - **See:** `docs/openhands/free-model-registry.md` for full model compatibility matrix

## Testing Connectivity

To verify your OpenHands integration is working:

```python
import asyncio
from src.agent_orchestration.openhands_integration import OpenHandsIntegrationConfig

async def test_connection():
    try:
        # Load config from environment
        config = OpenHandsIntegrationConfig.from_env()
        print("✓ Configuration loaded successfully")
        print(f"  Model: {config.model_preset}")
        print(f"  Workspace: {config.workspace_root}")
        print(f"  Timeout: {config.default_timeout_seconds}s")
        print(f"  Circuit Breaker: {config.circuit_breaker_enabled}")

        # Note: Actual API connectivity test requires implementing
        # a simple task execution, which is beyond basic config validation

    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("\nMake sure you have set OPENROUTER_API_KEY in your .env file")
        print("Get your API key from: https://openrouter.ai/keys")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

**Expected Output:**
```
✓ Configuration loaded successfully
  Model: openrouter/deepseek/deepseek-chat
  Workspace: openhands_workspace
  Timeout: 300.0s
  Circuit Breaker: True
```

## Troubleshooting

### Error: "OPENROUTER_API_KEY environment variable is required"

**Solution:** Set your API key in `.env`:
```bash
echo "OPENROUTER_API_KEY=your_key_here" >> .env
```

### Error: "OpenHands SDK not installed"

**Solution:** Reinstall dependencies:
```bash
uv sync
```

### Workspace Permission Errors

**Solution:** Ensure workspace directory is writable:
```bash
mkdir -p openhands_workspace
chmod 755 openhands_workspace
```

### Import Errors

**Solution:** Verify you're in the project root and virtual environment is activated:
```bash
cd /path/to/recovered-tta-storytelling
uv sync
```

### Error: "LLM Provider NOT provided" or "model is not a valid model ID"

**Problem:** Model name missing `openrouter/` prefix

**Solution:** Add `openrouter/` prefix to model name:
```bash
# ❌ Wrong
OPENHANDS_MODEL=deepseek/deepseek-chat

# ✅ Correct
OPENHANDS_MODEL=openrouter/deepseek/deepseek-chat
```

**Why:** litellm requires `openrouter/` prefix to recognize OpenRouter as the provider.

### Error: "requested about 1003154 tokens... Please reduce the length"

**Problem:** Token budget exceeded (extended_thinking_budget too high)

**Solution:** Limit token budget in client configuration:
```python
# In src/agent_orchestration/openhands_integration/client.py
self._llm = LLM(
    model=self.config.model,
    max_output_tokens=4096,  # Limit output tokens
    extended_thinking_budget=0,  # Disable extended thinking
)
```

**Why:** OpenHands SDK defaults to high token budgets that exceed model limits.

### Error: "No auth credentials found" (401)

**Problem:** Invalid or expired API key

**Solution:** Generate a fresh API key from https://openrouter.ai/keys and update `.env`:
```bash
# Test API key directly
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{"model": "openrouter/deepseek/deepseek-chat", "messages": [{"role": "user", "content": "Hello"}]}'
```

### Model-Specific Issues

**Llama Models:** Content moderation blocks OpenHands system prompts
- **Error:** "This content may violate our content policy"
- **Solution:** Use DeepSeek model instead

**Gemma Models:** No developer instructions support
- **Error:** "developer instruction is not enabled for this model"
- **Solution:** Use DeepSeek model instead

**Rate Limiting:** Free models have usage limits
- **Error:** "Rate limit exceeded" or "upstream rate limited"
- **Solution:** Wait and retry, or use DeepSeek (more reliable)

**See:** `docs/validation/openhands-integration-validation-2025-10-24.md` for detailed validation findings.

## Additional Documentation

- **✅ Validation Report:** `docs/validation/openhands-integration-validation-2025-10-24.md` (NEW)
  - End-to-end validation results
  - Model compatibility testing (8 models tested)
  - Working configuration details
  - Quality assessment and recommendations

- **Design Document:** `docs/development/openhands-integration-design.md` (1,337 lines)
  - Comprehensive architecture and component details
  - Error recovery strategies
  - Testing strategy

- **Implementation Summary:** `docs/development/openhands-implementation-summary.md` (373 lines)
  - Current implementation status
  - Known issues and TODOs
  - Next steps for full integration

- **Integration Summary:** `docs/development/openhands-integration-summary.md` (277 lines)
  - Executive summary
  - Free models catalog
  - Integration points with TTA core

- **Tool Configuration Research:** `docs/openhands/tool-configuration-research.md` (COMING SOON)
  - OpenHands SDK vs runtime environment
  - MCP integration options
  - Bash/file operation tool configuration

- **Free Model Registry:** `docs/openhands/free-model-registry.md` (COMING SOON)
  - Detailed model compatibility matrix
  - Model selection strategy
  - Configuration examples and troubleshooting

## Next Steps

To enable full orchestration integration:

1. **Register Proxy in OrchestrationService** (Priority 2)
   - Update `src/agent_orchestration/service.py`
   - Add proxy initialization and lifecycle management
   - Estimated effort: 4 hours

2. **Complete Test Coverage** (Priority 2)
   - Add proxy tests
   - Add error recovery tests
   - Achieve >70% coverage
   - Estimated effort: 4 hours

3. **Implement Missing Features** (Priority 3)
   - Enforce timeout in client
   - Parse actual output from conversation
   - Estimated effort: 3 hours

## Support

For issues or questions:
- Check the comprehensive design document
- Review implementation summary for known issues
- Consult TTA development team

---

**Last Updated:** 2025-10-24
**Status:** ✅ Validated (Manual Instantiation, Limited Tool Access)
**Version:** Phase 3 Implementation + End-to-End Validation Complete
**Validation Date:** 2025-10-24
**Validated Model:** `openrouter/deepseek/deepseek-chat`

