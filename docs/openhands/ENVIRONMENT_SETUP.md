# OpenHands Environment Setup Guide

This guide explains how to configure the OpenHands integration with the OpenRouter API for automated test generation.

## Prerequisites

- Docker installed and running
- Python 3.10+
- OpenRouter API key (free tier available)
- `.env` file in the repository root

## Step 1: Get OpenRouter API Key

1. Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key (format: `sk-or-v1-...`)

## Step 2: Configure .env File

The `.env` file should already exist in the repository root with the following variables:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_SHOW_FREE_ONLY=false
OPENROUTER_PREFER_FREE_MODELS=true
OPENROUTER_MAX_COST_PER_TOKEN=0.001
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | ✅ Yes | - | OpenRouter API key for authentication |
| `OPENHANDS_MODEL` | ❌ No | `gemini-flash` | Model preset: `deepseek-v3`, `mistral-small`, `gemini-flash`, `llama-scout`, `deepseek-r1` |
| `OPENHANDS_CUSTOM_MODEL_ID` | ❌ No | - | Full model ID (e.g., `openrouter/deepseek/deepseek-chat-v3.1:free`) |
| `OPENHANDS_BASE_URL` | ❌ No | `https://openrouter.ai/api/v1` | OpenRouter API base URL |
| `OPENHANDS_WORKSPACE_ROOT` | ❌ No | `./openhands_workspace` | Root directory for workspaces |
| `OPENHANDS_TIMEOUT` | ❌ No | `300.0` | Task execution timeout in seconds |
| `OPENHANDS_ENABLE_CIRCUIT_BREAKER` | ❌ No | `true` | Enable circuit breaker for fault tolerance |
| `OPENHANDS_USE_DOCKER_RUNTIME` | ❌ No | `false` | Use Docker runtime mode |
| `OPENHANDS_DOCKER_IMAGE` | ❌ No | `docker.all-hands.dev/all-hands-ai/openhands:0.59` | OpenHands Docker image |
| `OPENHANDS_DOCKER_RUNTIME_IMAGE` | ❌ No | `docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik` | Sandbox runtime image |
| `OPENHANDS_DOCKER_TIMEOUT` | ❌ No | `600.0` | Docker execution timeout in seconds |

## Step 3: Verify Configuration

Run the configuration test to verify everything is set up correctly:

```bash
python scripts/test_openhands_config_loading.py
```

Expected output:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              OpenHands Configuration Loading Test                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
Step 1: Verify .env file
================================================================================
✓ .env file found at /home/thein/recovered-tta-storytelling/.env
✓ OPENROUTER_API_KEY found in .env file
  - Key: sk-or-v1-c6dbf1feb25...

================================================================================
Step 2: Load configuration from environment
================================================================================
✓ Configuration loaded successfully
  - API Key: sk-or-v1-c6dbf1feb25...
  - Model Preset: deepseek-v3
  - Base URL: https://openrouter.ai/api/v1
  - Workspace Root: ./openhands_workspace
  - Default Timeout: 300.0s
  - Max Retries: 3
  - Circuit Breaker Enabled: True

================================================================================
Step 3: Create client configuration
================================================================================
✓ Client configuration created successfully
  - API Key: sk-or-v1-c6dbf1feb25...
  - Model: openrouter/deepseek/deepseek-chat-v3.1:free
  - Base URL: https://openrouter.ai/api/v1
  - Workspace Path: ./openhands_workspace
  - Timeout: 300.0s

================================================================================
Step 4: Initialize DockerOpenHandsClient
================================================================================
✓ DockerOpenHandsClient initialized successfully
  - OpenHands Image: docker.all-hands.dev/all-hands-ai/openhands:0.59
  - Runtime Image: docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik
  - Config Model: openrouter/deepseek/deepseek-chat-v3.1:free

================================================================================
Step 5: Test Docker command construction
================================================================================
✓ Docker command constructed successfully
  - Command length: 25 arguments
  - Docker image: docker.all-hands.dev/all-hands-ai/openhands:0.59

  Key command components:
    - -it
    - --rm
    - --pull=always
    - -e
    - Image: docker.all-hands.dev/all-hands-ai/openhands:0.59

================================================================================
SUMMARY
================================================================================
1. .env file                           ✅ PASS
2. Config loading                      ✅ PASS
3. Client config                       ✅ PASS
4. Docker client init                  ✅ PASS
5. Docker command                      ✅ PASS

================================================================================
✅ ALL TESTS PASSED - Configuration is correct!

Next steps:
1. Run: python scripts/test_openhands_with_real_credentials.py
2. This will execute a real task via Docker with OpenRouter API
3. Verify that files are created in the workspace
================================================================================
```

## Step 4: Test with Real Credentials

Once configuration is verified, test the integration with real OpenRouter API:

```bash
python scripts/test_openhands_with_real_credentials.py
```

This will:
1. Load configuration from `.env`
2. Initialize the Docker client
3. Execute a test task: "Create a file named 'openhands_test.txt' with content 'Hello from OpenHands'"
4. Verify that the file is created in the workspace
5. Report success/failure with diagnostics

## Step 5: Troubleshooting

### Issue: "OPENROUTER_API_KEY environment variable is required"

**Solution:** Ensure `.env` file exists in the repository root and contains:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key
```

### Issue: Docker command fails with "image not found"

**Solution:** Pull the required Docker images:
```bash
docker pull docker.all-hands.dev/all-hands-ai/openhands:0.59
docker pull docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik
```

### Issue: Permission denied errors in Docker

**Solution:** Ensure Docker daemon is running and your user has permission:
```bash
# Check Docker status
docker ps

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: Task execution timeout

**Solution:** Increase the timeout in `.env`:
```bash
OPENHANDS_TIMEOUT=600.0  # 10 minutes instead of 5
```

## Configuration for Different Environments

### Local Development

```bash
OPENHANDS_MODEL=gemini-flash
OPENHANDS_TIMEOUT=300.0
OPENHANDS_ENABLE_CIRCUIT_BREAKER=true
```

### CI/CD Pipeline

```bash
OPENHANDS_MODEL=deepseek-v3
OPENHANDS_TIMEOUT=600.0
OPENHANDS_ENABLE_CIRCUIT_BREAKER=true
OPENHANDS_USE_DOCKER_RUNTIME=true
```

### Production

```bash
OPENHANDS_MODEL=deepseek-v3
OPENHANDS_TIMEOUT=900.0
OPENHANDS_ENABLE_CIRCUIT_BREAKER=true
OPENHANDS_USE_DOCKER_RUNTIME=true
OPENHANDS_DOCKER_TIMEOUT=1200.0
```

## Next Steps

1. ✅ Configure `.env` file with OpenRouter API key
2. ✅ Run configuration test: `python scripts/test_openhands_config_loading.py`
3. ✅ Test with real credentials: `python scripts/test_openhands_with_real_credentials.py`
4. 📋 Integrate with TTA test generation pipeline
5. 📊 Monitor and optimize performance

## API Key Security

⚠️ **Important:** Never commit the `.env` file to version control. The `.gitignore` file should already exclude it:

```bash
# Verify .env is in .gitignore
grep "^\.env$" .gitignore
```

For CI/CD environments, use repository secrets instead:
- GitHub Actions: Settings → Secrets and variables → Actions
- GitLab CI: Settings → CI/CD → Variables
- Other platforms: Refer to your platform's documentation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review OpenRouter documentation: https://openrouter.ai/docs
3. Check OpenHands documentation: https://docs.all-hands.ai
4. Review the integration documentation: `docs/openhands/INTEGRATION_ANALYSIS_AND_RECOMMENDATION.md`
