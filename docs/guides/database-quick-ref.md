# TTA Database Quick Reference 🚀

**Single-Instance Setup with Logical Separation**

## Quick Start

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Setup Neo4j databases
uv run python scripts/setup_neo4j_databases.py

# Test connections
uv run python scripts/test_database_connections.py
```

## Connection Examples

### Neo4j - Development
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "tta_password_2024")
)

# Use dev database
with driver.session(database="tta_dev") as session:
    result = session.run("CREATE (n:Character {name: $name})", name="Hero")
```

### Neo4j - Testing
```python
# Use test database (automatically cleared between tests)
with driver.session(database="tta_test") as session:
    result = session.run("MATCH (n) RETURN count(n)")
```

### Redis - Development
```python
import redis

# Development cache (DB 0)
r_dev = redis.Redis(host='localhost', port=6379, db=0)
r_dev.set('player:123', 'data')

# Test cache (DB 1)
r_test = redis.Redis(host='localhost', port=6379, db=1)
r_test.set('test_key', 'test_value')
```

## Environment Variables

```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tta_password_2024
NEO4J_DATABASE=tta_dev          # or tta_test, tta_staging

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0                      # or 1 (test), 2 (staging)
```

## Database Management

### Neo4j

```cypher
-- List all databases
SHOW DATABASES;

-- Switch database in Browser
:use tta_dev
:use tta_test

-- Clear a database
:use tta_dev
MATCH (n) DETACH DELETE n;
```

### Redis

```bash
# Select database
redis-cli
SELECT 0  # dev
SELECT 1  # test

# Clear specific database
redis-cli -n 0 FLUSHDB  # Clear dev only

# View all keys in a database
redis-cli -n 0 KEYS *
```

## Access Points

- **Neo4j Browser**: http://localhost:7474
- **Redis Commander**: http://localhost:8081
- **Grafana** (optional): http://localhost:3000

## Common Tasks

### Backup Neo4j Database
```bash
# Backup tta_dev
docker exec tta-neo4j neo4j-admin database dump tta_dev \
  --to-path=/var/lib/neo4j/import/backups

# Copy to host
docker cp tta-neo4j:/var/lib/neo4j/import/backups ./backups/
```

### Restore Neo4j Database
```bash
# Copy to container
docker cp ./backups/tta_dev.dump tta-neo4j:/var/lib/neo4j/import/

# Restore
docker exec tta-neo4j neo4j-admin database load tta_dev \
  --from-path=/var/lib/neo4j/import
```

### Clear Test Data
```bash
# Clear test database
docker exec tta-neo4j cypher-shell -u neo4j -p tta_password_2024 \
  -d tta_test "MATCH (n) DETACH DELETE n"

# Clear test Redis
docker exec tta-redis redis-cli -n 1 FLUSHDB
```

## Code Patterns

### Repository Pattern with Database Selection
```python
class PlayerRepository:
    def __init__(self, neo4j_driver, database="tta_dev"):
        self.driver = neo4j_driver
        self.database = database

    def create_player(self, player_id, name):
        with self.driver.session(database=self.database) as session:
            session.run(
                "CREATE (p:Player {id: $id, name: $name})",
                id=player_id, name=name
            )

# Development
repo_dev = PlayerRepository(driver, database="tta_dev")

# Testing
repo_test = PlayerRepository(driver, database="tta_test")
```

### Testing with Isolated Databases
```python
import pytest
from neo4j import GraphDatabase

@pytest.fixture(scope="function")
def neo4j_session():
    """Provides clean Neo4j test database"""
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "tta_password_2024")
    )

    # Use test database
    session = driver.session(database="tta_test")

    yield session

    # Cleanup after test
    session.run("MATCH (n) DETACH DELETE n")
    session.close()
    driver.close()
```

## Troubleshooting

### Neo4j won't start
```bash
# Check logs
docker logs tta-neo4j

# Restart
docker restart tta-neo4j

# Verify health
docker exec tta-neo4j wget --spider http://localhost:7474
```

### Can't connect to Neo4j
```bash
# Check if running
docker ps | grep neo4j

# Test connection
docker exec tta-neo4j cypher-shell -u neo4j -p tta_password_2024 "RETURN 1"
```

### Database doesn't exist
```bash
# Create missing databases
uv run python scripts/setup_neo4j_databases.py

# Or manually
docker exec tta-neo4j cypher-shell -u neo4j -p tta_password_2024 \
  -d system "CREATE DATABASE tta_dev IF NOT EXISTS"
```

### Redis connection refused
```bash
# Check if running
docker ps | grep redis

# Test connection
docker exec tta-redis redis-cli ping
```

## Migration from Old Setup

```bash
# Automated migration
./scripts/migrate_to_simple_setup.sh

# Manual check
docker-compose down  # Stop old
docker-compose -f docker-compose.dev.yml up -d  # Start new
```

## Future: When to Use Multiple Instances

✅ **Keep single instance for:**
- Local development
- Testing
- Staging experiments

🔄 **Use multiple instances for:**
- Production deployment (see issue template)
- CI/CD parallel testing (see issue template)
- Version migration testing (see issue template)

## Documentation

- Full guide: `docs/setup/SIMPLIFIED_DOCKER_SETUP.md`
- Migration docs: `MIGRATION_COMPLETE.md`
- Issue templates: `.github/ISSUE_TEMPLATE/`

---

**Last Updated**: October 27, 2025
**Setup**: Simplified single-instance approach
**Status**: ✅ Active


---
**Logseq:** [[TTA.dev/Docs/Guides/Database-quick-ref]]
