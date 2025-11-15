# Docker Desktop WSL2 Integration Setup

**Status**: ⚠️ Docker Compose not currently accessible in WSL2
**Created**: November 1, 2025
**Required For**: Neo4j, Redis, and Grafana services

---

## Problem

Currently getting error when trying to run Docker Compose:

```bash
$ docker-compose ps
The command 'docker-compose' could not be found in this WSL 2 distro.
We recommend to activate the WSL integration in Docker Desktop settings.

For details about using Docker Desktop with WSL 2, visit:
https://docs.docker.com/go/wsl2/
```

---

## Solution: Enable Docker Desktop WSL2 Integration

### Step 1: Install Docker Desktop for Windows

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install Docker Desktop on Windows (not inside WSL)
3. Restart Windows if prompted

### Step 2: Enable WSL2 Backend

1. Open Docker Desktop
2. Go to **Settings** (gear icon in top right)
3. Navigate to **General**
4. Ensure **Use the WSL 2 based engine** is checked
5. Click **Apply & Restart**

### Step 3: Enable WSL Integration for Your Distro

1. In Docker Desktop Settings, go to **Resources** → **WSL Integration**
2. Enable **Enable integration with my default WSL distro**
3. Find your WSL distro in the list (likely "Ubuntu" or similar)
4. Toggle it **ON**
5. Click **Apply & Restart**

### Step 4: Verify Installation

Open your WSL terminal and run:

```bash
# Check Docker is available
docker --version

# Check Docker Compose is available
docker-compose --version

# Test Docker connectivity
docker run hello-world
```

Expected output:
```
Docker version 24.0.x, build xxxxx
Docker Compose version v2.x.x
Hello from Docker!
...
```

---

## TTA Services Setup

Once Docker is configured, start the TTA development services:

### Quick Start

```bash
cd /home/thein/recovered-tta-storytelling

# Start all development services
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.dev.yml up -d

# Or use the management script
bash docker/scripts/tta-docker.sh dev up -d
```

### Verify Services

```bash
# Check service status
docker-compose ps

# Test database connections
uv run python scripts/test_database_connections.py
```

### Access Services

Once running, services are available at:

- **Neo4j Browser**: http://localhost:7474
  - Username: `neo4j`
  - Password: Check `.env.dev` or `secrets/neo4j.env`

- **Redis**: `localhost:6379`
  - Test: `redis-cli ping` (should return `PONG`)

- **Redis Commander**: http://localhost:8081
  - Web UI for Redis inspection

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: Check `.env.dev` or `secrets/grafana.env`

---

## Common Issues

### Issue: "Cannot connect to the Docker daemon"

**Solution**: Make sure Docker Desktop is running in Windows
- Check the system tray for Docker icon
- If not running, start Docker Desktop from Start Menu

### Issue: "docker-compose: command not found"

**Solution**: Docker Compose V2 uses `docker compose` (no hyphen)
- Use: `docker compose` instead of `docker-compose`
- Or install Docker Compose V1: `sudo apt-get install docker-compose`

### Issue: WSL distro not listed in Docker Desktop

**Solution**:
1. Ensure WSL2 is properly installed: `wsl --list --verbose`
2. Update WSL: `wsl --update`
3. Restart Docker Desktop
4. Check distro appears in Settings → Resources → WSL Integration

### Issue: Permission denied when running docker commands

**Solution**: Add your user to docker group
```bash
# This might not work in WSL2, use sudo or check Docker Desktop settings
sudo usermod -aG docker $USER
# Then logout and login again
```

---

## Troubleshooting Commands

```bash
# Check WSL version
wsl --version

# Check WSL distributions
wsl --list --verbose

# Restart WSL
wsl --shutdown
# Then reopen WSL terminal

# Check Docker daemon status
docker info

# View Docker Desktop logs
# In Docker Desktop → Troubleshoot → View Logs

# Test network connectivity
ping host.docker.internal
```

---

## Alternative: Use Dev Containers

If Docker Desktop integration doesn't work, consider using VS Code Dev Containers:

1. Install "Dev Containers" extension in VS Code
2. Open project in VS Code
3. Press `F1` → "Dev Containers: Reopen in Container"
4. Services will start automatically

---

## Environment Files

Ensure these files exist with correct credentials:

```bash
# Main environment file
.env.dev

# Service-specific secrets
secrets/neo4j.env
secrets/redis.env
secrets/grafana.env
```

If missing, copy from examples:
```bash
cp .env.example .env.dev
cp secrets/neo4j.env.example secrets/neo4j.env
cp secrets/redis.env.example secrets/redis.env
```

---

## Testing After Setup

Run the comprehensive database connection test:

```bash
uv run python scripts/test_database_connections.py
```

Expected output:
```
✅ Neo4j connection: SUCCESS
✅ Redis connection: SUCCESS
✅ Neo4j query test: SUCCESS
✅ Redis operation test: SUCCESS

All database connections working!
```

---

## Next Steps After Setup

1. ✅ Verify all services are running
2. ✅ Test database connectivity
3. ✅ Run integration tests that require databases:
   ```bash
   uv run pytest tests/integration/ --neo4j --redis -v
   ```
4. ✅ Start development server:
   ```bash
   uv run python src/main.py start
   ```

---

## Resources

- **Docker Desktop WSL2**: https://docs.docker.com/desktop/wsl/
- **WSL Documentation**: https://learn.microsoft.com/en-us/windows/wsl/
- **TTA Docker Setup**: `docker/README.md`
- **Database Quick Reference**: `.vscode/DATABASE_QUICK_REF.md`

---

**Status**: 🔧 Follow the steps above to enable Docker integration

Once completed, update this file with ✅ and any lessons learned!
