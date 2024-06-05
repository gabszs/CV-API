from typing import AsyncGenerator
from typing import Generator
from typing import List

import pytest
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker
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
from tests.helpers import token
from tests.schemas import UserModelSetup

sync_db_url = settings.TEST_DATABASE_URL.replace("+asyncpg", "")


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
def default_uuid_search_options() -> str:
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


# async def setup_users_data(
#     session: AsyncSession, normal_users: int = 0, admin_users: int = 0, disable_users: int = 0, disable_admins: int = 0
# ) -> List[UserWithCleanPassword]:
#     users, clean_users = batch_users_by_options(
#         normal_users=normal_users, admin_users=admin_users, disable_users=disable_users, disable_admins=disable_admins
#     )
#     session.add_all(users)
#     await session.flush()
#     await session.commit()
#     for user in users:
#         await session.refresh(user)
#     return clean_users


# async def setup_skill_data(session: AsyncSession, qty_size: int = 1) -> List[BaseSkill]:
#     skills: List[Skill] = SkillFactory.create_batch(qty_size)
#     clean_skills: List[BaseSkill] = [
#         BaseSkill(skill_name=skill.skill_name, category=skill.category.value) for skill in skills
#     ]
#     session.add_all(skills)
#     await session.flush()
#     await session.commit()
#     for skill in skills:
#         await session.refresh(skill)
#     return clean_skills


#     if clean_user_index > normal_users or clean_user_index < 0:
#         raise ValueError("The index needs to be lower than normal_users_qty or greater than 0")

#     clean_users = await setup_users_data(session, normal_users=normal_users, **kwargs)
#     clean_user = clean_users[clean_user_index]
#     response = await client.post(
#         f"{base_auth_route}/sign-in", json={"email__eq": clean_user.email, "password": clean_user.clean_password}
#     )
#     return clean_user, response.json()["access_token"]


# async def get_admin_token_header(client, session) -> str:
#     _, auth_token = await token(client, session, normal_users=0, admin_users=1)
#     return {"Authorization": f"Bearer {auth_token}"}


# async def get_normal_token_header(client, session) -> str:
#     _, auth_token = await token(client, session, normal_users=1)
#     return {"Authorization": f"Bearer {auth_token}"}


# async def get_disable_token_header(client, session) -> str:
#     _, auth_token = await token(client, session, normal_users=0, disable_users=1)
#     return {"Authorization": f"Bearer {auth_token}"}


# @pytest.fixture()
# async def disable_user_token(client, session):
#     return await get_disable_token_header(client, session)


@pytest.fixture()
async def normal_user_token(client, session):
    return await token(client, session)


@pytest.fixture()
async def moderator_user_token(client, session):
    return await token(client, session, user_role=UserRoles.MODERATOR)


@pytest.fixture()
async def admin_user_token(client, session):
    return await token(client, session, user_role=UserRoles.ADMIN)


@pytest.fixture()
async def disable_normal_user_token(client, session):
    return await token(client, session, user_role=UserRoles.MODERATOR, is_active=False)


# @pytest.fixture()
# async def admin_user_token(client, session):
#     return await get_admin_token_header(client, session)


# @pytest.fixture()
# async def skill(client, session):
#     await setup_skill_data(session, 1)
#     return await get_skill_by_index(client)


@pytest.fixture()
async def normal_user(session):
    return await add_users_models(session, index=0)


@pytest.fixture()
async def moderator_user(session):
    return await add_users_models(session, index=0, user_role=UserRoles.MODERATOR)


@pytest.fixture()
async def admin_user(session):
    return await add_users_models(session, index=0, user_role=UserRoles.ADMIN)


@pytest.fixture()
async def disable_normal_user(session):
    return await add_users_models(session, index=0, user_role=UserRoles.BASE_USER, is_active=False)


@pytest.fixture()
async def skill(session):
    return await setup_skill_data(session, index=0)


@pytest.fixture()
async def another_skill(session):
    return await setup_skill_data(session, index=0)


# @pytest.fixture()
# async def disable_user(client, session):
#     users = await setup_users_data(session, disable_users=1)
#     user = users[0]

#     user_with_id = await get_user_by_index(client)
#     user_with_id["password"] = user.clean_password
#     return user_with_id
