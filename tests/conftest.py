import asyncio
from contextlib import ExitStack

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from icecream import ic
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import select

from app.core.database import get_db
from app.core.database import sessionmanager
from app.main import init_app
from app.models import User
from tests.factories import UserFactory

test_db = factories.postgresql_noproc(
    user="app_user", password="app_password", host="localhost", port="5432", dbname="test_db"
)


async def show_users_in_table(session):
    all_users = await session.execute(select(User))
    print("Todos os usuários antes de adicionar:")
    for user_row in all_users:
        ic(user_row)


@pytest.fixture
def user_factory():
    return UserFactory()


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app(init_db=False)


@pytest.fixture(scope="session")
def event_loop(request):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connection_test(test_db, event_loop):
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    pg_password = test_db.password
    pg_version = test_db.version

    with DatabaseJanitor(pg_user, pg_host, pg_port, pg_db, pg_version, pg_password):
        connection_str = f"postgresql+psycopg://{pg_user}:@{pg_host}:{pg_port}/{pg_db}"
        sessionmanager.init(connection_str)
        yield
        await sessionmanager.close()


@pytest.fixture(scope="function", autouse=True)
async def create_tables(connection_test):
    async with sessionmanager.connect() as connection:
        await sessionmanager.drop_all(connection)
        await sessionmanager.create_all(connection)


@pytest_asyncio.fixture
async def session(connection_test):
    async with sessionmanager.session() as session:
        yield session


@pytest_asyncio.fixture
async def user(session):
    # await show_users_in_table(session)
    user = UserFactory()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    yield user

    await session.delete(user)
    await session.commit()


@pytest_asyncio.fixture
async def other_user(session):
    other_user = UserFactory()
    session.add(other_user)
    await session.commit()
    await session.refresh(other_user)
    yield other_user

    await session.delete(other_user)
    await session.commit()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, connection_test):
    async def get_db_override():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_db] = get_db_override
