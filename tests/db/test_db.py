import pytest
from sqlalchemy import select
from sqlalchemy import text

from app.core.database import AsyncSession
from app.core.database import Database
from app.core.settings import settings
from app.models import User


@pytest.mark.asyncio
async def test_get_session():
    db = Database(settings.DATABASE_URL)

    async with db.session() as session:
        assert isinstance(session, AsyncSession)
        query = await session.execute(text("SELECT 1"))
        assert query.scalar() == 1


def test_db_create_user_success(session):
    new_user = User(username="Gabriel", password="password", email="gabriel@test.com")

    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.email == new_user.email))

    assert user.username == new_user.username
    assert user.password == new_user.password
    assert user.email == new_user.email
