# MCP Servers Configuration for TTA

This directory contains comprehensive configuration for Model Context Protocol (MCP) servers that integrate with the TTA (Therapeutic Text Adventure) Docker environment.

## 🚀 Quick Start

1. **Run the automated setup script:**
   ```bash
   ./setup-mcp-servers.sh
   ```

2. **Source environment variables:**
   ```bash
   source mcp-servers.env
   ```

3. **Set up Grafana API key** (see instructions below)

## 📁 Files Overview

- **`mcp-servers.env`** - Environment variables for all MCP servers
- **`setup-mcp-servers.sh`** - Automated installation and configuration script
- **`MCP_SETUP_README.md`** - This documentation file

## 🔧 Supported MCP Servers

### 1. **Neo4j MCP Server** (`/neo4j-contrib/mcp-neo4j`)
- **Purpose**: Graph database queries and knowledge graph management
- **Connection**: `bolt://localhost:7687`
- **Credentials**: `neo4j` / `neo4j_password`
- **Installation**: `uvx mcp-neo4j-cypher@0.3.0`

### 2. **PostgreSQL MCP Server** (`/executeautomation/mcp-database-server`)
- **Purpose**: Primary database operations and SQL queries
- **Connection**: `localhost:5432`
- **Database**: `tta_db`
- **Credentials**: `tta_user` / `tta_password`
- **Installation**: `npm install -g @executeautomation/database-server`

### 3. **Grafana MCP Server** (`/grafana/mcp-grafana`)
- **Purpose**: Monitoring, visualization, and Prometheus/Loki queries
- **Connection**: `http://localhost:3000`
- **Requires**: Service account API key
- **Installation**: `go install github.com/grafana/mcp-grafana/cmd/mcp-grafana@latest`

### 4. **Redis Connection**
- **Purpose**: Session management and caching
- **Connection**: `redis://localhost:6379`
- **Authentication**: None (default setup)

## 🛠️ Manual Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.8+
- Go 1.19+ (optional, for Grafana MCP)
- Docker and Docker Compose
- TTA Docker environment running

### Install MCP Servers

```bash
# PostgreSQL MCP Server
npm install -g @executeautomation/database-server

# Python package manager for Neo4j MCP
pip3 install uv

# Grafana MCP Server (optional)
GOBIN="$HOME/go/bin" go install github.com/grafana/mcp-grafana/cmd/mcp-grafana@latest
```

### Set Up Grafana API Key

1. **Access Grafana**: http://localhost:3000
2. **Login**: admin/admin (change password when prompted)
3. **Navigate**: Administration → Service Accounts
4. **Create Service Account**:
   - Name: `mcp-server`
   - Role: `Viewer` (or higher based on needs)
5. **Generate API Key**:
   - Click on the service account
   - Add service account token
   - Copy the generated token
6. **Update Environment**:
   ```bash
   # Edit mcp-servers.env
   GRAFANA_API_KEY=your_generated_api_key_here
   ```

## 🔌 Claude Desktop Configuration

The setup script automatically generates a Claude Desktop configuration file at:
- **Linux/Mac**: `~/.config/claude-desktop/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

### Example Configuration:
```json
{
  "mcpServers": {
    "neo4j": {
      "command": "uvx",
      "args": ["mcp-neo4j-cypher@0.3.0", "--transport", "stdio"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "neo4j_password",
        "NEO4J_DATABASE": "neo4j",
        "NEO4J_NAMESPACE": "tta"
      }
    },
    "postgresql": {
      "command": "npx",
      "args": [
        "-y",
        "@executeautomation/database-server",
        "--postgresql",
        "--host", "localhost",
        "--database", "tta_db",
        "--user", "tta_user",
        "--password", "tta_password"
      ]
    },
    "grafana": {
      "command": "mcp-grafana",
      "args": [],
      "env": {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_API_KEY": "your_grafana_api_key_here"
      }
    }
  }
}
```

## 🧪 Testing Connections

### Test Database Services:
```bash
# Redis
redis-cli -h localhost -p 6379 ping

# Neo4j
docker exec tta-neo4j cypher-shell -u neo4j -p neo4j_password "RETURN 1"

# PostgreSQL
docker exec tta-postgres pg_isready -U tta_user -d tta_db

# Grafana
curl http://localhost:3000/api/health
```

### Test MCP Servers:
```bash
# PostgreSQL MCP Server
npx @executeautomation/database-server --postgresql --host localhost --database tta_db --user tta_user --password tta_password

# Neo4j MCP Server
uvx mcp-neo4j-cypher@0.3.0 --transport stdio

# Grafana MCP Server (requires API key)
mcp-grafana --debug
```

## 🐳 Docker Integration

The MCP servers connect to TTA services via Docker port forwarding:

| Service    | Container Port | Host Port | MCP Connection |
|------------|----------------|-----------|----------------|
| Redis      | 6379          | 6379      | `localhost:6379` |
| Neo4j      | 7687          | 7687      | `localhost:7687` |
| PostgreSQL | 5432          | 5432      | `localhost:5432` |
| Grafana    | 3000          | 3000      | `localhost:3000` |
| Prometheus | 9090          | 9090      | `localhost:9090` |

## 🔒 Security Considerations

- **Credentials**: All credentials are stored in `mcp-servers.env`
- **Git Ignore**: Add `mcp-servers.env` to `.gitignore`
- **API Keys**: Rotate Grafana API keys regularly
- **Network**: Services are exposed on localhost only
- **Authentication**: Use strong passwords for production

## 🔧 Troubleshooting

### Common Issues:

1. **Connection Refused**
   - Ensure TTA Docker services are running
   - Check port forwarding: `docker ps`

2. **Authentication Failed**
   - Verify credentials in `mcp-servers.env`
   - Check Docker environment variables

3. **MCP Server Not Found**
   - Ensure global npm packages are in PATH
   - Verify installation: `which mcp-grafana`

4. **Permission Denied**
   - Check Grafana service account permissions
   - Verify API key is valid

### Debug Commands:
```bash
# Check Docker services
docker-compose -f docker-compose.phase2a.yml ps

# View service logs
docker logs tta-redis
docker logs tta-neo4j
docker logs tta-postgres

# Test individual connections
redis-cli -h localhost -p 6379 info
docker exec tta-neo4j cypher-shell -u neo4j -p neo4j_password "SHOW DATABASES"
docker exec tta-postgres psql -U tta_user -d tta_db -c "SELECT version();"
```

## 📚 Additional Resources

- [Neo4j MCP Server Documentation](https://github.com/neo4j-contrib/mcp-neo4j)
- [PostgreSQL MCP Server Documentation](https://github.com/executeautomation/mcp-database-server)
- [Grafana MCP Server Documentation](https://github.com/grafana/mcp-grafana)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)

## 🤝 Support

For issues specific to:
- **TTA Integration**: Check TTA documentation
- **MCP Servers**: Refer to individual server repositories
- **Docker Environment**: Verify docker-compose configuration
