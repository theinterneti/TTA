"""
In-memory fakes for service-layer testing without real databases.

These fakes replace Neo4j and Redis backed repositories with plain Python
collections so that domain logic can be validated quickly and deterministically.
"""

from .fake_repository import FakeRepository
from .fake_unit_of_work import FakeUnitOfWork

__all__ = ["FakeRepository", "FakeUnitOfWork"]
