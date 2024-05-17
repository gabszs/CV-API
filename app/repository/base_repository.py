from contextlib import AbstractContextManager
from typing import Any
from typing import Callable
from uuid import UUID

from icecream import ic
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError
from app.core.exceptions import DuplicatedError
from app.core.exceptions import NotFoundError
from app.core.settings import Settings
from app.schemas.base_schema import FindBase


settings = Settings()


class BaseRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model, public_schema) -> None:
        self.session_factory = session_factory
        self.model = model
        self.public_schema = public_schema

    # async def read_by_options(
    #     self, schema: FindBase, eager: bool = False
    # ):  # Tentar adicionaro eager_argsd e passar o moodel.users como arg
    #     async with self.session_factory() as session:
    #         order_query = (
    #             getattr(self.model, schema.ordering[1:]).desc()
    #             if schema.ordering.startswith("-")
    #             else getattr(self.model, schema.ordering).asc()
    #         )
    #         stmt = select(self.model)
    #         if eager:
    #             for eager in getattr(self.model, "eagers", []):
    #                 stmt = stmt.options(joinedload(getattr(self.model, eager)))
    #         ic(schema, eager)
    #         offset = (schema.page - 1) * int(schema.page_size)
    #         limit = int(schema.page_size)
    #         ic(offset, limit, type(limit))
    #         # page_size = int(schema.page_size)
    #         stmt = stmt.offset(offset).limit(limit)
    #         # query = await session.execute(stmt.order_by(order_query))
    #         query = await session.execute(stmt.order_by(self.model.created_at.desc()))
    #         stmt = stmt.order_by(self.model.created_at.desc())
    #         query.scalars().all()
    #         if eager:
    #             result = query.unique().scalars().all()
    #         else:
    #             result = query.scalars().all()
    #         ic(str(stmt))
    #         return result
    #         print
    #         ic(result)
    async def read_by_options(self, schema: FindBase, eager: bool = False, unique: bool = False):
        from app.schemas.skill_schema import SearchOptions
        from app.schemas.base_schema import FindModelResult

        async with self.session_factory() as session:
            order_query = (
                getattr(self.model, schema.ordering[1:]).desc()
                if schema.ordering.startswith("-")
                else getattr(self.model, schema.ordering).asc()
            )
            stmt = select(self.model)
            if eager:
                for eager_relation in getattr(self.model, "eagers", []):
                    stmt = stmt.options(joinedload(getattr(self.model, eager_relation)))

            offset = (schema.page - 1) * int(schema.page_size)
            limit = int(schema.page_size)
            stmt = stmt.order_by(order_query).offset(offset).limit(limit)

            compiled_stmt = str(stmt.compile(compile_kwargs={"literal_binds": True}))
            ic(compiled_stmt)

            query = await session.execute(stmt)
            if False:
                ic()
                result = query.unique().scalars().all()
            else:
                result = query.scalars().all()
            for skill in result:
                print(f"Skill: {skill.id}, Name: {skill.skill_name}, Category: {skill.category}")
            ic(query, type(query))
            # ic(type(result), list(result))
            return FindModelResult(
                founds=[self.public_schema(model) for model in result],
                search_options=SearchOptions(
                    ordering=schema.ordering, page=schema.page, page_size=schema.page_size, total_count=len(result)
                ),
            )
            return {
                "founds": query,
                "search_options": {
                    "page": schema.page,
                    "page_size": schema.page_size,
                    "ordering": schema.ordering,
                    "total_count": len(result),
                },
            }

    async def read_by_id(self, id: UUID):
        async with self.session_factory() as session:
            result = await session.get(self.model, id)

            if not result:
                raise NotFoundError(detail=f"id not found: {id}")
            return result

    async def read_by_email(self, email: EmailStr):
        async with self.session_factory() as session:
            stmt = select(self.model).where(self.model.email == email)
            result = await session.execute(stmt)
            user = result.scalars().all()

            return user

    # probally a bug will happpen here, correct later due to diferente models
    async def create(self, schema):
        async with self.session_factory() as session:
            query = self.model(**schema.model_dump())
            try:
                session.add(query)
                await session.commit()
                await session.refresh(query)
            except IntegrityError as e:
                if "Key (email)" in str(e.orig):
                    raise DuplicatedError(detail="Email already registered")
                if "Key (username)" in str(e.orig):
                    raise DuplicatedError(detail="Username already registered")
                raise DuplicatedError(detail=f"{self.model.__tablename__.capitalize()[:-1]} already registered")
            return query

    async def update(self, id: UUID, schema):
        async with self.session_factory() as session:
            schema = schema.model_dump()
            result = await session.get(self.model, id)

            if schema == {attr: getattr(result, attr) for attr in schema.keys()}:
                raise BadRequestError(detail="No changes detected")

            if not result:
                raise NotFoundError(detail=f"id not found: {id}")

            stmt = update(self.model).where(self.model.id == id).values(**schema)
            try:
                await session.execute(stmt)
                await session.commit()
                await session.refresh(result)
                return result
            except IntegrityError as e:
                error_message = ":".join(str(e.orig).replace("\n", " ").split(":")[1:])
                raise DuplicatedError(detail=error_message)

    async def update_attr(self, id: UUID, column: str, value: Any):
        async with self.session_factory() as session:
            result = await session.get(self.model, id)

            if not result:
                raise NotFoundError(detail=f"id not found: {id}")

            if value == getattr(result, column):
                raise BadRequestError(detail="No changes detected")

            stmt = update(self.model).where(self.model.id == id).values({column: value})
            try:
                await session.execute(stmt)
                await session.commit()
                await session.refresh(result)
                return result
            except IntegrityError as e:
                error_message = ":".join(str(e.orig).replace("\n", " ").split(":")[1:])
                raise DuplicatedError(detail=error_message)

    async def whole_update(self, id: UUID, schema):
        async with self.session_factory() as session:
            await session.query(self.model).filter(self.model.id == id).update(schema.model_dump())
            await session.commit()
            return self.read_by_id(id)

    async def delete_by_id(self, id: UUID):
        async with self.session_factory() as session:
            user = await session.get(self.model, id)
            if not user:
                raise NotFoundError(detail=f"not found id: {id}")
            await session.delete(user)
            await session.commit()
