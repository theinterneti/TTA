# Simplified Docker Setup for TTA

**Why This Approach?**
- ✅ **Simpler**: One Neo4j, one Redis instead of multiple instances
- ✅ **Less resource usage**: Single Neo4j uses ~2GB RAM instead of 4-6GB
- ✅ **Easier troubleshooting**: Fewer moving parts
- ✅ **Cleaner AI context**: One connection string to remember
- ✅ **Standard practice**: Most teams use logical separation, not instance separation

## Quick Start

### 1. Start Services

```bash
# Stop any existing instances first
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.staging.yml down

# Start simplified stack
docker-compose -f docker-compose.simple.yml up -d
```

### 2. Setup Neo4j Databases

```bash
# Copy the simplified environment file
cp .env.simple .env

# Create databases for each environment
uv run python scripts/setup_neo4j_databases.py
```

### 3. Verify Setup

```bash
# Test connections
uv run python scripts/test_database_connections.py
```

## How Data Separation Works

### Neo4j: Database Namespaces

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "tta_password_2024")
)

# Development work
with driver.session(database="tta_dev") as session:
    session.run("CREATE (c:Character {name: 'Dev Character'})")

# Staging work
with driver.session(database="tta_staging") as session:
    session.run("CREATE (c:Character {name: 'Staging Character'})")

# They're completely separate!
```

**In Neo4j Browser:**
```cypher
// Switch to dev database
:use tta_dev

// Switch to staging database
:use tta_staging
```

### Redis: Database Numbers

```python
import redis

# Development cache (DB 0)
redis_dev = redis.Redis(host='localhost', port=6379, db=0)
redis_dev.set('dev_key', 'dev_value')

# Staging cache (DB 1)
redis_staging = redis.Redis(host='localhost', port=6379, db=1)
redis_staging.set('staging_key', 'staging_value')

# Test cache (DB 2)
redis_test = redis.Redis(host='localhost', port=6379, db=2)
redis_test.set('test_key', 'test_value')
```

**In Redis Commander:**
- Visit http://localhost:8081
- Select different database numbers in the dropdown

## Environment Variables

```bash
# Single Neo4j instance
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tta_password_2024

# Use different databases
NEO4J_DEV_DATABASE=tta_dev
NEO4J_STAGING_DATABASE=tta_staging
NEO4J_TEST_DATABASE=tta_test

# Single Redis instance
REDIS_HOST=localhost
REDIS_PORT=6379

# Use different database numbers
REDIS_DEV_DB=0
REDIS_STAGING_DB=1
REDIS_TEST_DB=2
```

## Database Management

### List All Neo4j Databases

```cypher
SHOW DATABASES;
```

### Switch Database in Neo4j Browser

```cypher
:use tta_dev
:use tta_staging
:use tta_test
```

### Clear a Specific Database

```cypher
:use tta_dev
MATCH (n) DETACH DELETE n;
```

### Clear a Specific Redis Database

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.flushdb()  # Clear only this database
```

## When to Use Multiple Instances

You should still use **separate instances** for:

1. **Production** - Always isolate production completely
2. **Different Neo4j versions** - Testing upgrades
3. **Hard resource limits** - Strict memory/CPU per environment
4. **Compliance requirements** - Physical data separation mandated

For **local development**, single instance with logical separation is recommended.

## Migration from Complex Setup

### 1. Export Data from Old Setup

```bash
# Export from dev instance
docker exec tta-dev-neo4j neo4j-admin database dump neo4j --to-path=/import

# Export from staging instance
docker exec tta-staging-neo4j neo4j-admin database dump neo4j --to-path=/import
```

### 2. Import to New Setup

```bash
# Import to tta_dev database
docker exec tta-neo4j neo4j-admin database load tta_dev --from-path=/import

# Import to tta_staging database
docker exec tta-neo4j neo4j-admin database load tta_staging --from-path=/import
```

## Troubleshooting

### "Database does not exist"

Run the setup script:
```bash
uv run python scripts/setup_neo4j_databases.py
```

### Check Database Status

```cypher
SHOW DATABASES;
```

### Connection Refused

Check if containers are running:
```bash
docker-compose -f docker-compose.simple.yml ps
```

View logs:
```bash
docker-compose -f docker-compose.simple.yml logs neo4j
docker-compose -f docker-compose.simple.yml logs redis
```

## Additional Resources

- [Neo4j Multi-Database Documentation](https://neo4j.com/docs/operations-manual/current/manage-databases/)
- [Redis Database Selection](https://redis.io/commands/select/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)


---
**Logseq:** [[TTA.dev/Docs/Setup/Simplified_docker_setup]]
