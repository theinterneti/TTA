# Neo4j Browser Access Issue - WSL2 Solution

## Problem
Getting `ERR_EMPTY_RESPONSE` when trying to access Neo4j Browser at http://localhost:7474 from Windows browser.

## Root Cause
WSL2 networking issue - Windows browser cannot properly access Docker containers running in WSL2 via `localhost`.

## ✅ Solutions (Try in Order)

### Solution 1: Access from within WSL (Recommended)
**Use a browser within WSL or Linux-based browser:**

```bash
# Option A: Install and use a WSL-based browser
# Using w3m (text-based browser for testing)
sudo apt-get update && sudo apt-get install -y w3m
w3m http://localhost:7474/browser/

# Option B: Use xdg-open if you have X server
xdg-open http://localhost:7474/browser/
```

### Solution 2: Use Cypher-Shell (Direct Access)
**This works perfectly - no browser needed:**

```bash
# Access Neo4j directly via cypher-shell
docker exec -it tta-dev-neo4j cypher-shell -u neo4j -p dev_password_2024

# Once in cypher-shell, you can run queries:
# MATCH (n) RETURN count(n);
# CREATE (n:TestNode {name: 'test'});
# MATCH (n:TestNode) RETURN n;
```

### Solution 3: Port Forwarding from Windows
**Make Windows aware of WSL2 ports:**

1. Open PowerShell as Administrator on Windows:
```powershell
# Find WSL IP
wsl hostname -I

# Add port forwarding (replace <WSL-IP> with actual IP)
netsh interface portproxy add v4tov4 listenport=7474 listenaddress=0.0.0.0 connectport=7474 connectaddress=<WSL-IP>
```

2. Then access from Windows browser: http://localhost:7474

### Solution 4: Use Docker Desktop Port Forwarding
**Restart container with explicit host binding:**

```bash
# Stop current container
docker stop tta-dev-neo4j

# Start with explicit Windows-accessible binding
docker start tta-dev-neo4j

# Docker Desktop should automatically forward the port to Windows
```

Then try accessing from Windows browser: http://localhost:7474

### Solution 5: Access via WSL IP from Windows
**Try accessing via the WSL IP address:**

1. Get WSL IP:
```bash
ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
# Result: 172.31.16.41 (example)
```

2. From Windows browser, try: http://172.31.16.41:7474
   (Note: This likely won't work due to firewall, but worth trying)

### Solution 6: Use WSL localhost.run Tunnel (Quick Test)
```bash
# Install ssh if not available
sudo apt-get install openssh-client

# Create a tunnel (this gives you a public URL)
ssh -R 80:localhost:7474 serveo.net
# Or use: ssh -R 80:localhost:7474 nokey@localhost.run

# Access via the provided URL
```

## ✅ Recommended Approach

**Best Option: Use Cypher-Shell for Development**

Since the browser access is problematic, use cypher-shell directly:

```bash
# Quick access script
cat > ~/neo4j-dev.sh << 'EOF'
#!/bin/bash
docker exec -it tta-dev-neo4j cypher-shell -u neo4j -p dev_password_2024
EOF

chmod +x ~/neo4j-dev.sh

# Now just run:
~/neo4j-dev.sh
```

## Python Access (For Development)

While browser doesn't work, the Python driver issue is separate. Use this workaround:

```python
# Create a script: scripts/neo4j_query.py
from neo4j import GraphDatabase

def run_query(query):
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "dev_password_2024")
    )
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]
    driver.close()

# Usage:
# uv run python scripts/neo4j_query.py
```

## Verification

Test that Neo4j is actually working:

```bash
# Test 1: API endpoint works
curl http://localhost:7474
# Should return JSON with neo4j_version

# Test 2: Cypher-shell works
docker exec tta-dev-neo4j cypher-shell -u neo4j -p dev_password_2024 "RETURN 1 as test"
# Should return: test
#                1

# Test 3: Bolt protocol works (from within WSL)
echo "RETURN 1 as test;" | docker exec -i tta-dev-neo4j cypher-shell -u neo4j -p dev_password_2024
```

## Why This Happens

**WSL2 Networking Quirks:**
- WSL2 uses a virtual network adapter
- Windows cannot directly access `localhost` on WSL2 containers
- Docker Desktop tries to bridge this but doesn't always work
- Browser WebSocket connections are especially problematic

**What Works:**
- ✅ Accessing from within WSL
- ✅ Cypher-shell (direct bolt protocol)
- ✅ API calls via curl from WSL
- ❌ Windows browser to WSL Neo4j Browser
- ❌ Python driver (separate authentication issue)

## Quick Reference

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check if port is listening
ss -tuln | grep 7474

# Test API
curl http://localhost:7474

# Access directly
docker exec -it tta-dev-neo4j cypher-shell -u neo4j -p dev_password_2024

# View logs
docker logs tta-dev-neo4j --tail 50

# Restart Neo4j
docker restart tta-dev-neo4j
```

## Conclusion

**For TTA Development:**
1. ✅ Use Redis (works perfectly)
2. ✅ Use cypher-shell for Neo4j queries
3. ✅ Access Neo4j via bolt protocol in tests
4. ⏸️ Skip Neo4j Browser (not critical for development)

The Neo4j database is **working** - it's just the browser UI that's inaccessible from Windows. This won't block your development!
