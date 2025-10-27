# Gemini CLI Extensions Configuration Guide

**Date:** 2025-10-20  
**Purpose:** Configuration guide for Gemini CLI extensions with TTA credentials  
**Status:** ✅ Credentials Located, ⚠️ Partial Configuration

---

## 📋 Summary

### Credentials Located ✅
- **Location 1:** `.env` file in project root
- **Location 2:** `mcp-servers.env` file in project root
- **Services Running:** Redis (port 6380), Neo4j (port 7688)

### Extension Status
1. ✅ **code-review** (v0.1.0) - Working immediately
2. ✅ **gemini-cli-security** (v0.3.0) - Working immediately
3. ⚠️ **github** (v1.0.0) - Needs GitHub authentication (HTTP 400 error)
4. ⚠️ **mcp-neo4j** (v1.0.0) - 2/4 MCP servers failing (needs env vars)
5. ⚠️ **mcp-redis** (v0.1.0) - Needs REDIS_URL env var

---

## 🔑 Credentials Found

### Redis Configuration
**From `.env` file:**
```bash
REDIS_URL=redis://localhost:6379  # Default port
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # No password configured
REDIS_DB=0
```

**Actual Service (Docker):**
```bash
# Redis is running on port 6380 (mapped from 6379)
REDIS_URL=redis://localhost:6380
```

**Verification:**
```bash
docker ps | grep redis
# Output: tta-staging-redis Up 2 hours (healthy) 0.0.0.0:6380->6379/tcp
```

---

### Neo4j Configuration
**From `.env` file:**
```bash
NEO4J_URI=bolt://localhost:7688  # Staging Neo4j
NEO4J_URL=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=staging_neo4j_secure_pass_2024
NEO4J_DATABASE=neo4j
```

**From `mcp-servers.env` file:**
```bash
NEO4J_URI=bolt://localhost:7687  # Different port!
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4j_password  # Different password!
NEO4J_DATABASE=neo4j
NEO4J_NAMESPACE=tta
```

**Actual Service (Docker):**
```bash
# Neo4j is running on port 7688 (mapped from 7687)
NEO4J_URI=bolt://localhost:7688
NEO4J_AUTH=neo4j:staging_neo4j_secure_pass_2024
```

**Verification:**
```bash
docker ps | grep neo4j
# Output: tta-staging-neo4j Up 2 hours (healthy) 0.0.0.0:7688->7687/tcp
```

---

### GitHub Configuration
**Status:** Not configured in `.env` files

**Required:** GitHub authentication for MCP server

**Options:**
1. GitHub Copilot authentication (automatic if configured)
2. GitHub personal access token
3. GitHub App credentials

---

## ⚙️ Configuration Steps

### Step 1: Export Environment Variables

Create a script to export environment variables before running Gemini CLI:

**File:** `scripts/gemini-cli-env.sh`
```bash
#!/bin/bash
# Export environment variables for Gemini CLI extensions

# Neo4j Configuration (Staging)
export NEO4J_URI="bolt://localhost:7688"
export NEO4J_AUTH="neo4j:staging_neo4j_secure_pass_2024"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="staging_neo4j_secure_pass_2024"
export NEO4J_DATABASE="neo4j"
export NEO4J_NAMESPACE="tta"

# Redis Configuration (Staging)
export REDIS_URL="redis://localhost:6380"
export REDIS_HOST="localhost"
export REDIS_PORT="6380"
export REDIS_DB="0"

echo "✓ Environment variables exported for Gemini CLI"
echo "  NEO4J_URI=$NEO4J_URI"
echo "  REDIS_URL=$REDIS_URL"
```

**Usage:**
```bash
# Source the script before running Gemini CLI
source scripts/gemini-cli-env.sh

# Then run Gemini CLI
gemini "Your prompt here"
```

---

### Step 2: Persistent Configuration (Optional)

Add to `~/.bashrc` or `~/.zshrc` for automatic export:

```bash
# Gemini CLI Extensions - TTA Credentials
export NEO4J_URI="bolt://localhost:7688"
export NEO4J_AUTH="neo4j:staging_neo4j_secure_pass_2024"
export REDIS_URL="redis://localhost:6380"
```

**Apply changes:**
```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

### Step 3: Verify Services Running

Before using extensions, ensure services are running:

```bash
# Check Docker services
docker ps | grep -E "(redis|neo4j)"

# Expected output:
# tta-staging-redis     Up X hours (healthy)   0.0.0.0:6380->6379/tcp
# tta-staging-neo4j     Up X hours (healthy)   0.0.0.0:7688->7687/tcp

# Test Redis connection
redis-cli -h localhost -p 6380 ping
# Expected: PONG

# Test Neo4j connection
docker exec tta-staging-neo4j cypher-shell -u neo4j -p staging_neo4j_secure_pass_2024 "RETURN 1"
# Expected: 1
```

---

### Step 4: Configure GitHub Authentication

**Option A: GitHub Copilot (Recommended)**
If you have GitHub Copilot, authentication should work automatically.

**Option B: Personal Access Token**
1. Generate token at https://github.com/settings/tokens
2. Permissions needed: `repo`, `read:org`, `read:user`
3. Configure in Gemini CLI settings (if supported)

**Option C: Verify Current Auth**
```bash
# Check if GitHub CLI is authenticated
gh auth status

# If not authenticated, login
gh auth login
```

---

## 🧪 Validation Tests

### Test 1: Verify Environment Variables
```bash
# Export variables
source scripts/gemini-cli-env.sh

# Verify they're set
echo "NEO4J_URI: $NEO4J_URI"
echo "REDIS_URL: $REDIS_URL"
```

### Test 2: Test Gemini CLI Extensions
```bash
# Run with environment variables
NEO4J_URI="bolt://localhost:7688" \
NEO4J_AUTH="neo4j:staging_neo4j_secure_pass_2024" \
REDIS_URL="redis://localhost:6380" \
gemini "Test extensions: List installed extensions and their status"
```

### Test 3: Verify MCP Server Connections
```bash
# Check Gemini CLI extension status
gemini extensions list

# Expected output should show all 5 extensions enabled
```

---

## 🐛 Troubleshooting

### Issue 1: Neo4j MCP Servers Failing
**Symptoms:**
```
Error during discovery for server 'mcp-neo4j-cloud-aura-api': Connection closed
Error during discovery for server 'mcp-neo4j-memory': Connection closed
```

**Cause:** Environment variables not passed to MCP servers

**Solution:**
```bash
# Export variables before running Gemini CLI
export NEO4J_URI="bolt://localhost:7688"
export NEO4J_AUTH="neo4j:staging_neo4j_secure_pass_2024"

# Then run Gemini CLI
gemini "Your prompt"
```

---

### Issue 2: GitHub Extension HTTP 400 Error
**Symptoms:**
```
Error during discovery for server 'github': Authorization header is badly formatted
```

**Cause:** GitHub authentication not configured or invalid

**Solutions:**
1. **Check GitHub CLI auth:**
   ```bash
   gh auth status
   gh auth login  # If not authenticated
   ```

2. **Verify GitHub Copilot:**
   - Ensure GitHub Copilot is active
   - Check subscription status

3. **Temporary Workaround:**
   - Disable GitHub extension if not needed:
     ```bash
     gemini extensions disable github
     ```

---

### Issue 3: Redis Connection Refused
**Symptoms:**
```
Error connecting to Redis: Connection refused
```

**Cause:** Wrong port or service not running

**Solutions:**
1. **Verify service running:**
   ```bash
   docker ps | grep redis
   ```

2. **Use correct port:**
   ```bash
   # TTA staging Redis is on port 6380, not 6379
   export REDIS_URL="redis://localhost:6380"
   ```

3. **Start service if stopped:**
   ```bash
   docker-compose -f docker-compose.staging.yml up -d tta-staging-redis
   ```

---

## 📊 Current Status

### Working Extensions (2/5)
- ✅ **code-review** - No configuration needed
- ✅ **gemini-cli-security** - No configuration needed

### Needs Configuration (3/5)
- ⚠️ **github** - Needs GitHub authentication
- ⚠️ **mcp-neo4j** - Needs NEO4J_URI and NEO4J_AUTH env vars
- ⚠️ **mcp-redis** - Needs REDIS_URL env var

### Next Steps
1. Create `scripts/gemini-cli-env.sh` script
2. Test Gemini CLI with exported environment variables
3. Verify all 5 extensions connect successfully
4. Configure GitHub authentication (optional)
5. Document final configuration in this file

---

## 🎯 Recommended Workflow

### For Orchestration Refactoring

**Step 1: Start Services**
```bash
# Ensure Redis and Neo4j are running
docker-compose -f docker-compose.staging.yml up -d tta-staging-redis tta-staging-neo4j
```

**Step 2: Export Environment Variables**
```bash
# Source the environment script
source scripts/gemini-cli-env.sh
```

**Step 3: Use Gemini CLI**
```bash
# Now Gemini CLI has access to database schemas
gemini "
Analyze the orchestration component for refactoring opportunities.

Context:
- Current coverage: 49.4%
- Target coverage: 70%
- Focus: _import_components() method

Consider:
- Neo4j narrative graph schema
- Redis session state patterns
- Dependency injection opportunities
"
```

---

**Last Updated:** 2025-10-20  
**Status:** Credentials located, partial configuration complete  
**Next Action:** Create gemini-cli-env.sh script and test full configuration


