# 🗄️ VS Code Database Integration - Setup Complete ✅

## What's Been Configured

Your TTA development workspace now has **complete integration** with VS Code's database panel for Redis and Neo4j. You can browse, query, and debug your databases directly within VS Code without switching to external tools.

## 🚀 Quick Start (3 Steps)

### 1. Start Development Databases
## Quick Start

```bash
bash docker/scripts/tta-docker.sh dev up -d
```

### 2. Test Connections
```bash
# Run the connection tester
uv run python scripts/test_database_connections.py

# Or use VS Code task: Ctrl+Shift+P → "Tasks: Run Task" → "🗄️ Database: Test Connections"
```

### 3. Access Database Panels
- **Neo4j**: Click the 🗄️ **Database** icon in the left sidebar
- **Redis**: Click the 🔴 **Redis** icon in the left sidebar

## 📁 What Was Created

### Configuration Files
```
.vscode/
├── settings.json                      # Redis + Database client config
├── database-connections.json          # Neo4j connection profiles (3 environments)
├── launch.json                        # Enhanced debug configs with DB access
├── extensions.json                    # Database extension recommendations
├── tta-database-snippets.code-snippets # 10+ Cypher query shortcuts
├── dev-database-setup.md              # Complete setup guide (full docs)
└── DATABASE_QUICK_REF.md              # One-page quick reference

Project Root:
├── .env.dev                           # Dev environment variables
├── DATABASE_SETUP_COMPLETE.md         # Getting started guide
└── scripts/test_database_connections.py # Connection diagnostics tool
```

## 🎯 Key Features

### Neo4j Graph Database
- **Visual graph browser** with node/relationship exploration
- **Cypher query editor** with syntax highlighting
- **Code snippets**: Type `tta-sessions`, `tta-world`, etc.
- **Export results** to JSON/CSV
- **3 pre-configured connections**: Dev, Test, Staging

### Redis Cache/Queue
- **Tree view** organized by namespace (session:, queue:, etc.)
- **Value inspector** for all Redis data types
- **TTL monitoring** for expiring keys
- **Pattern search** (e.g., `session:*`)
- **2 pre-configured connections**: Dev (db:0), Test (db:1)

### Debugging Integration
- **Database-aware debug configs**: Auto-connect to databases during debugging
- **Inspect state during breakpoints**: Switch to DB panels while paused
- **Auto-start services**: "Debug with Database Inspection" starts Docker services
- **Environment isolation**: Test database separation (Neo4j: test, Redis: db 1)

## 💡 Common Tasks

### View Active Game Sessions (Neo4j)
1. Open Database panel (🗄️)
2. Right-click "TTA Dev Neo4j" → New Query
3. Type: `tta-sessions` (snippet)
4. Press Enter

### Monitor Agent Message Queues (Redis)
1. Open Redis panel (🔴)
2. Expand "TTA Dev Redis"
3. Find keys: `queue:ipa`, `queue:wba`, `queue:nga`
4. Click to view queue contents

### Check Circuit Breaker States (Redis)
1. Open Redis panel
2. Search pattern: `circuit_breaker:*`
3. View keys showing: `{state: 'CLOSED'|'OPEN'|'HALF_OPEN', failures: N}`

### Debug Session State Issues
1. Set breakpoint in session-related code
2. Press F5 → "Debug with Database Inspection"
3. When paused at breakpoint:
   - Switch to Redis panel → Check `session:{id}:*` cache
   - Switch to Neo4j panel → Query `MATCH (s:GameSession) WHERE s.session_id = 'X'`
4. Compare cached vs. persistent state

## 🔧 VS Code Tasks

Press `Ctrl+Shift+P` → "Tasks: Run Task" → Select:

- **��️ Database: Test Connections** - Verify Redis + Neo4j are accessible
- **🗄️ Database: Show Quick Reference** - Display quick ref in terminal
- **🚀 Dev: Start All Services** - Start Docker Compose services
- **🛑 Dev: Stop All Services** - Stop all services
- **📊 Dev: Service Status** - Check health of running containers

## 🌐 Alternative Access (Web UIs)

If you prefer web interfaces:

```bash
# Neo4j Browser
open http://localhost:7474
# Credentials: neo4j / tta_dev_password_2024

# Redis Commander
open http://localhost:8081

# Grafana (monitoring - optional)
bash docker/scripts/tta-docker.sh dev up -d
open http://localhost:3000
```

## 🎓 Learn More

- **Full Setup Guide**: `.vscode/dev-database-setup.md`
- **Quick Reference**: `.vscode/DATABASE_QUICK_REF.md`
- **Getting Started**: `DATABASE_SETUP_COMPLETE.md`
- **Code Snippets**: `.vscode/tta-database-snippets.code-snippets`

## 🐛 Troubleshooting

### Database Panel Shows No Connections
```bash
# Ensure services are running
bash docker/scripts/tta-docker.sh dev status

# Restart VS Code window
Ctrl+Shift+P → "Developer: Reload Window"
```

### Connection Test Fails
```bash
# Check services health
bash docker/scripts/tta-docker.sh dev logs neo4j redis

# Neo4j takes 30-40s to start - wait and retry
# Redis should be instant
```

### Can't See Database Icons in Sidebar
1. Ensure extensions are installed:
   - `cweijan.dbclient-jdbc` (Neo4j)
   - `cweijan.vscode-redis-client` (Redis)
2. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
3. Check Extensions panel for installation status

## 🎉 You're All Set!

Everything is configured and ready to use. Just:

1. **Start services**: `bash docker/scripts/tta-docker.sh dev up -d`
2. **Click database icons** in VS Code sidebar
3. **Start exploring** your TTA data!

The integration works seamlessly with your existing:
- ✅ Multi-agent orchestration system
- ✅ Circuit breaker patterns
- ✅ Redis message coordination
- ✅ Neo4j graph state management
- ✅ Pytest test fixtures

Happy debugging! 🚀
