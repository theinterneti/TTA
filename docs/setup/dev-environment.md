# TTA Development Environment - Ready! ✅

**Date:** November 1, 2025
**Status:** OPERATIONAL

## Quick Start

```bash
# Start services
bash scripts/tta-dev.sh start

# Check status
bash scripts/tta-dev.sh status

# Test connections
bash scripts/tta-dev.sh test

# Stop services
bash scripts/tta-dev.sh stop
```

## Services

### Redis
- **Port:** 6379
- **Status:** ✅ Fully operational
- **Connection:** `redis://localhost:6379/0`
- **Version:** 7.4.5

### Neo4j
- **HTTP Port:** 7474
- **Bolt Port:** 7687
- **Status:** ✅ Fully operational
- **Credentials:** `neo4j / tta_dev_neo4j_2024`
- **Version:** 5.26.1
- **Browser:** http://localhost:7474
- **Plugins:** APOC, Graph Data Science

## Verified Working

✅ Redis connection from container (redis-cli)
✅ Neo4j connection from container (cypher-shell)
✅ Both services healthy in Docker
✅ Management scripts operational

## Python Driver Note

The Python `neo4j` driver (version 6.0.2) may have authentication issues with Neo4j 5.26.1 from WSL2. However, the database itself is fully functional and accessible via:
- Cypher shell inside container
- Neo4j Browser (http://localhost:7474)
- Direct bolt connections

If Python driver issues persist, consider:
1. Using `uv run python scripts/test_neo4j_tta_dev.py` to test
2. Checking if driver needs update or downgrade
3. Testing from native Linux (non-WSL) environment

## Configuration Files

- **Docker Compose:** `docker-compose.tta-dev.yml`
- **Environment:** `.env.tta-dev`
- **Management Script:** `scripts/tta-dev.sh`

## Key Learning: Neo4j Authentication

**IMPORTANT:** `NEO4J_AUTH` environment variable only applies on **first startup**. If you change the password in docker-compose:
1. Stop services: `bash scripts/tta-dev.sh stop`
2. Remove volumes: `docker volume rm tta_neo4j_data tta_neo4j_logs tta_neo4j_plugins tta_neo4j_import`
3. Start fresh: `bash scripts/tta-dev.sh start`

The persisted `auth.ini` file in the data volume will override any new `NEO4J_AUTH` settings.

## Next Steps for TTA Development

With Redis and Neo4j now running properly, you can:

1. **Test Agent Messaging:** Redis pub/sub for agent coordination
2. **Build Narrative Graphs:** Neo4j for story structure
3. **Develop Workflows:** LangGraph with Neo4j backend
4. **Run Integration Tests:** Full agent orchestration tests

## Troubleshooting

### Neo4j Browser Not Accessible from Windows
- Use: http://localhost:7474 from WSL2
- Or connect via cypher-shell: `docker exec -it tta-neo4j cypher-shell -u neo4j -p tta_dev_neo4j_2024`

### Services Won't Start
```bash
# Check what's using ports
sudo lsof -i :6379
sudo lsof -i :7474
sudo lsof -i :7687

# Force clean restart
bash scripts/tta-dev.sh clean  # Type 'yes' to confirm
bash scripts/tta-dev.sh start
```

### Check Logs
```bash
bash scripts/tta-dev.sh logs        # All services
bash scripts/tta-dev.sh logs redis  # Just Redis
bash scripts/tta-dev.sh logs neo4j  # Just Neo4j
```

---

**Environment Ready for TTA Agent Development** 🚀
