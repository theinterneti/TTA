"""Abstract Unit of Work base class for transactional boundaries.

Provides :class:`AbstractUnitOfWork` — the interface that all UoW
implementations must satisfy.  Defined locally; the ``ttadev.primitives``
package does not expose a UoW abstraction.
"""

from __future__ import annotations

import abc


class AbstractUnitOfWork(abc.ABC):
    """Abstract base class for the Unit of Work pattern.

    Concrete subclasses must implement :meth:`commit` and :meth:`rollback`.
    The default :meth:`__enter__` / :meth:`__exit__` context manager wires
    ``rollback`` on exception, which subclasses may override.
    """

    @abc.abstractmethod
    def commit(self) -> None:
        """Persist all changes made within this unit of work."""
        ...

    @abc.abstractmethod
    def rollback(self) -> None:
        """Discard all changes made within this unit of work."""
        ...

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
