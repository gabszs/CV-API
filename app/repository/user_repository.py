from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import User
from app.repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, User)

    async def patch(self, id: UUID, schema, current_user: User = None):
        return await self._repository.update(id, schema)
