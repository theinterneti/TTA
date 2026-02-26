# TTA Deployment Guide

## Overview

TTA uses GitHub Actions for CI/CD. The pipeline has three stages:

1. **Tests** — runs on every push/PR (`.github/workflows/tests.yml`)
2. **Staging** — deploys automatically on push to `main`/`develop` (`.github/workflows/deploy-staging.yml`)
3. **Production** — manual trigger with approval gate (`.github/workflows/deploy-production.yml`)

All images are published to GitHub Container Registry (GHCR): `ghcr.io/<owner>/tta-*`

---

## Required GitHub Secrets

Configure these in **Settings → Secrets and variables → Actions**.

### Staging Deployment

| Secret | Description |
|---|---|
| `STAGING_SSH_HOST` | Hostname or IP of staging server |
| `STAGING_SSH_USER` | SSH username |
| `STAGING_SSH_PRIVATE_KEY` | Private SSH key (PEM format) |

### Production Deployment

| Secret | Description |
|---|---|
| `PROD_SSH_HOST` | Hostname or IP of production server |
| `PROD_SSH_USER` | SSH username |
| `PROD_SSH_PRIVATE_KEY` | Private SSH key (PEM format) |
| `PROD_SSH_KNOWN_HOSTS` | Known hosts entry (optional, auto-populated) |

### Post-Deployment Tests

| Secret | Description |
|---|---|
| `NEO4J_URI` | Neo4j bolt URI for staging (e.g. `bolt://localhost:7688`) |
| `NEO4J_USERNAME` | Neo4j username |
| `NEO4J_PASSWORD` | Neo4j password |
| `REDIS_HOST` | Redis host |
| `REDIS_PORT` | Redis port (default: `6379`) |
| `REDIS_PASSWORD` | Redis password (optional) |
| `TEST_USER_USERNAME` | Username for post-deployment test user |
| `TEST_USER_PASSWORD` | Password for post-deployment test user |
| `TEST_USER_EMAIL` | Email for post-deployment test user |

Production variants use the same names with `_PROD` suffix (e.g. `NEO4J_URI_PROD`).

---

## Required GitHub Variables

Configure in **Settings → Secrets and variables → Actions → Variables**.

| Variable | Description | Default |
|---|---|---|
| `STAGING_DEPLOY_PATH` | Deploy directory on staging server | `/opt/tta/staging` |
| `PROD_DEPLOY_PATH` | Deploy directory on production server | `/opt/tta/production` |
| `API_BASE_URL` | Staging API URL for health checks | `https://staging-api.tta.example.com` |
| `STAGING_API_BASE_URL` | Same (used by production pre-flight check) | same |
| `ENVIRONMENT_NAME` | Environment label for logs | `staging` / `production` |
| `LOG_LEVEL` | App log level | `INFO` |

---

## GitHub Environments

Two GitHub Environments must be configured (**Settings → Environments**):

### `staging`
- No required reviewers (auto-deploy on push to `main`)
- Optional: deployment URL = staging API URL

### `production`
- **Required reviewers**: add at least one reviewer (this is the manual approval gate)
- Optional: deployment URL = production API URL

---

## Server Setup (Staging & Production)

### Prerequisites
```bash
# On the deployment server
sudo apt-get install -y docker.io docker-compose-plugin
sudo usermod -aG docker $DEPLOY_USER

# Create deploy directory
sudo mkdir -p /opt/tta/staging
sudo chown $DEPLOY_USER:$DEPLOY_USER /opt/tta/staging

# Copy the repository (initial setup only)
git clone https://github.com/<owner>/TTA.git /opt/tta/staging
```

### SSH Key Setup
```bash
# On your local machine, generate a deploy key
ssh-keygen -t ed25519 -C "tta-deploy-staging" -f ~/.ssh/tta_staging_deploy

# Add public key to server
ssh-copy-id -i ~/.ssh/tta_staging_deploy.pub $DEPLOY_USER@$STAGING_HOST

# Add private key content to GitHub secret STAGING_SSH_PRIVATE_KEY
cat ~/.ssh/tta_staging_deploy
```

### Docker Login on Server
```bash
# The server needs to pull images from GHCR
# Option 1: Use a GitHub PAT with read:packages scope
echo $GITHUB_PAT | docker login ghcr.io -u <username> --password-stdin

# Option 2: The workflow uses GITHUB_TOKEN via the build step, not the server
# Images pushed during CI are public if the repo is public
```

---

## Deployment Workflow

### Staging (Automatic)

1. Push to `main` or `develop`
2. CI checks for deployment-relevant changes (`src/`, `Dockerfile*`, `pyproject.toml`)
3. Docker images built and pushed to GHCR with `staging-<sha>` tag
4. SSH into staging server → pull images → `docker compose up -d`
5. Health check (10 retries × 30s)
6. Post-deployment tests run against live staging environment
7. Rollback on failure

### Production (Manual)

1. Go to **Actions → Deploy to Production → Run workflow**
2. Enter version (git tag like `v1.0.0` or commit SHA)
3. Optionally skip staging health check
4. Workflow validates version, checks staging health, runs security checks
5. **GitHub Environment review gate** — assigned reviewers approve in the UI
6. Production images built and pushed (`prod-<sha>` tag)
7. Backup taken, deployment executed via SSH
8. Health check (15 retries × 30s)
9. Post-deployment tests (failures trigger rollback)
10. Deployment tagged in GitHub

### Rollback

Rollback is automatic on health check failure. The previous image tag is stored in `.pre-deploy-image-tag` on the server.

Manual rollback:
```bash
# On the deployment server
cd /opt/tta/staging
cat .pre-deploy-image-tag  # find previous tag
echo "staging" > .env.deploy  # or the specific tag
docker compose -f docker/compose/docker-compose.staging-homelab.yml up -d
```

---

## Running Post-Deployment Tests Locally

```bash
# Against local stack
API_BASE_URL=http://localhost:8080 \
DEPLOYMENT_ENV=local \
uv run pytest tests/post_deployment/ -v

# Against staging
API_BASE_URL=http://localhost:8081 \
DEPLOYMENT_ENV=staging \
TEST_USER_USERNAME=test_user \
TEST_USER_PASSWORD=TestPassword123! \
uv run pytest tests/post_deployment/ -v
```

---

## Monitoring After Deployment

- **Prometheus**: `:9091` (staging) / `:9090` (production)
- **Grafana**: `:3003` (staging) / `:3000` (production)
- **API health**: `GET /health`
- **API metrics**: `GET /metrics`
