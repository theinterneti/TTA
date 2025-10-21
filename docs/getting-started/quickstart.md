# Quick Start

Get up and running with TTA in under 5 minutes! This guide assumes you've already completed the [installation](installation.md).

## Start the Application

### 1. Start Backend Services

First, ensure Docker services are running:

```bash
# Start Neo4j and Redis
docker-compose up -d neo4j redis

# Verify services are healthy
docker-compose ps
```

Start the FastAPI backend:

```bash
# From the project root
uv run python src/player_experience/api/main.py
```

Expected output:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. Start Frontend (Optional)

In a new terminal, start the React frontend:

```bash
# Navigate to frontend directory
cd src/player_experience/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Expected output:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 3. Access the Application

Open your browser and navigate to:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474)

## Your First TTA Session

### Using the Web Interface

1. **Navigate to** [http://localhost:3000](http://localhost:3000)

2. **Sign In** using OAuth (GitHub, Google, etc.) or create a test account

3. **Create a New Story**:
   - Click "New Adventure"
   - Choose a therapeutic theme (e.g., "Anxiety Management", "Building Confidence")
   - Select difficulty level
   - Click "Start Adventure"

4. **Play the Game**:
   - Read the narrative presented by the AI
   - Choose from available actions
   - Watch the story adapt to your choices
   - Track your therapeutic progress

### Using the API

You can also interact with TTA programmatically using the REST API:

```bash
# Health check
curl http://localhost:8000/health

# Create a new session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "therapeutic_theme": "anxiety_management"
  }'

# Get session details
curl http://localhost:8000/api/v1/sessions/{session_id}

# Submit a player action
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/actions \
  -H "Content-Type: application/json" \
  -d '{
    "action": "explore_the_forest",
    "context": "Looking for a safe place to rest"
  }'
```

### Using the Python SDK

```python
from tta_ai_framework import TTAClient

# Initialize client
client = TTAClient(
    api_url="http://localhost:8000",
    api_key="your_api_key"  # pragma: allowlist secret - Optional for local development
)

# Create a new session
session = client.create_session(
    user_id="test_user",
    therapeutic_theme="anxiety_management",
    difficulty="medium"
)

# Get initial narrative
narrative = client.get_narrative(session.id)
print(narrative.text)

# Submit an action
response = client.submit_action(
    session_id=session.id,
    action="explore_the_forest",
    context="Looking for a safe place to rest"
)

print(response.narrative)
print(response.available_actions)
```

## Quick Tests

### Run Unit Tests

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/       # Integration tests only

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Run Quick Validation

```bash
# Validate environment setup
python scripts/validate_environment.py

# Run quick smoke tests
uv run pytest -q -m "not slow"

# Check system health
curl http://localhost:8000/health
```

## Common Tasks

### View Logs

```bash
# Backend logs (if running in terminal, logs appear in stdout)
# Or check application logs
tail -f logs/tta.log

# Docker service logs
docker-compose logs -f neo4j
docker-compose logs -f redis

# Frontend logs (in the terminal where npm run dev is running)
```

### Stop Services

```bash
# Stop backend (Ctrl+C in the terminal running the API)

# Stop frontend (Ctrl+C in the terminal running npm)

# Stop Docker services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Reset Database

```bash
# Stop services
docker-compose down -v

# Restart services (creates fresh databases)
docker-compose up -d neo4j redis

# Verify clean state
docker-compose ps
```

## Troubleshooting

### Port Already in Use

If you see "Address already in use" errors:

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
uv run python src/player_experience/api/main.py --port 8001
```

### Docker Services Not Starting

```bash
# Check Docker is running
docker ps

# Restart Docker daemon
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop (macOS/Windows)

# Check logs for errors
docker-compose logs neo4j
docker-compose logs redis
```

### Frontend Build Errors

```bash
# Clear node_modules and reinstall
cd src/player_experience/frontend
rm -rf node_modules package-lock.json
npm install

# Clear cache
npm cache clean --force
npm install
```

### API Connection Errors

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check environment variables
cat .env | grep -v "API_KEY"

# Verify Neo4j and Redis are accessible
docker-compose ps
```

## Next Steps

Now that you have TTA running:

1. **[Configuration Guide](configuration.md)**: Customize TTA settings
2. **[Development Guide](../development/contributing.md)**: Start contributing
3. **[API Documentation](../api/tta-application.md)**: Explore the API
4. **[Architecture Overview](../architecture/overview.md)**: Understand the system

## Additional Resources

- **[Testing Guide](../development/testing.md)**: Learn about the testing framework
- **[Component Maturity](../development/component-maturity.md)**: Understand the development workflow
- **[Troubleshooting](../../Documentation/docker/devcontainer_troubleshooting_guide.md)**: Common issues and solutions
