"""Unit of Work implementations for the full player experience (characters + sessions).
# Logseq: [[TTA.dev/Player_experience/Uow/Player_experience_uow]]

Provides:
- AbstractPlayerExperienceUnitOfWork — contract (character repo + session repo)
- PlayerExperienceUnitOfWork         — production wrapper (Neo4j + Redis)
- FakePlayerExperienceUnitOfWork     — test double (in-memory, zero DB)
"""

from __future__ import annotations

import abc

from tta_dev_primitives.persistence import AbstractUnitOfWork

from ..database.abstract_repository import (
    AbstractCharacterRepository,
    AbstractSessionRepository,
)
from ..database.character_repository import CharacterRepository
from ..database.fake_repositories import FakeCharacterRepository, FakeSessionRepository
from ..database.session_repository import SessionRepository


class AbstractPlayerExperienceUnitOfWork(AbstractUnitOfWork, abc.ABC):
    """UoW that exposes character and session repositories."""

    characters: AbstractCharacterRepository
    sessions: AbstractSessionRepository


class PlayerExperienceUnitOfWork(AbstractPlayerExperienceUnitOfWork):
    """Production UoW — wraps Neo4j CharacterRepository and Redis/Neo4j SessionRepository.

    Neo4j uses auto-commit per operation, so commit()/rollback() are no-ops unless
    explicit transaction management is wired in later.
    """

    def __init__(self, redis_client=None, neo4j_driver=None) -> None:
        self.characters = CharacterRepository()
        self.sessions = SessionRepository(redis_client, neo4j_driver)

    def commit(self) -> None:
        pass  # extend for explicit Neo4j transaction commit

    def rollback(self) -> None:
        pass  # extend for explicit Neo4j transaction rollback


class FakePlayerExperienceUnitOfWork(AbstractPlayerExperienceUnitOfWork):
    """Test double — zero DB dependencies, purely in-memory."""

    def __init__(self) -> None:
        self.characters = FakeCharacterRepository()
        self.sessions = FakeSessionRepository()
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False