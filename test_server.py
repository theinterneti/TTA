#!/usr/bin/env python3
"""
Simple test server to verify TTA development environment setup.
"""

import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="TTA Development Environment Test Server",
    description="Simple test server to verify all components are working",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for database connections
redis_client = None
neo4j_driver = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup."""
    global redis_client, neo4j_driver
    
    try:
        # Initialize Redis connection
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_password = os.getenv("REDIS_PASSWORD", "")
        
        if redis_password:
            redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        else:
            redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # Test Redis connection
        redis_client.ping()
        print("✅ Redis connection successful")
        
        # Initialize Neo4j connection
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "tta-storytelling-2025")
        
        neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        
        # Test Neo4j connection
        with neo4j_driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"✅ Neo4j connection successful: {record['message']}")
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "TTA Interactive Storytelling Platform - Development Environment",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "test_redis": "/test/redis",
            "test_neo4j": "/test/neo4j",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {}
    }
    
    # Check Redis
    try:
        if redis_client:
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_connected"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Neo4j
    try:
        if neo4j_driver:
            with neo4j_driver.session() as session:
                session.run("RETURN 1")
            health_status["services"]["neo4j"] = "healthy"
        else:
            health_status["services"]["neo4j"] = "not_connected"
    except Exception as e:
        health_status["services"]["neo4j"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
