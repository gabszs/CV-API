from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicatedError
from app.core.exceptions import NotFoundError
from app.models import Skill
from app.models import User
from app.models import UserSkillsAssociation
from app.repository.base_repository import BaseRepository
from app.schemas.base_schema import FindBase
from app.schemas.user_skills_schema import FindSkillsByUser


class UserSkillRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, UserSkillsAssociation)

    async def read_by_id(user_id: UUID, skill_id: int):
        pass

    async def create(self, schema):
        async with self.session_factory() as session:
            try:
                user = await session.get(User, schema.user_id)
                skill = await session.get(Skill, schema.skill_id)

                if not user:
                    raise NotFoundError("User not found")
                if not skill:
                    raise NotFoundError("Skill not found")
                user_skill_association = self.model(user=user, skill=skill, **schema.model_dump())
                session.add(user_skill_association)
                await session.commit()
                await session.refresh(user_skill_association)
                return user_skill_association
            except IntegrityError as _:
                raise DuplicatedError(detail="Association already created")

    async def read_skills_by_user_id(self, user_id: UUID, find_query: FindBase) -> FindSkillsByUser:
        async with self.session_factory() as session:
            stmt = select(User).where(User.id == user_id).options(selectinload(User.skills))
            if find_query.page_size != "all":
                stmt = stmt.offset((find_query.page - 1) * (find_query.page_size)).limit(int(find_query.page_size))

            result = await session.execute(stmt)
            user = result.scalar_one()

            return {
                "user_id": user_id,
                "founds": user.skills,
                "search_options": {
                    "page": find_query.page,
                    "page_size": find_query.page_size,
                    "ordering": find_query.ordering,
                    "total_count": len(user.skills),
                },
            }
