import pytest
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_factory_users


async def setup_data(session: AsyncSession) -> None:
    users_with_password = create_factory_users(2)
    ic(users_with_password)
    session.add_all(users_with_password["users"])
    await session.flush()
    await session.commit()
    return users_with_password


@pytest.mark.anyio
async def test_setup_data(session):
    from app.models import User
    from sqlalchemy import select

    ic(session)
    t = await setup_data(session)
    query = await session.execute(select(User))
    result = query.scalars().all()
    ic(result, t)


@pytest.mark.anyio
async def test_setup_data2(session):
    from app.models import User
    from sqlalchemy import select

    ic(session)
    t = await setup_data(session)
    query = await session.execute(select(User))
    result = query.scalars().all()
    ic(result, t)


@pytest.mark.anyio
async def test_setup_data3(session):
    from app.models import User
    from sqlalchemy import select

    ic(session)
    t = await setup_data(session)
    query = await session.execute(select(User))
    result = query.scalars().all()
    ic(result, t)

def test_create_user_should_return_201_success(client, db, user_factory):
    response = client.post(
        "/v1/user",
        json={"email": user_factory.email, "username": user_factory.username, "password": user_factory.password},
    )
    assert response.status_code == 201
    print(response.json())
