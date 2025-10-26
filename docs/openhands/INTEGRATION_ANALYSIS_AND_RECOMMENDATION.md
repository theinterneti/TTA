# OpenHands Integration Analysis and Recommendation

**Date:** 2025-10-26  
**Status:** Complete Analysis with Clear Recommendation  
**Source:** Official OpenHands Documentation (Context7 Library ID: `/all-hands-ai/openhands`)

## Executive Summary

After comprehensive analysis of official OpenHands documentation and testing, **Docker headless mode is the recommended integration method** for automated test file generation. The OpenHands integration code in this repository was never implemented; this document provides the definitive approach.

## Integration Methods Comparison

| Method | File Creation | Bash Execution | Setup Complexity | Performance | Reliability | Recommendation |
|--------|---------------|----------------|------------------|-------------|-------------|-----------------|
| **SDK** | ❌ No | ❌ No | Low | Fast | High | ❌ Not suitable |
| **CLI** | ✅ Yes | ✅ Yes | Low | Medium | High | ✅ Alternative |
| **Docker** | ✅ Yes | ✅ Yes | Medium | Slow | High | ✅✅ **PRIMARY** |
| **REST API** | ❓ N/A | ❓ N/A | N/A | N/A | N/A | ❌ Not available |

## Detailed Analysis

### 1. SDK Mode (Python)
**Verdict:** ❌ **NOT SUITABLE**

- **Tools Available:** Only 2 tools: `think` and `finish`
- **File Creation:** ❌ Cannot create files
- **Bash Execution:** ❌ Cannot execute bash commands
- **Use Case:** Only for reasoning/planning tasks
- **Conclusion:** Fundamentally incompatible with test file generation

### 2. CLI Mode (Poetry/uv)
**Verdict:** ✅ **VIABLE ALTERNATIVE**

```bash
# Simple invocation
poetry run python -m openhands.core.main -t "Create test file"

# With repository context
export GITHUB_TOKEN="your-token"
poetry run python -m openhands.core.main \
  --selected-repo "owner/repo-name" \
  -t "Generate tests for module X"

# From task file
echo "Generate comprehensive tests" > task.txt
poetry run python -m openhands.core.main -f task.txt
```

**Advantages:**
- Simple setup (no Docker required)
- Full tool access (bash, file operations, etc.)
- Faster startup than Docker
- Good for development/testing

**Disadvantages:**
- Requires local Python environment
- Less isolated than Docker
- Harder to scale/parallelize

### 3. Docker Headless Mode (RECOMMENDED)
**Verdict:** ✅✅ **PRIMARY RECOMMENDATION**

```bash
# Official command structure
docker run -it \
    --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES=/path/to/workspace:/workspace:rw \
    -e LLM_API_KEY="your-api-key" \
    -e LLM_MODEL="openrouter/deepseek/deepseek-chat-v3.1:free" \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/.openhands \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app-$(date +%Y%m%d%H%M%S) \
    docker.all-hands.dev/all-hands-ai/openhands:0.59 \
    python -m openhands.core.main -t "Your task here"
```

**Advantages:**
- Full tool access (bash, file operations, browser, etc.)
- Isolated execution environment
- Scalable (can run multiple containers)
- Production-ready
- Consistent across environments

**Disadvantages:**
- Requires Docker installation
- Slower startup (30-40 seconds)
- More complex configuration

## Critical Configuration Details

### 1. Docker Flags
- **`-it`** (not just `-i`): Interactive + TTY mode required for proper headless execution
- **`--pull=always`**: Ensures latest images are used
- **`--rm`**: Automatic cleanup after execution

### 2. Environment Variables
```bash
# CRITICAL - Must match host user to avoid permission issues
SANDBOX_USER_ID=$(id -u)

# Workspace mounting format: /host/path:/container/path:mode
SANDBOX_VOLUMES=/path/to/workspace:/workspace:rw

# LLM Model MUST include provider prefix
# Format: provider/model-name or provider/organization/model-name
LLM_MODEL="openrouter/deepseek/deepseek-chat-v3.1:free"

# Enable JSON event logging
LOG_ALL_EVENTS=true
```

### 3. Volume Mounts
```bash
# Docker socket (required for Docker-in-Docker)
-v /var/run/docker.sock:/var/run/docker.sock

# OpenHands config directory
-v ~/.openhands:/.openhands

# Workspace (where files are created)
-e SANDBOX_VOLUMES=/path/to/workspace:/workspace:rw
```

### 4. Image Versions
- **OpenHands Main:** `docker.all-hands.dev/all-hands-ai/openhands:0.59`
- **Runtime:** `docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik`
- **Note:** Documentation shows 0.54, but 0.59 is latest stable

## Implementation Recommendation

### For Test File Generation

**Use Docker headless mode with the following approach:**

1. **Create a wrapper script** that:
   - Accepts task description as input
   - Sets up workspace directory
   - Configures LLM credentials
   - Executes Docker container
   - Captures output and validates file creation

2. **Configuration:**
   - Use OpenRouter API for LLM access (supports free models)
   - Mount workspace at `/workspace` in container
   - Set `SANDBOX_USER_ID` to current user
   - Enable `LOG_ALL_EVENTS` for debugging

3. **Error Handling:**
   - Detect LLM configuration errors (invalid model format)
   - Handle permission issues (`.openhands` directory)
   - Validate file creation in workspace
   - Implement retry logic with model rotation

## Known Issues and Workarounds

### Issue 1: Permission Errors on `.openhands` Directory
**Symptom:** `Permission denied: /.openhands/sessions/`

**Solution:**
```bash
# Fix permissions from previous runs
sudo chown -R $(id -u):$(id -g) ~/.openhands
chmod -R u+w ~/.openhands

# Or remove and recreate
rm -rf ~/.openhands/sessions
mkdir -p ~/.openhands/sessions
```

### Issue 2: Invalid LLM Model Format
**Symptom:** `litellm.BadRequestError: LLM Provider NOT provided`

**Solution:** Ensure model includes provider prefix:
```bash
# ❌ WRONG
-e LLM_MODEL="test-model"

# ✅ CORRECT
-e LLM_MODEL="openrouter/deepseek/deepseek-chat-v3.1:free"
```

### Issue 3: Container Startup Timeout
**Symptom:** Container exits without output

**Solution:**
- Increase timeout to 60+ seconds
- Verify Docker daemon is running
- Check Docker socket permissions

## Next Steps

1. **Implement Docker wrapper** in `src/agent_orchestration/openhands_integration/`
2. **Create configuration management** for LLM credentials and workspace paths
3. **Add error handling and retry logic** with model rotation
4. **Test with real LLM credentials** (OpenRouter API key)
5. **Validate file creation** in workspace after execution
6. **Document usage patterns** for test generation tasks

## References

- **Official Documentation:** https://github.com/all-hands-ai/openhands
- **Headless Mode Guide:** https://docs.all-hands.dev/openhands/usage/how-to/headless-mode
- **Docker Runtime:** https://docs.all-hands.dev/openhands/usage/runtimes/docker
- **Configuration Options:** https://docs.all-hands.dev/openhands/usage/configuration-options

