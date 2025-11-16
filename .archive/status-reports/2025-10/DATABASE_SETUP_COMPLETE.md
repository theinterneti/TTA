# 🗄️ VS Code Database Integration Setup - Complete

## ✅ What's Been Configured

I've set up a complete VS Code database integration for your TTA development workflow. Here's everything that's been added:

### 📁 Configuration Files Created/Updated

1. **`.vscode/settings.json`** - Added database client configurations
   - Redis connection profiles (dev and test databases)
   - Database client settings for Neo4j
   - File associations for Cypher query files

2. **`.vscode/database-connections.json`** - Neo4j connection profiles
   - TTA Dev Neo4j (main database)
   - TTA Test Neo4j (test isolation)
   - TTA Staging Neo4j (staging environment)

3. **`.vscode/launch.json`** - Enhanced debug configurations
   - "Debug Integration Tests (with Databases)" - Run tests with DB access
   - "Debug TTA Orchestrator" - Debug main application with DB connections
   - "Debug with Database Inspection" - Auto-starts services before debugging

4. **`.vscode/extensions.json`** - Updated recommendations
   - Added `cweijan.dbclient-jdbc` for Neo4j
   - Already includes `cweijan.vscode-redis-client` for Redis

5. **`.vscode/tta-database-snippets.code-snippets`** - Cypher query snippets
   - 10+ ready-to-use queries for common TTA operations
   - Type prefixes like `tta-sessions`, `tta-world`, `tta-journey`

6. **`.env.dev`** - Development environment variables
   - Safe default values for local Docker Compose setup
   - Neo4j and Redis connection strings

### 📚 Documentation Created

1. **`.vscode/dev-database-setup.md`** - Complete setup guide
   - How to use database panels in VS Code
   - Common development tasks
   - Troubleshooting guide

2. **`.vscode/DATABASE_QUICK_REF.md`** - Quick reference card
   - One-page cheat sheet
   - Common queries and tasks
   - Keyboard shortcuts and tips

3. **`scripts/test_database_connections.py`** - Connection tester
   - Verifies Redis and Neo4j connectivity
   - Shows database statistics and health info
   - Run with: `uv run python scripts/test_database_connections.py`

## 🚀 How to Use

### 1. Start Development Databases

```bash
# From project root
docker-compose -f docker-compose.dev.yml up -d

# Wait ~30 seconds for Neo4j to fully start
# Check status
docker-compose -f docker-compose.dev.yml ps
```

### 2. Access Database Panels in VS Code

#### **Neo4j (Graph Database)**
1. Click the **Database** icon (🗄️) in the left sidebar
2. Your connections will appear automatically:
   - **TTA Dev Neo4j**
   - **TTA Test Neo4j**
   - **TTA Staging Neo4j**
3. Click any connection to expand and browse
4. Right-click nodes/tables to run queries
5. Use code snippets: Type `tta-` in query editor for suggestions

#### **Redis (Cache/Queue)**
1. Click the **Redis** icon (🔴) in the left sidebar
2. Your connections will appear:
   - **TTA Dev Redis** (db:0)
   - **TTA Test Redis** (db:1)
3. Browse keys by namespace in tree view
4. Click any key to inspect/edit value
5. Use pattern search: `session:*`, `queue:*`, etc.

### 3. Test Connections

```bash
# Run the connection tester
uv run python scripts/test_database_connections.py

# You should see:
# ✅ Redis: OK
# ✅ Neo4j: OK
```

### 4. Debug with Database Access

1. Set breakpoints in your code
2. Press **F5** or click "Run and Debug"
3. Select **"Debug with Database Inspection"**
4. Services auto-start if not running
5. While debugging:
   - Switch to Database/Redis panels
   - Run queries to inspect state
   - View real-time data

## 🎯 Key Features

### 1. **Integrated Query Editor**
- Write and execute Cypher queries directly in VS Code
- Syntax highlighting for `.cypher` files
- Results displayed in formatted tables
- Export to JSON/CSV

### 2. **Visual Graph Browser**
- Click nodes to see relationships
- Drag to explore graph structure
- Filter by labels and properties
- Zoom and pan the graph view

### 3. **Redis Key Browser**
- Tree view organized by namespace
- Value inspection for all data types (string, hash, list, set, zset)
- TTL monitoring
- Pattern-based search
- Direct editing of values

### 4. **Code Snippets**
Type these prefixes in Cypher query editor:
- `tta-sessions` → View active game sessions
- `tta-world` → Explore world structure
- `tta-journey` → Player interaction history
- `tta-characters` → Character relationships
- `tta-stats` → Database statistics
- `tta-recent` → Recent activity

### 5. **Debugging Integration**
- Database-aware debug configurations
- Environment variables auto-configured
- Service health checks before tests
- Separate test databases (Neo4j: `test`, Redis: db 1)

## 🔧 Database Connection Details

### Neo4j
```
Bolt URI:  bolt://localhost:7687
HTTP URI:  http://localhost:7474
Username:  neo4j
Password:  tta_dev_password_2024
Databases: neo4j (dev), test, staging
```

### Redis
```
Host:      localhost
Port:      6379
Password:  (none for dev)
Databases: 0 (dev), 1 (test)
```

## 📊 VS Code Extensions Used

Your workspace already has these extensions installed:

1. **Database Client JDBC** (`cweijan.dbclient-jdbc`)
   - Neo4j support
   - Visual query builder
   - ER diagrams
   - Data export

2. **Redis Client** (`cweijan.vscode-redis-client`)
   - Key browser with tree view
   - Value editor for all types
   - CLI terminal
   - Pub/Sub monitor

3. **Neo4j VS Code** (`neo4j.neo4j-vscode`) - Optional alternative
   - Official Neo4j extension
   - Graph visualization
   - Cypher language support

## 🎨 AI Development Workflow Integration

### Circuit Breaker Monitoring (Redis)
```bash
# Pattern: circuit_breaker:*
# Each key shows: {state: 'CLOSED'|'OPEN'|'HALF_OPEN', failures: N}
```

### Agent Message Queues (Redis)
```bash
# View queues in Redis panel:
queue:ipa  # Input Processing Agent
queue:wba  # World Building Agent
queue:nga  # Narrative Generation Agent
result:*   # Agent responses
```

### Session Context (Distributed)
- **Fast cache**: Redis `session:{session_id}:*`
- **Persistent state**: Neo4j `(Player)-[:IN_SESSION]->(GameSession)`
- **Best practice**: Check both when debugging

### Example Debugging Workflow
1. User reports issue with session X
2. Open Redis panel → Search `session:X:*`
3. Check cached state
4. Open Neo4j panel → Run query:
   ```cypher
   MATCH (s:GameSession {session_id: 'X'})
   RETURN s
   ```
5. Compare cached vs. persistent state
6. Identify discrepancy

## 🌐 Alternative Access Methods

While VS Code panels are recommended, you can also use:

```bash
# Neo4j Browser (web UI)
open http://localhost:7474

# Redis Commander (web UI)
open http://localhost:8081

# Grafana (monitoring)
docker-compose -f docker-compose.dev.yml --profile monitoring up -d
open http://localhost:3000
```

## 🐛 Troubleshooting

### Database Panel Shows No Connections
1. Ensure services are running:
   ```bash
   docker-compose -f docker-compose.dev.yml ps
   ```
2. Refresh Database Client: Right-click panel → Refresh
3. Check `.vscode/database-connections.json` exists

### Redis Connection Fails
1. Test connection:
   ```bash
   docker exec tta-dev-redis redis-cli ping
   # Should return: PONG
   ```
2. Check port not in use: `lsof -i :6379`
3. View logs: `docker-compose -f docker-compose.dev.yml logs redis`

### Neo4j Connection Timeout
1. Neo4j takes 30-40 seconds to start fully
2. Check health:
   ```bash
   docker exec tta-dev-neo4j neo4j status
   ```
3. View startup logs:
   ```bash
   docker-compose -f docker-compose.dev.yml logs neo4j
   ```
4. Verify ports: `nc -zv localhost 7687`

### Extension Not Working
1. Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"
2. Check extension installed: View → Extensions → Search "database"
3. Update extension: Extensions panel → Update button

## 📝 Next Steps

### Recommended Workflow
1. **Start services**: `docker-compose -f docker-compose.dev.yml up -d`
2. **Test connections**: `uv run python scripts/test_database_connections.py`
3. **Open database panels**: Click 🗄️ and 🔴 icons in sidebar
4. **Try a query**: Use `tta-sessions` snippet in Neo4j
5. **Inspect cache**: Browse `session:*` keys in Redis
6. **Debug with databases**: Use "Debug with Database Inspection" config

### Explore Further
- Read full guide: `.vscode/dev-database-setup.md`
- Check quick ref: `.vscode/DATABASE_QUICK_REF.md`
- Browse snippets: `.vscode/tta-database-snippets.code-snippets`
- Review tasks: `Ctrl+Shift+P` → "Tasks: Run Task"

## 🎓 Learning Resources

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Redis Commands Reference](https://redis.io/commands/)
- [Database Client Extension Docs](https://database-client.com/)
- [VS Code Debugging Guide](https://code.visualstudio.com/docs/editor/debugging)

## 💡 Pro Tips

1. **Bookmark Common Queries**: Save frequently-used Cypher queries as `.cypher` files
2. **Use Namespaces**: Organize Redis keys with prefixes (`session:`, `queue:`, `cache:`)
3. **Test Isolation**: Always use separate databases for testing (Redis db:1, Neo4j test)
4. **Monitor Performance**: Watch query execution times in database panel
5. **Export Data**: Use export feature for debugging complex issues
6. **Graph Visualization**: Use Neo4j's graph view for relationship debugging

---

**Everything is configured and ready to use! 🎉**

Try it now:
1. Run `docker-compose -f docker-compose.dev.yml up -d`
2. Click the database icons in VS Code sidebar
3. Start exploring your TTA data!
