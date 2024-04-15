import asyncio
import sys
from asyncio import WindowsSelectorEventLoopPolicy
from contextlib import ExitStack

import pytest
import pytest_asyncio
import sqlalchemy as sa
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.database import sessionmanager
from app.core.settings import settings
from app.main import init_app
from app.models import User
from tests.factories import UserFactory


@pytest.fixture(scope="session")
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed" on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def user_factory():
    return UserFactory()


@pytest.fixture(scope="session")
def _database_url():
    return settings.TEST_DATABASE_URL


@pytest.fixture(scope="session")
def init_database():
    from app.models import Base

    return Base.metadata.create_all


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app(init_db=False)


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def db(event_loop, _database_url):
    sessionmanager.init(_database_url)
    async with sessionmanager.connect() as conn:
        await sessionmanager.drop_all(conn)
        await sessionmanager.create_all(conn)
    yield sessionmanager
    async with sessionmanager.connect() as conn:
        await sessionmanager.drop_all(conn)
    await sessionmanager.close()


@pytest_asyncio.fixture()
async def session(db):
    # async with AsyncSession(sessionmanager._engine) as session:
    #     yield session
    async with sessionmanager.session() as session:
        yield session


@pytest_asyncio.fixture()
async def user(session):
    user = UserFactory()
    session.add(user)
    await session.commit()
    result = await session.execute(sa.select(User))
    return result.scalars().all()[0]


@pytest_asyncio.fixture()
async def other_user(session):
    other_user = UserFactory()
    session.add(other_user)
    await session.commit()
    result = await session.execute(sa.select(User))
    return result.scalars().all()[1]


@pytest_asyncio.fixture()
async def all_users(session):
    result = await session.execute(sa.select(User))
    return result.scalars().all()


@pytest.fixture(scope="function")
async def session_override(app, connection_test):
    async def get_db_override():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_db] = get_db_override
