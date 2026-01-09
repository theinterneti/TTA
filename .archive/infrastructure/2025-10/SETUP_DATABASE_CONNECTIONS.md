# 🎯 QUICK FIX: Database Connections Not Showing

## The Issue

The Database Client extension (for Neo4j) requires **manual connection setup through the UI**. The configuration files we created are for reference, but you need to add connections through the VS Code interface.

## ✅ What's Working

- ✅ Extensions installed: `cweijan.dbclient-jdbc` and `cweijan.vscode-redis-client`
- ✅ Databases running: Neo4j (port 7687) and Redis (port 6379)
- ✅ Credentials verified: Both databases are accessible

## 🔧 Quick Fix (4 Steps)

### 1. Reload VS Code
```
Ctrl+Shift+P → "Developer: Reload Window"
```

### 2. Find the Database Icons

Look in your **LEFT SIDEBAR** for:
- 🗄️ = Database Client (Neo4j)
- 🔴 = Redis Client (Redis)

Can't see them? Scroll down or check Extensions (Ctrl+Shift+X) to ensure they're enabled.

### 3. Add Neo4j Connection Manually

1. Click 🗄️ icon in sidebar
2. Click "+" button in panel
3. Select "Neo4j"
4. Fill in:
   - **Host**: `localhost`
   - **Port**: `7687`
   - **Username**: `neo4j`
   - **Password**: `tta_dev_password_2024`
   - **Database**: `neo4j`
5. Save/Connect

### 4. Check Redis (Should Auto-Load)

1. Click 🔴 icon in sidebar
2. Should see "TTA Dev Redis" and "TTA Test Redis"
3. If not, add manually with:
   - **Host**: `localhost`
   - **Port**: `6379`
   - **Database**: `0`

## 🎓 Full Documentation

- **Troubleshooting Guide**: `.vscode/TROUBLESHOOTING_CONNECTIONS.md`
- **Quick Reference**: `.vscode/DATABASE_QUICK_REF.md`
- **Complete Setup**: `.vscode/dev-database-setup.md`

---

**Still stuck?** Open `.vscode/TROUBLESHOOTING_CONNECTIONS.md` for detailed troubleshooting steps.


---
**Logseq:** [[TTA.dev/.archive/Infrastructure/2025-10/Setup_database_connections]]
