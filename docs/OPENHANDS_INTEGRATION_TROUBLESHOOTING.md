# OpenHands Integration Troubleshooting Guide

## Overview

This guide documents common issues encountered during OpenHands Docker integration and their solutions.

## Issues Resolved

### 1. ✅ TTY Device Not Available

**Symptom:**
```
the input device is not a TTY
```

**Root Cause:**
Docker `-i` and `-t` flags were being added unconditionally, but the container runs in non-interactive environments where TTY is not available.

**Solution:**
Detect TTY availability before adding flags:
```python
tty_flags = []
if sys.stdout.isatty():
    tty_flags.append("-t")
if sys.stdin.isatty():
    tty_flags.append("-i")
```

**Status:** ✅ RESOLVED

---

### 2. ✅ Permission Denied: `.openhands` Directory

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/.openhands/.jwt_secret'
```

**Root Cause:**
The `.openhands` directory was owned by root from previous Docker runs, and the container's non-root user couldn't write to it.

**Solution:**
1. Remove `.openhands` directory mounting from Docker command
2. Create directory inside container before running OpenHands:
```bash
mkdir -p /.openhands && python -m openhands.core.main -t '<task>'
```

**Status:** ✅ RESOLVED

---

### 3. ✅ Infinite Loop: ConversationWindowCondenser

**Symptom:**
```
WARNING: All recent events are dangling observations, which we truncate.
This means the agent has only the essential first events. This should not happen.
ACTION: CondensationAction(...)
ERROR: Agent reached maximum iteration. Current iteration: 500, max iteration: 500
```

**Root Cause:**
The agent got stuck in a loop trying to condense conversation history. This occurred when:
1. History truncation was enabled (default)
2. The model had insufficient context window
3. The agent couldn't make progress on the task

**Solution:**
1. Switch to a model with larger context window (gemini-flash: 1M tokens vs deepseek-v3: 64K tokens)
2. Disable problematic history truncation:
```bash
-e AGENT_ENABLE_HISTORY_TRUNCATION=false
```
3. Set reasonable iteration limit:
```bash
-e MAX_ITERATIONS=100
```

**Configuration Changes:**
- Updated `.env`: Changed `OPENHANDS_MODEL=gemini-flash` (default)
- Updated `docker_client.py`: Added environment variables for iteration limit and history truncation

**Status:** ✅ RESOLVED

---

### 4. ✅ LLM Context Window Exceeded

**Symptom:**
```
litellm.exceptions.BadRequestError: This endpoint's maximum context length is 163800 tokens.
However, you requested about 174867 tokens...
LLMContextWindowExceedError: Conversation history longer than LLM context window limit.
```

**Root Cause:**
Using deepseek-v3 (64K context) for tasks that generated conversation history exceeding the limit.

**Solution:**
Switch to gemini-flash model with 1M context window:
```python
"gemini-flash": OpenHandsModelConfig(
    model_id="openrouter/google/gemini-2.0-flash-exp:free",
    display_name="Google Gemini 2.0 Flash",
    context_tokens=1_000_000,  # 1M tokens
    is_free=True,
)
```

**Status:** ✅ RESOLVED

---

### 5. ✅ DNS Resolution Failure

**Symptom:**
```
litellm.exceptions.APIError: OpenrouterException - [Errno -2] Name or service not known
```

**Root Cause:**
The Docker container couldn't resolve hostnames (DNS issue). The container didn't have access to the host's DNS resolver, preventing API calls to openrouter.ai.

**Solution:**
Add explicit DNS configuration to Docker command:
```bash
--dns 8.8.8.8      # Google DNS primary
--dns 8.8.4.4      # Google DNS secondary
```

**Implementation:**
```python
cmd.extend([
    "--dns", "8.8.8.8",
    "--dns", "8.8.4.4",
    "--add-host", "host.docker.internal:host-gateway",
    # ... rest of command
])
```

**Status:** ✅ RESOLVED

---

## Final Configuration

### Environment Variables (.env)
```bash
OPENHANDS_MODEL=gemini-flash
# OPENHANDS_CUSTOM_MODEL_ID=<commented out to use preset>
OPENHANDS_USE_DOCKER_RUNTIME=true
OPENHANDS_DOCKER_IMAGE=docker.all-hands.dev/all-hands-ai/openhands:0.59
OPENHANDS_DOCKER_RUNTIME_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik
```

### Docker Command Flags
```python
# TTY Detection
tty_flags = []
if sys.stdout.isatty():
    tty_flags.append("-t")
if sys.stdin.isatty():
    tty_flags.append("-i")

# Environment Variables
"-e", "MAX_ITERATIONS=100"
"-e", "AGENT_ENABLE_HISTORY_TRUNCATION=false"
"-e", "FILE_STORE=memory"
"-e", "FILE_STORE_PATH=/tmp/openhands_store"  # pragma: allowlist secret

# DNS Configuration
"--dns", "8.8.8.8"
"--dns", "8.8.4.4"

# Directory Creation
"sh", "-c", "mkdir -p /.openhands && python -m openhands.core.main -t '<task>'"
```

---

## Testing

Run the comprehensive test suite:
```bash
python scripts/test_openhands_integration.py
```

Expected output:
```
✅ PASS: Environment File
✅ PASS: Config Loading
✅ PASS: Docker Client Init
✅ PASS: Real Task Execution

Total: 4/4 tests passed
🎉 ALL TESTS PASSED! OpenHands integration is ready for production.
```

---

## Performance Metrics

- **Configuration Loading:** < 1 second
- **Docker Client Initialization:** < 2 seconds
- **Simple Task Execution:** 50-75 seconds (includes Docker startup, model inference, file creation)
- **Total Test Suite:** ~2 minutes

---

## Model Comparison

| Model | Context | Free | Status | Notes |
|-------|---------|------|--------|-------|
| gemini-flash | 1M | ✅ | ✅ Recommended | Large context, stable |
| deepseek-v3 | 64K | ✅ | ⚠️ Limited | May hit context limits |
| mistral-small | 32K | ✅ | ⚠️ Limited | Small context window |
| llama-scout | 190M | ✅ | ⚠️ Experimental | Very large but untested |

---

## Next Steps

1. ✅ Configuration verified
2. ✅ Docker integration working
3. ✅ Real API calls successful
4. ⏭️ TTA pipeline integration (next phase)
5. ⏭️ Batch processing setup
6. ⏭️ Production deployment

---

## Support

For issues not covered here:
1. Check Docker logs: `docker logs <container_id>`
2. Verify API key: `echo $OPENROUTER_API_KEY`
3. Test DNS: `docker run --rm alpine nslookup openrouter.ai`
4. Check network: `docker run --rm alpine ping 8.8.8.8`


---
**Logseq:** [[TTA.dev/Docs/Openhands_integration_troubleshooting]]
