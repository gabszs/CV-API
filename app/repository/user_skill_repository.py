from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicatedError
from app.models import UserSkillsAssociation
from app.repository.base_repository import BaseRepository


class UserSkillRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, UserSkillsAssociation)

    async def read_by_id(user_id: UUID, skill_id: int):
        pass

    async def create(self, schema):
        async with self.session_factory() as session:
            try:
                model = self.model(**schema.model_dump())
                session.add(model)
                await session.commit()
                await session.refresh(model)
                return model
            except IntegrityError as _:
                raise DuplicatedError(detail="Association already created")
