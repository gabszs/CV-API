from datetime import datetime
from typing import AsyncGenerator
from typing import Generator

import pytest
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import SessionTransaction

from app.core.database import get_session_factory
from app.core.settings import settings
from app.main import app
from app.models import Base
from tests.factories import batch_users_by_options
from tests.factories import UserFactory


sync_db_url = settings.TEST_DATABASE_URL.replace("+asyncpg", "")


@pytest.fixture
def factory_user() -> UserFactory:
    return UserFactory()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        yield client


@pytest.fixture(scope="session")
def setup_db() -> Generator:
    engine = create_engine(sync_db_url)
    conn = engine.connect()
    conn.execute(text("commit"))

    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    finally:
        conn.close()

    conn = engine.connect()

    conn.execute(text("commit"))
    conn.execute(text("create database test"))
    conn.close()

    yield

    conn = engine.connect()
    conn.execute(text("commit"))
    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    conn.close()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(setup_db: Generator) -> Generator:
    engine = create_engine(sync_db_url)

    with engine.begin():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        yield
        Base.metadata.drop_all(engine)

    engine.dispose()


@pytest.fixture
async def session() -> AsyncGenerator:
    async_engine = create_async_engine(settings.TEST_DATABASE_URL)
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        AsyncSessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=conn,
            future=True,
        )

        async_session = AsyncSessionLocal()

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session: Session, transaction: SessionTransaction) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                if conn.sync_connection:
                    conn.sync_connection.begin_nested()

        def test_get_session() -> Generator:
            try:
                yield AsyncSessionLocal
            except SQLAlchemyError:
                pass

        app.dependency_overrides[get_session_factory] = test_get_session

        yield async_session
        await async_session.close()
        await conn.rollback()

    await async_engine.dispose()


def validate_datetime(data_string):
    try:
        datetime.strptime(data_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        return True
    except ValueError:
        try:
            datetime.strptime(data_string, "%Y-%m-%dT%H:%M:%S")
            return True
        except ValueError:
            return False


async def setup_users_data(
    session: AsyncSession, normal_users: int = 0, admin_users: int = 0, disable_users: int = 0, disable_admins: int = 0
) -> None:
    users, clean_users = batch_users_by_options(
        normal_users=normal_users, admin_users=admin_users, disable_users=disable_users, disable_admins=disable_admins
    )
    session.add_all(users)
    await session.flush()
    await session.commit()
    return clean_users


async def token(
    client, session, base_auth_route: str = "/v1/auth", normal_users: int = 1, clean_user_index: int = 0, **kwargs
):
    if clean_user_index > normal_users or clean_user_index < 0:
        raise ValueError("The index needs to be lower than normal_users_qty or greater than 0")

    clean_users = await setup_users_data(session, normal_users=normal_users, **kwargs)
    clean_user = clean_users[clean_user_index]
    response = await client.post(
        f"{base_auth_route}/sign-in", json={"email__eq": clean_user.email, "password": clean_user.clean_password}
    )
    return clean_user, response.json()["access_token"]
