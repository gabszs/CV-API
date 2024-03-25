import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Database
from app.core.settings import settings
from app.models.base_model import BaseModel
from app.repository.base_repository import BaseRepository
from app.repository.user_repository import UserRepository
from tests.factories import UserFactory


@pytest.fixture
def session():
    sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")

    engine = create_engine(sync_db_url)
    Session = sessionmaker(autoflush=False, autocommit=False, bind=engine)
    BaseModel.metadata.create_all(engine)
    with Session() as session:
        yield session
        session.rollback()

    BaseModel.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    user = UserFactory()

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def async_session():
    db = Database(settings.DATABASE_URL)
    return db.get_session()


@pytest.fixture
async def base_repository(async_session):
    return BaseRepository(session_factory=async_session)


@pytest.fixture
async def user_repository(async_session):
    return UserRepository(async_session)
