# Health Check Best Practices

## Updated depends_on Pattern

Replace simple depends_on:
```yaml
depends_on:
  - neo4j
  - redis
```

With health check conditions:
```yaml
depends_on:
  neo4j:
    condition: service_healthy
  redis:
    condition: service_healthy
```

## Service Health Checks

### Neo4j
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:7474 || exit 1"]
  interval: 10s
  timeout: 10s
  retries: 5
  start_period: 40s
```

### Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
```

### API Services
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

## Manual Application Required
This guide must be applied manually to each compose file to ensure correctness.


---
**Logseq:** [[TTA.dev/Docker/Configs/Health-check-guide]]
