import asyncio
from contextlib import AbstractContextManager
from contextlib import asynccontextmanager
from typing import Any
from typing import Callable

from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import and_

from app.core.settings import Settings

SQLALCHEMY_QUERY_MAPPER = {
    "eq": "__eq__",
    "ne": "__ne__",
    "lt": "__lt__",
    "lte": "__le__",
    "gt": "__gt__",
    "gte": "__ge__",
}


@as_declarative()
class BaseModel:
    id: Any
    __name__: str

    @declared_attr
    def __table__(cls):
        return cls.__name__.lower()


class Database:
    def __init__(self, db_url: str = Settings().DATABASE_URL) -> None:
        self._engine = create_async_engine(db_url, echo=True, pool_pre_ping=True)
        self._session_factory = async_scoped_session(
            async_sessionmaker(bind=self._engine, autocommit=False, autoflush=False, class_=AsyncSession),
            scopefunc=asyncio.current_task,
        )

    def create_database(self) -> None:
        BaseModel.metadata.create_all(self._engine)

    def drop_all(self) -> None:
        BaseModel.metadata.drop_all(self._engine)

    def get_session(self) -> AsyncSession:
        return self._session_factory()

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session() -> Session:
    db = Database()
    async with db.session() as session:
        yield session


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
