from typing import AsyncGenerator
from typing import Dict
from typing import Generator
from typing import List
from uuid import UUID
from uuid import uuid4

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
from app.models.models_enums import UserRoles
from tests.factories import SkillFactory
from tests.factories import UserFactory
from tests.factories import UserSkillFactory
from tests.helpers import add_users_models
from tests.helpers import setup_skill_data
from tests.helpers import setup_user_skill_data
from tests.helpers import token
from tests.schemas import TestSkillSchema
from tests.schemas import UserModelSetup
from tests.schemas import UserSchemaWithHashedPassword
from tests.schemas import UserSkillTest

sync_db_url = settings.TEST_DATABASE_URL.replace("+asyncpg", "")


@pytest.fixture
def random_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def batch_setup_users() -> List[UserModelSetup]:
    setup_list: List[UserModelSetup] = []
    for role in UserRoles:
        setup_list.append(UserModelSetup(is_active=True, role=role))
        setup_list.append(UserModelSetup(is_active=False, role=role))
    return setup_list


@pytest.fixture
def default_search_options() -> str:
    return {"ordering": "id", "page": 1, "page_size": "all"}


@pytest.fixture
def default_created_search_options() -> str:
    return {"ordering": "created_at", "page": 1, "page_size": "all"}


@pytest.fixture
def default_username_search_options() -> str:
    return {"ordering": "username", "page": 1, "page_size": "all"}


@pytest.fixture
def factory_user() -> UserFactory:
    return UserFactory()


@pytest.fixture
def factory_user_skill() -> UserSkillFactory:
    return UserSkillFactory()


@pytest.fixture
def factory_skill() -> SkillFactory:
    return SkillFactory()


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


@pytest.fixture()
async def normal_user_token(client: AsyncClient, session: AsyncSession) -> Dict[str, str]:
    return await token(client, session)


@pytest.fixture()
async def moderator_user_token(client: AsyncClient, session: AsyncSession) -> Dict[str, str]:
    return await token(client, session, user_role=UserRoles.MODERATOR)


@pytest.fixture()
async def admin_user_token(client: AsyncClient, session: AsyncSession) -> Dict[str, str]:
    return await token(client, session, user_role=UserRoles.ADMIN)


@pytest.fixture()
async def disable_normal_user_token(client: AsyncClient, session: AsyncSession) -> Dict[str, str]:
    return await token(client, session, user_role=UserRoles.MODERATOR, is_active=False)


@pytest.fixture()
async def normal_user(session: AsyncSession) -> UserSchemaWithHashedPassword:
    return await add_users_models(session, index=0)


@pytest.fixture()
async def moderator_user(session: AsyncSession) -> UserSchemaWithHashedPassword:
    return await add_users_models(session, index=0, user_role=UserRoles.MODERATOR)


@pytest.fixture()
async def admin_user(session: AsyncSession) -> UserSchemaWithHashedPassword:
    return await add_users_models(session, index=0, user_role=UserRoles.ADMIN)


@pytest.fixture()
async def disable_normal_user(session: AsyncSession) -> UserSchemaWithHashedPassword:
    return await add_users_models(session, index=0, user_role=UserRoles.BASE_USER, is_active=False)


@pytest.fixture()
async def skill(session: AsyncSession) -> TestSkillSchema:
    return await setup_skill_data(session, index=0)


@pytest.fixture()
async def another_skill(session: AsyncSession) -> TestSkillSchema:
    return await setup_skill_data(session, index=0)


@pytest.fixture()
async def user_skill_assoc(session: AsyncSession) -> UserSkillTest:
    return await setup_user_skill_data(session, model_args=[UserModelSetup()], index=0)


@pytest.fixture()
async def batch_user_skill_assoc(session: AsyncSession, batch_setup_users) -> UserSkillTest:
    return await setup_user_skill_data(session, model_args=batch_setup_users)
