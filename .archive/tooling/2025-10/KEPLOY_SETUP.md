# Keploy Setup Guide for TTA

## What is Keploy?

Keploy is a developer-centric API testing tool that:
- **Records** your API traffic and converts it to tests
- **Generates** mocks automatically (no need for Redis/Neo4j during testing!)
- **Runs** tests faster than unit tests
- Works **locally** - no deployment required!

## Installation

```bash
# Install Keploy agent (Linux/Mac)
curl --silent -O -L https://keploy.io/install.sh && source install.sh
```

## Your API URLs (No Hosting Required!)

Keploy works with your **local development server**. Choose based on what you want to test:

### Option 1: Main Player Experience API (Recommended)
```bash
# Your API will run at: http://localhost:8080
# Command to start: python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080
```

### Option 2: Minimal Test API (Simpler, fewer dependencies)
```bash
# Your API will run at: http://localhost:8000
# Command to start: python scripts/minimal_api_server.py
```

### Option 3: Simple Demo API (Lightest)
```bash
# Your API will run at: http://localhost:8000
# Command to start: python simple_api_server.py
```

## Step-by-Step: Record Tests

### 1. Start Recording with Keploy

**For Main API:**
```bash
keploy record -c "python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080"
```

**For Minimal API:**
```bash
keploy record -c "python scripts/minimal_api_server.py"
```

**For Simple API:**
```bash
keploy record -c "python simple_api_server.py"
```

### 2. Use Your API

Open another terminal and make API calls:

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test root endpoint
curl http://localhost:8080/

# Test authentication
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Test gameplay
curl -X POST http://localhost:8080/api/v1/gameplay/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"world_id": "fantasy-world"}'
```

### 3. Stop Recording

Press `Ctrl+C` in the Keploy terminal. Keploy will save:
- Test cases in `keploy/tests/`
- Mocks in `keploy/mocks/`

## Run Tests (No External Services Needed!)

```bash
# Stop Redis and Neo4j - Keploy doesn't need them!
docker-compose down

# Run tests with Keploy
keploy test -c "python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080" --delay 10
```

The `--delay 10` gives your server 10 seconds to start before tests run.

## Advanced: Generate Tests from OpenAPI Schema

Your TTA API already has OpenAPI docs! Use them:

```bash
# First, save your OpenAPI schema
curl http://localhost:8080/openapi.json > schema.json

# Generate tests from schema
keploy generate-tests -c "python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080" -s "schema.json"
```

## Configuration File (Optional)

Create `keploy.yaml` in your project root:

```yaml
# keploy.yaml
path: "keploy"  # Where to store tests
command: "python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080"
port: 8080
delay: 10
disableMockUpload: true  # Don't upload to cloud (keep local)
```

Then simply run:
```bash
keploy record  # Uses config file
keploy test    # Uses config file
```

## Integration with TTA Tasks

Add to `.vscode/tasks.json`:

```json
{
    "label": "🧪 Keploy: Record API Tests",
    "type": "shell",
    "command": "keploy record -c 'python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080'"
},
{
    "label": "🧪 Keploy: Run API Tests",
    "type": "shell",
    "command": "keploy test -c 'python -m uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080' --delay 10"
}
```

## Key Benefits for TTA

✅ **No Mocking Work**: Keploy auto-generates mocks for Redis, Neo4j, OpenRouter
✅ **Real Traffic**: Tests based on actual API usage, not assumptions
✅ **Fast**: Runs without starting external services
✅ **Regression Testing**: Catch breaking changes automatically
✅ **Multi-Agent Safe**: Works with your circuit breaker patterns

## Troubleshooting

### "Connection refused"
- Make sure your API server is actually starting
- Check the port isn't already in use: `lsof -i :8080`

### "Tests failing"
- Ensure you recorded tests with the same command you're testing with
- Check `keploy/tests/` to see what was recorded

### "Mocks not working"
- Keploy auto-generates mocks from recorded traffic
- If you need specific mock behavior, record that scenario first

## Next Steps

1. **Start simple**: Record health/root endpoints first
2. **Add complexity**: Record full user journeys (login → start game → action)
3. **Automate**: Add to CI/CD pipeline (GitHub Actions)
4. **Deduplicate**: Remove redundant tests with `keploy dedup`

## Resources

- [Keploy Docs](https://github.com/keploy/keploy)
- TTA API Docs: `http://localhost:8080/docs` (when server running)
- Your API structure: `tests/test_api_structure.py`


---
**Logseq:** [[TTA.dev/.archive/Tooling/2025-10/Keploy_setup]]
