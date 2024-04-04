import pytest
from icecream import ic
from sqlalchemy import select

from app.models import User


@pytest.mark.asyncio
async def test_fixtures(session, user):
    ic(session, user)

    users = await session.execute(select(User))
    print(len(list(users)))
    ic(list(users))
