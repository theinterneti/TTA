#!/bin/bash
# =============================================================================
# Gemini CLI Environment Variables Export Script
# =============================================================================
# Purpose: Export environment variables for Gemini CLI extensions
# Usage: source scripts/gemini-cli-env.sh
# =============================================================================

# Neo4j Configuration (Staging - Port 7688)
export NEO4J_URI="bolt://localhost:7688"
export NEO4J_AUTH="neo4j:staging_neo4j_secure_pass_2024"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="staging_neo4j_secure_pass_2024"
export NEO4J_DATABASE="neo4j"
export NEO4J_NAMESPACE="tta"

# Redis Configuration (Staging - Port 6380)
export REDIS_URL="redis://localhost:6380"
export REDIS_HOST="localhost"
export REDIS_PORT="6380"
export REDIS_DB="0"

# Confirmation
echo "✓ Gemini CLI environment variables exported"
echo ""
echo "Database Connections:"
echo "  NEO4J_URI:  $NEO4J_URI"
echo "  REDIS_URL:  $REDIS_URL"
echo ""
echo "Extensions Ready:"
echo "  ✓ code-review (no config needed)"
echo "  ✓ gemini-cli-security (no config needed)"
echo "  ⚠ github (needs GitHub auth)"
echo "  ✓ mcp-neo4j (env vars configured)"
echo "  ✓ mcp-redis (env vars configured)"
echo ""
echo "Usage: gemini \"Your prompt here\""

