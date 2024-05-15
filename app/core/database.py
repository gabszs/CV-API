import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import and_

from app.core.settings import settings
from app.models import Base


SQLALCHEMY_QUERY_MAPPER = {
    "eq": "__eq__",
    "ne": "__ne__",
    "lt": "__lt__",
    "lte": "__le__",
    "gt": "__gt__",
    "gte": "__ge__",
}


# @as_declarative()
# class BaseModel:
#     id: Any
#     __name__: str

#     @declared_attr
#     def __table__(cls):
#         return cls.__name__.lower()

# BaseModel = declarative_base()


class Database:
    def __init__(self, db_url: str = settings.DATABASE_URL) -> None:
        self._engine = create_async_engine(db_url, echo=True, pool_pre_ping=True)
        self._session_factory = (
            async_sessionmaker(bind=self._engine, autocommit=False, autoflush=False, class_=AsyncSession),
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def create_database_from_base(self, base_model: declarative_base) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(base_model.metadata.create_all)

    async def drop_all_from_base(self, base_model: declarative_base) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(base_model.metadata.drop_all)

    async def get_table_names(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.reflect)
            return Base.metadata.sorted_tables, Base.metadata.tables.keys()

    def get_session(self) -> AsyncSession:
        return self._session_factory()

    @asynccontextmanager
    async def session(self):
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# async def get_db():
#     db = Database()
#     async with db.session() as session:
#         yield session


def dict_to_sqlalchemy_filter_options(model_class, search_option_dict):
    sql_alchemy_filter_options = []
    copied_dict = search_option_dict.copy()
    for key in search_option_dict:
        attr = getattr(model_class, key, None)
        if attr is None:
            continue
        option_from_dict = copied_dict.pop(key)
        if type(option_from_dict) in [int, float]:
            sql_alchemy_filter_options.append(attr == option_from_dict)
        elif type(option_from_dict) in [str]:
            sql_alchemy_filter_options.append(attr.like("%" + option_from_dict + "%"))
        elif type(option_from_dict) in [bool]:
            sql_alchemy_filter_options.append(attr.is_(option_from_dict))

    for custom_option in copied_dict:
        if "__" not in custom_option:
            continue
        key, command = custom_option.split("__")
        attr = getattr(model_class, key, None)
        if attr is None:
            continue
        option_from_dict = copied_dict[custom_option]
        if command == "in":
            sql_alchemy_filter_options.append(attr.in_([option.strip() for option in option_from_dict.split(",")]))
        elif command in SQLALCHEMY_QUERY_MAPPER.keys():
            sql_alchemy_filter_options.append(getattr(attr, SQLALCHEMY_QUERY_MAPPER[command])(option_from_dict))
        elif command == "isnull":
            bool_command = "__eq__" if option_from_dict else "__ne__"
            sql_alchemy_filter_options.append(getattr(attr, bool_command)(None))

    return and_(True, *sql_alchemy_filter_options)


# from typing import Any
# from sqlalchemy.ext.declarative import declared_attr
# from sqlalchemy.orm import as_declarative

SQLALCHEMY_QUERY_MAPPER = {
    "eq": "__eq__",
    "ne": "__ne__",
    "lt": "__lt__",
    "lte": "__le__",
    "gt": "__gt__",
    "gte": "__ge__",
}


# Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, database_url: str = settings.DATABASE_URL):
        self._engine = create_async_engine(database_url)
        self._sessionmaker = async_scoped_session(
            async_sessionmaker(autocommit=False, bind=self._engine, expire_on_commit=False),
            scopefunc=asyncio.current_task,
        )

    def session_factory(self):
        return self._sessionmaker

    def sync_create_all(self, engine):
        Base.metadata.create_all(engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Used for testing
    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.drop_all)

    async def create_all_from_base(self, connection: AsyncConnection, base_model: declarative_base):
        await connection.run_sync(base_model.metadata.create_all)

    async def drop_all_from_base(self, connection: AsyncConnection, base_model: declarative_base):
        await connection.run_sync(base_model.metadata.drop_all)


sessionmanager = DatabaseSessionManager()


async def get_db():
    async with sessionmanager.session() as session:
        yield session


async def get_session_factory():
    return sessionmanager.session_factory()
