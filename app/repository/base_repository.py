from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import dict_to_sqlalchemy_filter_options
from app.core.exceptions import DuplicatedError
from app.core.exceptions import NotFoundError
from app.core.settings import Settings

settings = Settings()


class BaseRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model) -> None:
        self.session_factory = session_factory
        self.model = model

    async def read_by_options(self, schema):
        async with self.session_factory() as session:
            schema_as_dict = schema.dict(exclude_none=True)
            ordering = schema_as_dict.get("ordering", settings.ORDERING)
            order_query = (
                getattr(self.model, ordering[1:]).desc()
                if ordering.startswith("-")
                else getattr(self.model, ordering).asc()
            )
            page = schema_as_dict.get("page", settings.PAGE)
            page_size = schema_as_dict.get("page_size", settings.PAGE_SIZE)
            filter_options = dict_to_sqlalchemy_filter_options(self.model, schema.dict(exclude_none=True))
            query = await session.query(self.model)

            filtered_query = query.filter(filter_options)
            query = filtered_query.order_by(order_query)
            if page_size == "all":
                query = query.all()
            else:
                query = query.limit(page_size).offset((page - 1) * page_size).all()
            total_count = filtered_query.count()
            return {
                "founds": query,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                    "total_count": total_count,
                },
            }

    async def read_by_id(self, id: UUID):
        async with self.session_factory() as session:
            result = await session.get(self.model, id)
            if not result:
                raise NotFoundError(detail=f"id not found: {id}")
            return result

    async def create(self, schema):
        async with self.session_factory() as session:
            print(self.model, schema)
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
            await session.query(self.model).filter(self.model.id == id).update(schema.dict(exclude_none=True))
            await session.commit()
            return self.read_by_id(id)

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
