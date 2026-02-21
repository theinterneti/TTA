# 🔧 Neo4j Connection Fix - Manual Steps Required

**Issue**: Neo4j password authentication is not working properly via bolt driver, even though the password is set correctly in the environment.

**Root Cause**: There appears to be an incompatibility between how Neo4j's `NEO4J_AUTH` environment variable sets the password vs. how the bolt driver authenticates. This is affecting both VS Code extensions and Python drivers.

## ✅ Immediate Workaround - Browser Access

Neo4j IS running and accessible via the browser:

1. Open: **http://localhost:7474**
2. Since auth is currently disabled (`NEO4J_AUTH=none`), you should be able to connect without credentials
3. Once connected, you can set a password manually

## 🔨 Recommended Fix: Use Browser to Set Password

### Step 1: Access Neo4j Browser
```bash
# Open in your browser
open http://localhost:7474   # or manually go to http://localhost:7474
```

### Step 2: Connect (No Auth Required Currently)
- Click "Connect"
- No username/password needed since `NEO4J_AUTH=none`

### Step 3: Set Password via Cypher
In the Neo4j browser query box, run:
```cypher
ALTER USER neo4j SET PASSWORD 'tta_dev_password_2024'
```

### Step 4: Re-enable Authentication
Edit `docker-compose.dev.yml` and change:
```yaml
- NEO4J_AUTH=none
```
to:
```yaml
- NEO4J_AUTH=neo4j/tta_dev_password_2024
```

### Step 5: Restart Neo4j
```bash
cd /home/thein/recovered-tta-storytelling
docker compose -f docker-compose.dev.yml restart neo4j
```

###Step 6: Test in VS Code
- Refresh your VS Code database connections
- Try connecting to "TTA Dev Neo4j"
- Should work now!

## 📋 VS Code Connection Settings

Your `.vscode/database-connections.json` should have:
```json
{
  "name": "TTA Dev Neo4j",
  "type": "neo4j",
  "host": "127.0.0.1",
  "port": 7687,
  "user": "neo4j",
  "password": "tta_dev_password_2024",
  "database": "neo4j",
  "useSSL": false
}
```

## 🐛 Alternative: Use Cypher-Shell (If Browser Doesn't Work)

```bash
# Connect to Neo4j container
docker exec -it tta-dev-neo4j cypher-shell

# When prompted:
# username: (press Enter - no auth)
# password: (press Enter - no auth)

# Then run:
ALTER USER neo4j SET PASSWORD 'tta_dev_password_2024';
```

## ❓ Why This Happened

The Neo4j bolt authentication has been problematic with the environment variable approach. The manual password setting via Cypher ensures the password is properly stored in Neo4j's internal auth system in a way that the bolt driver can authenticate against.

## 📞 Next Steps if Still Not Working

1. Check Neo4j logs: `docker logs tta-dev-neo4j`
2. Verify port accessibility: `telnet localhost 7687`
3. Try connecting via browser first to confirm Neo4j is working
4. Check VS Code extension output panel for detailed errors

---

**Current Status**: Neo4j is running with `NEO4J_AUTH=none`. Follow the steps above to set the password properly.


---
**Logseq:** [[TTA.dev/.archive/Database/2025-10/Neo4j_fix_instructions]]
