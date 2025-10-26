# OpenHands Docker Integration - Quick Start Guide

## One-Minute Setup

### Prerequisites
```bash
# 1. Docker installed and running
docker --version

# 2. OpenRouter API key (free tier available)
export OPENROUTER_API_KEY="your-key-here"

# 3. Workspace directory
mkdir -p /tmp/openhands-workspace
```

### Run Your First Task
```bash
# Create workspace
WORKSPACE="/tmp/openhands-workspace"
mkdir -p "$WORKSPACE"

# Run OpenHands
docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES="$WORKSPACE:/workspace:rw" \
    -e LLM_API_KEY="$OPENROUTER_API_KEY" \
    -e LLM_MODEL="openrouter/deepseek/deepseek-chat-v3.1:free" \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/.openhands \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app-$(date +%s) \
    docker.all-hands.dev/all-hands-ai/openhands:0.59 \
    python -m openhands.core.main -t "Create a file named hello.txt with content 'Hello from OpenHands'"

# Verify file was created
ls -la "$WORKSPACE/"
cat "$WORKSPACE/hello.txt"
```

## Common Tasks

### Generate Test File
```bash
docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES="/path/to/project:/workspace:rw" \
    -e LLM_API_KEY="$OPENROUTER_API_KEY" \
    -e LLM_MODEL="openrouter/deepseek/deepseek-chat-v3.1:free" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/.openhands \
    --add-host host.docker.internal:host-gateway \
    docker.all-hands.dev/all-hands-ai/openhands:0.59 \
    python -m openhands.core.main -t "Generate comprehensive unit tests for src/module.py"
```

### Fix Permissions Issue
```bash
# If you get "Permission denied: /.openhands/sessions/"
sudo chown -R $(id -u):$(id -g) ~/.openhands
chmod -R u+w ~/.openhands
```

### Debug Output
```bash
# Add to docker run command to see all events:
-e LOG_ALL_EVENTS=true

# Capture output to file:
docker run ... 2>&1 | tee openhands-output.log
```

## Environment Variables Reference

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `SANDBOX_RUNTIME_CONTAINER_IMAGE` | Yes | `docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik` | Runtime container image |
| `SANDBOX_USER_ID` | Yes | `$(id -u)` | Match host user permissions |
| `SANDBOX_VOLUMES` | Yes | `/path:/workspace:rw` | Mount workspace directory |
| `LLM_API_KEY` | Yes | `your-api-key` | LLM provider API key |
| `LLM_MODEL` | Yes | `openrouter/deepseek/...` | Model with provider prefix |
| `LOG_ALL_EVENTS` | No | `true` | Enable JSON event logging |
| `GITHUB_TOKEN` | No | `your-token` | For GitHub operations |

## Troubleshooting

### Container exits immediately
- Check Docker daemon is running: `docker ps`
- Verify LLM_MODEL format includes provider: `openrouter/deepseek/...`
- Check API key is valid

### Permission denied errors
```bash
# Fix .openhands directory permissions
rm -rf ~/.openhands/sessions
mkdir -p ~/.openhands/sessions
```

### Files not created in workspace
- Verify SANDBOX_VOLUMES path exists: `ls -la /path/to/workspace`
- Check SANDBOX_USER_ID matches current user: `id -u`
- Verify task description is clear and specific

### LLM errors
- Ensure model format: `provider/model-name` (e.g., `openrouter/deepseek/deepseek-chat-v3.1:free`)
- Verify API key is valid for the provider
- Check rate limits (may need to rotate models)

## Free LLM Models (OpenRouter)

```bash
# DeepSeek V3 (free tier)
openrouter/deepseek/deepseek-chat-v3.1:free

# Mistral Small (free tier)
openrouter/mistral/mistral-small:free

# Llama Scout (free tier)
openrouter/meta-llama/llama-3.2-1b:free
```

## Next Steps

1. **Test with your project:** Mount your actual project directory
2. **Automate:** Create wrapper script for batch processing
3. **Monitor:** Use `LOG_ALL_EVENTS=true` to capture execution details
4. **Scale:** Run multiple containers in parallel for batch tasks

## References

- **Full Documentation:** `docs/openhands/INTEGRATION_ANALYSIS_AND_RECOMMENDATION.md`
- **Official Docs:** https://docs.all-hands.dev/openhands/usage/how-to/headless-mode
- **OpenRouter API:** https://openrouter.ai/

