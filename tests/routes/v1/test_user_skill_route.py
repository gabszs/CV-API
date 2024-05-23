# import pytest
# from icecream import ic

# from tests.conftest import get_normal_token_header
# from tests.conftest import setup_skill_data
# from tests.conftest import setup_users_data
# from tests.conftest import validate_datetime
# from tests.routes.v1.test_skill_route import get_skill_by_index
# from tests.routes.v1.test_user_route import get_user_by_index

# base_url = "v1/user-skill"


# async def get_search_normal_user_skill_data(client, session, normal_users: int = 1, skills_qty: int = 1, **kwargs):
#     await setup_users_data(session, normal_users=normal_users, **kwargs)
#     await setup_skill_data(session, skills_qty)

#     user_search = await get_user_by_index(client)
#     skill_search = await get_skill_by_index(client)

#     return user_search, skill_search


# @pytest.mark.anyio
# async def test_create_normal_user_skills_should_return_201_POST(client, session, factory_user_skill):
#     token_header = await get_normal_token_header(client, session)
#     user_search, skill_search = await get_search_normal_user_skill_data(client, session)

#     response = await client.post(
#         f"{base_url}/",
#         json={
#             "users_id": user_search["id"],
#             "skill_id": skill_search["id"],
#             "skill_level": factory_user_skill.skill_level,
#             "skill_years_experience": factory_user_skill.skill_years_experience,
#         },
#         headers=token_header,
#     )
#     response_json = response.json()
#     ic(response_json, response)
#     validate_datetime
#     assert False


# ic

# assert response.status_code == 201
# assert response_json["skill_name"] == factory_skill.skill_name
# assert response_json["category"] == factory_skill.category
# assert validate_datetime(response_json["created_at"])
# assert validate_datetime(response_json["updated_at"])


# @pytest.mark.anyio
# async def test_create_normal_skill_should_return_422_unprocessable_entity_POST(client, session):
#     token_header = await get_admin_token_header(client, session)
#     response = await client.post(f"{base_url}/", headers=token_header)

#     assert response.status_code == 422


# @pytest.mark.anyio
# async def test_create_normal_skill_should_return_409_email_already_registered_POST(client, session):
#     token_header = await get_admin_token_header(client, session)
#     clean_skills = await setup_skill_data(session, 1)
#     clean_skill = clean_skills[0]
#     response = await client.post(
#         f"{base_url}/",
#         json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
#         headers=token_header,
#     )

#     assert response.status_code == 409
#     assert response.json() == {"detail": "Skill already registered"}


# @pytest.mark.anyio
# async def test_create_skill_should_return_409_email_already_registered_POST(client, session):
#     token_header = await get_admin_token_header(client, session)
#     clean_skills = await setup_skill_data(session)
#     clean_skill = clean_skills[0]
#     response = await client.post(
#         f"{base_url}/",
#         json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
#         headers=token_header,
#     )

#     assert response.status_code == 409
#     assert response.json() == {"detail": "Skill already registered"}
