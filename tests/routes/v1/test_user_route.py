import pytest
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import batch_users_by_options


async def setup_data(
    session: AsyncSession, normal_users: int = 0, admin_users: int = 0, disable_users: int = 0, disable_admins: int = 0
) -> None:
    users, clean_users = batch_users_by_options(
        normal_users=normal_users, admin_users=admin_users, disable_users=disable_users, disable_admins=disable_admins
    )
    session.add_all(users)
    await session.flush()
    await session.commit()
    return clean_users


# @pytest.mark.anyio
# async def test_setup_data(session, client):
#     await setup_data(session, admin_users=1, disable_users=5)
#     users = await client.get("/v1/user/?offset=0&limit=100")
#     ic(client, users.json())


@pytest.mark.anyio
async def test_setup_data1(session, client):
    clean_users = await setup_data(session, disable_admins=1)
    users = await client.get("/v1/user/?offset=0&limit=100")
    ic(client, users.json(), clean_users)
