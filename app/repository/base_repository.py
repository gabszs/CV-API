from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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

    async def create(self, schema):
        async with self.session_factory() as session:
            query = self.model(**schema.dict())
            try:
                session.add(query)
                await session.commit()
                await session.refresh(query)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            return query

    async def update(self, id: UUID, schema):
        async with self.session_factory() as session:
            result = await session.get(self.model, id)
            if not result:
                raise NotFoundError(detail=f"id not found: {id}")

            stmt = update(self.model).where(self.model.id == id).values(**schema.model_dump())
            print(f"stmt: {stmt}")
            try:
                await session.execute(stmt)

            except IntegrityError as e:
                error_message = ":".join(str(e.orig).replace("\n", " ").split(":")[1:])
                raise DuplicatedError(detail=error_message)

            return result

    async def update_attr(self, id: UUID, column: str, value):
        async with self.session_factory() as session:
            await session.query(self.model).filter(self.model.id == id).update({column: value})
            await session.commit()
            return self.read_by_id(id)

    async def whole_update(self, id: UUID, schema):
        async with self.session_factory() as session:
            await session.query(self.model).filter(self.model.id == id).update(schema.dict())
            await session.commit()
            return self.read_by_id(id)

    async def delete_by_id(self, id: UUID):
        async with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.id == id).first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            await session.delete(query)
            await session.commit()
