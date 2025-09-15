"""
Mock Neo4j driver and session implementations.

Provides mock implementations that simulate Neo4j database operations
without requiring an actual Neo4j instance.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, AsyncIterator
from datetime import datetime

logger = logging.getLogger(__name__)


class MockRecord:
    """Mock Neo4j record."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    def __getitem__(self, key):
        return self._data.get(key)
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def data(self):
        return self._data
    
    def values(self):
        return list(self._data.values())
    
    def keys(self):
        return list(self._data.keys())


class MockResult:
    """Mock Neo4j result."""
    
    def __init__(self, records: List[Dict[str, Any]]):
        self._records = [MockRecord(record) for record in records]
        self._consumed = False
    
    async def consume(self):
        """Consume the result."""
        self._consumed = True
        return self
    
    async def single(self) -> Optional[MockRecord]:
        """Return single record."""
        if self._records:
            return self._records[0]
        return None
    
    async def data(self) -> List[Dict[str, Any]]:
        """Return all records as data."""
        return [record.data() for record in self._records]
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if not hasattr(self, '_index'):
            self._index = 0
        
        if self._index >= len(self._records):
            raise StopAsyncIteration
        
        record = self._records[self._index]
        self._index += 1
        return record


class MockAsyncSession:
    """Mock Neo4j async session."""
    
    def __init__(self, driver: 'MockNeo4jDriver'):
        self.driver = driver
        self._closed = False
        self._transaction_count = 0
    
    async def run(self, query: str, parameters: Optional[Dict[str, Any]] = None, **kwargs) -> MockResult:
        """Execute a Cypher query."""
        if self._closed:
            raise RuntimeError("Session is closed")

        # Merge parameters and kwargs
        all_params = parameters or {}
        all_params.update(kwargs)

        logger.debug(f"Mock Neo4j query: {query[:100]}... with params: {all_params}")

        # Simulate different query responses based on query content
        if "CREATE" in query.upper():
            # Create operations - return the created node with parameters
            node_id = str(uuid.uuid4())
            result_data = {
                "id": node_id,
                "created": True,
                "timestamp": datetime.utcnow().isoformat()
            }

            # If creating a user, include user data
            if "User" in query:
                result_data.update({
                    "u": {
                        "name": all_params.get("name", "unknown_user"),
                        "created_at": all_params.get("created_at", datetime.utcnow().isoformat()),
                        "id": node_id
                    }
                })

            return MockResult([result_data])
        
        elif "MATCH" in query.upper() or "RETURN" in query.upper():
            # Read operations - return sample data
            if "User" in query:
                return MockResult([
                    {
                        "name": f"test_user_{i}",
                        "created_at": datetime.utcnow().isoformat(),
                        "user_id": str(uuid.uuid4()),
                        "active": True
                    }
                    for i in range(3)
                ])
            
            elif "Story" in query:
                return MockResult([
                    {
                        "story_id": str(uuid.uuid4()),
                        "title": f"Test Story {i}",
                        "content": f"This is test story content {i}",
                        "created_at": datetime.utcnow().isoformat()
                    }
                    for i in range(2)
                ])
            
            elif "Character" in query:
                return MockResult([
                    {
                        "character_id": str(uuid.uuid4()),
                        "name": f"Test Character {i}",
                        "attributes": {"strength": 10, "intelligence": 8},
                        "created_at": datetime.utcnow().isoformat()
                    }
                    for i in range(2)
                ])
            
            else:
                # Generic response
                return MockResult([{
                    "result": "success",
                    "count": 1,
                    "timestamp": datetime.utcnow().isoformat()
                }])
        
        elif "DELETE" in query.upper():
            # Delete operations
            return MockResult([{
                "deleted": True,
                "count": 1,
                "timestamp": datetime.utcnow().isoformat()
            }])
        
        else:
            # Default response
            return MockResult([{
                "executed": True,
                "timestamp": datetime.utcnow().isoformat()
            }])
    
    async def begin_transaction(self):
        """Begin a transaction."""
        self._transaction_count += 1
        return MockTransaction(self)
    
    async def close(self):
        """Close the session."""
        self._closed = True
        logger.debug("Mock Neo4j session closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class MockTransaction:
    """Mock Neo4j transaction."""
    
    def __init__(self, session: MockAsyncSession):
        self.session = session
        self._closed = False
    
    async def run(self, query: str, parameters: Optional[Dict[str, Any]] = None, **kwargs) -> MockResult:
        """Execute query in transaction."""
        return await self.session.run(query, parameters, **kwargs)
    
    async def commit(self):
        """Commit transaction."""
        logger.debug("Mock Neo4j transaction committed")
    
    async def rollback(self):
        """Rollback transaction."""
        logger.debug("Mock Neo4j transaction rolled back")
    
    async def close(self):
        """Close transaction."""
        self._closed = True
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()


class MockNeo4jDriver:
    """Mock Neo4j driver."""
    
    def __init__(self, uri: str, auth: Optional[tuple] = None):
        self.uri = uri
        self.auth = auth
        self._closed = False
        self._session_count = 0
        
        # Simulate connection data
        self.server_info = {
            "address": "localhost:7687",
            "version": "4.4.0",
            "edition": "community"
        }
        
        logger.info(f"Mock Neo4j driver initialized for {uri}")
    
    async def verify_connectivity(self):
        """Verify driver connectivity."""
        if self._closed:
            raise RuntimeError("Driver is closed")
        
        # Simulate connectivity check
        await asyncio.sleep(0.1)  # Simulate network delay
        logger.debug("Mock Neo4j connectivity verified")
        return True
    
    def session(self, **kwargs) -> MockAsyncSession:
        """Create a new session."""
        if self._closed:
            raise RuntimeError("Driver is closed")
        
        self._session_count += 1
        return MockAsyncSession(self)
    
    async def close(self):
        """Close the driver."""
        self._closed = True
        logger.info("Mock Neo4j driver closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def create_mock_driver(uri: str, auth: Optional[tuple] = None) -> MockNeo4jDriver:
    """Create a mock Neo4j driver."""
    return MockNeo4jDriver(uri, auth)
