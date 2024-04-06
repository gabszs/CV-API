import asyncio
from asyncio import WindowsSelectorEventLoopPolicy  # noqa
from contextlib import ExitStack

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pytest_postgresql import factories  # noqa
from pytest_postgresql.janitor import DatabaseJanitor  # noqa
from sqlalchemy import select  # noqa
from sqlalchemy.testing.entities import ComparableEntity  # noqa

from app.core.database import get_db
from app.core.database import sessionmanager
from app.core.settings import settings
from app.main import init_app
from app.models import User  # noqa
from tests.factories import UserFactory


@pytest.fixture(scope="session")
def event_loop(request):
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app(init_db=False)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def db(event_loop):
    sessionmanager.init(settings.TEST_DATABASE_URL)
    async with sessionmanager.connect() as conn:
        await sessionmanager.drop_all(conn)
        await sessionmanager.create_all(conn)
    yield sessionmanager
    async with sessionmanager.connect() as conn:
        await sessionmanager.drop_all(conn)
    await sessionmanager.close()


@pytest_asyncio.fixture(scope="function")
async def session(db):
    async with db.session() as session:
        yield session


@pytest_asyncio.fixture()
async def user(session):
    user = UserFactory()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def other_user(session):
    other_user = UserFactory()
    session.add(other_user)
    await session.commit()
    await session.refresh(other_user)
    return other_user


@pytest.fixture(scope="function")
async def session_override(app, connection_test):
    async def get_db_override():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_db] = get_db_override
