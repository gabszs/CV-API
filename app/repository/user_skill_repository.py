from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicatedError
from app.core.exceptions import NotFoundError
from app.models import Skill
from app.models import User
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
                user = await session.get(User, schema.users_id)
                skill = await session.get(Skill, schema.skill_id)

                if not user:
                    raise NotFoundError("User not found")
                if not skill:
                    raise NotFoundError("Skill not found")

                user_skill_association = self.model(user=user, skill=skill, **schema.model_dump())
                session.add(user_skill_association)
                user.skills.append(user_skill_association)
                skill.users.append(user_skill_association)
                await session.commit()
                await session.refresh(user_skill_association)
                return user_skill_association
            except IntegrityError as _:
                raise DuplicatedError(detail="Association already created")

    from app.schemas.base_schema import AttrSearchOptions

    async def read_skills_by_user_id(self, user_id: UUID, find_query: AttrSearchOptions):
        from sqlalchemy.orm import load_only
        from sqlalchemy import select
        from app.models import UserSkillsAssociation

        async with self.session_factory() as session:
            options = [load_only(Skill.id, Skill.skill_name, Skill.category)]

            order_query = await self.get_order_by(find_query)

            stmt = (
                select(self.model)
                .where(User.id == user_id)
                .join_from(self.model, UserSkillsAssociation)
                .join_from(UserSkillsAssociation, User)
                .options(*options)
                .order_by(order_query)
            )

            if find_query.page_size != "all":
                stmt = stmt.offset((find_query.page - 1) * (find_query.page_size)).limit(int(find_query.page_size))

            result = await session.scalars(stmt)
            # return result.unique().all()
            return result

            # order_query = (
            #     getattr(self.model, schema.ordering[1:]).desc()
            #     if schema.ordering.startswith("-")
            #     else getattr(self.model, schema.ordering).asc()
            # )
            # stmt = select(self.model).order_by(order_query)
            # if eager:
            #     for eager_relation in getattr(self.model, "eagers", []):
            #         stmt = stmt.options(joinedload(getattr(self.model, eager_relation)))
            # if schema.page_size != "all":
            #     stmt = stmt.offset((schema.page - 1) * (schema.page_size)).limit(int(schema.page_size))
