import pytest
# from sqlalchemy import select
# from app.models import User


@pytest.mark.asyncio
async def test_fixtures(user, other_user, session):
    # from app.models import User
    # from sqlalchemy import select
    # query_1 = select(User)
    # from icecream import ic
    # result = await session.execute(query_1)
    # users = result.scalars().all()
    print(user, other_user)
    # print("\n\n\n")
    # print(users)


@pytest.mark.asyncio
async def test_db(session, user, other_user):
    # from icecream import ic
    print(user, other_user)


#     from app.models import User
#     from sqlalchemy import select
#     query_1 = select(User).where(User.email == "user_0@test.com")
#     query_2 = select(User).where(User.email == "user_1@test.com")

#     users = await session.execute(query_1)
#     user2 = await session.execute(query_2)
#     user2 = user2.scalars().first()
#     users = users.scalars().all()
#     print("\n\n")
#     ic(users)

#     if user2:
#         print("not deu merda")
#     else:
#         print("dweu merda")

# @pytest.mark.asyncio
# async def test_get_session():
#     db = Database(settings.DATABASE_URL)
#     async with db.session() as session:
#         assert isinstance(session, AsyncSession)
#         query = await session.execute(text("SELECT 1"))
#         assert query.scalar() == 1


# def test_sync_db_create_user_success(session):
#     new_user = User(username="Gabriel", password="password", email="gabriel@test.com")
#     session.add(new_user)
#     session.commit()
#     user = session.scalar(select(User).where(User.email == new_user.email))
#     assert user.username == new_user.username
#     assert user.password == new_user.password
#     assert user.email == new_user.email


# @pytest.mark.asyncio
# async def test_client(async_session):
#     from icecream import ic
#     from sqlalchemy import text

#     # keys = await db.get_table_names()
#     # print(f"Matadata keys: {keys}")
#     result = await async_session.execute(
#         text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
#     )
#     tables = result.fetchall()
#     # table_names = [table[0] for table in tables]
#     print("Nomes das tabelas:", tables)
#     ic(tables)
