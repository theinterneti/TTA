# Player Experience API Test Template

When the Player Experience API is running on port 8080, record these scenarios:

## Authentication Tests
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout

## Character Management
- POST /api/characters
- GET /api/characters/:id
- PUT /api/characters/:id
- DELETE /api/characters/:id

## Story/Narrative
- POST /api/narratives/start
- GET /api/narratives/:id
- POST /api/narratives/:id/choice
- GET /api/narratives/:id/history

## Therapeutic Features
- POST /api/therapeutic/assessment
- GET /api/therapeutic/progress/:user_id
- POST /api/therapeutic/reflection

## Recording Command:
```bash
# Start Player Experience API
uv run uvicorn src.player_experience.api.app:app --host 0.0.0.0 --port 8080 &

# Record tests
./record-player-api.sh
```
