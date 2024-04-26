from contextlib import AbstractContextManager
from typing import Any
from typing import Callable
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError
from app.core.exceptions import DuplicatedError
from app.core.exceptions import NotFoundError
from app.core.settings import Settings
from app.schemas.base_schema import FindBase

settings = Settings()


class BaseRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model) -> None:
        self.session_factory = session_factory
        self.model = model

    async def read_by_options(self, schema: FindBase):
        async with self.session_factory() as session:
            query = await session.execute(select(self.model).offset(schema.offset).limit(schema.limit))
            result = query.scalars().all()
            return result

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
                raise DuplicatedError(detail=str(e.orig))
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
                raise NotFoundError(detail=f"not found id : {id}")
            await session.delete(user)
            await session.commit()
