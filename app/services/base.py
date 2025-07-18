

from __future__ import annotations
import contextlib
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar
from sqlalchemy.orm import Session

T = TypeVar("T")

class UnitOfWork(contextlib.AbstractAsyncContextManager):
    """Async unit of work for database sessions."""
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None

    async def __aenter__(self) -> UnitOfWork:
        # Create a new session at the start of the context
        self.session = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        # Commit on success, rollback on exception
        if self.session is None:
            return
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()

class GenericRepository(Generic[T]):
    """Generic repository for CRUD operations on SQLAlchemy models."""
    def __init__(self, uow: UnitOfWork, model: type[T]) -> None:
        self.uow = uow
        self.model = model

    def add(self, obj: T) -> T:
        assert self.uow.session is not None, "Session is not initialized"
        self.uow.session.add(obj)
        return obj

    def get(self, id: Any) -> Optional[T]:
        assert self.uow.session is not None, "Session is not initialized"
        return self.uow.session.get(self.model, id)

    def list(self, **filters: Any) -> Sequence[T]:
        assert self.uow.session is not None, "Session is not initialized"
        query = self.uow.session.query(self.model)
        return query.filter_by(**filters).all()

    def remove(self, obj: T) -> None:
        assert self.uow.session is not None, "Session is not initialized"
        self.uow.session.delete(obj)