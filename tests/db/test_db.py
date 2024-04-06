import pytest  # noqa
from icecream import ic  # noqa
from sqlalchemy import select
from sqlalchemy import text

from app.models import User  # noqa


async def get_tables(session):
    async with session.begin():
        query = text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
        )
        result = await session.execute(query)
        tables = [row[0] for row in result.fetchall()]
        return tables


@pytest.mark.asyncio
async def test_get_tables(session):
    tables = await get_tables(session)
    print("Tabelas no banco de dados:", tables)


@pytest.mark.asyncio
async def test_user(user):
    ic(user)


@pytest.mark.asyncio
async def test_other_test(other_user):
    ic(other_user)


@pytest.mark.asyncio
async def test_both_users(session, user, other_user):
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.fetchall()

    print(f"len total do users: {len(users)}")
    for item in [user, users[0][0], other_user, users[1][0]]:
        print("\n")
        ic(item)
    # print(f"Primeiro user(fixture): {user}\n")
    # print(f"Primeiro user(query): {users[0]}\n")

    # print(f"Segundo user(fixture): {user}\n")
    # print(f"Segundo user(query): {users[1]}\n")


@pytest.mark.asyncio
async def test_both_users_2(user, other_user):
    ic(user, other_user)
