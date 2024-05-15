from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.models import Skill
from app.repository.base_repository import BaseRepository


class SkillRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Skill)

    # async def read_by_options(self, schema: FindBase):
    #     async with self.session_factory() as session:
    #         query = select(self.model).options(joinedload(self.model.users)).offset(schema.offset).limit(schema.limit)
    #         result = await session.execute(query.order_by(self.model.id))  # .order_by(self.model.created_at)
    #         skills = result.unique().scalars().all()
    #         return skills

    # async def read_by_id()
