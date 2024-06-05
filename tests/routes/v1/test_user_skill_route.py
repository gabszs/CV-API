# from uuid import UUID
# import pytest
# from icecream import ic
# from tests.helpers import get_skill_by_index
# from tests.helpers import get_user_by_index
# from tests.helpers import setup_skill_data
# from tests.helpers import setup_users_data
# from tests.helpers import validate_datetime
# from app.core.settings import settings
# async def get_search_normal_user_skill_data(client, session, normal_users: int = 1, skills_qty: int = 1, **kwargs):
#     await setup_users_data(session, normal_users=normal_users, **kwargs)
#     await setup_skill_data(session, skills_qty)
#     user_search = await get_user_by_index(client)
#     skill_search = await get_skill_by_index(client)
#     return user_search, skill_search
# # @router.get("/get-skills-by-user/{user_id}", response_model=FindSkillsByUser)
# # async def get_skills_by_user(
# #     user_id: UUID,
# #     service: UserSkillServiceDependency,
# #     find_query: FindBase = Depends(),
# @pytest.mark.anyio
# async def test_get_all_skills_by_user_should_return_200_GET():
#     pass
# @pytest.mark.anyio
# async def test_create_normal_user_skills_should_return_201_POST(
#     client, session, normal_user_token, factory_user_skill, skill, normal_user
# ):
#     response = await client.post(
#         f"{base_url}/",
#         json={
#             "users_id": normal_user["id"],
#             "skill_id": skill["id"],
#             "skill_level": factory_user_skill.skill_level,
#             "skill_years_experience": factory_user_skill.skill_years_experience,
#         },
#         headers=normal_user_token,
#     )
#     response_json = response.json()
#     assert response.status_code == 201
#     assert UUID(response_json["id"])
#     assert response_json["skill_id"] == skill["id"]
#     assert response_json["users_id"] == normal_user["id"]
#     assert response_json["skill_level"] == factory_user_skill.skill_level
#     assert response_json["skill_years_experience"] == factory_user_skill.skill_years_experience
#     assert validate_datetime(response_json["created_at"])
#     assert validate_datetime(response_json["updated_at"])
# @pytest.mark.anyio
# async def test_get_skills_by_id_should_return_200_OK_GET(client, session, normal_user_token, factory_user_skill):
#     pass
# # @pytest.mark.anyio
# # async def test_create_normal_skill_should_return_422_unprocessable_entity_POST(client, session):
# #     token_header = await get_admin_token_header(client, session)
# #     response = await client.post(f"{base_url}/", headers=token_header)
# #     assert response.status_code == 422
# # @pytest.mark.anyio
# # async def test_create_normal_skill_should_return_409_email_already_registered_POST(client, session):
# #     token_header = await get_admin_token_header(client, session)
# #     clean_skills = await setup_skill_data(session, 1)
# #     clean_skill = clean_skills[0]
# #     response = await client.post(
# #         f"{base_url}/",
# #         json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
# #         headers=token_header,
# #     )
# #     assert response.status_code == 409
# #     assert response.json() == {"detail": "Skill already registered"}
# # @pytest.mark.anyio
# # async def test_create_skill_should_return_409_email_already_registered_POST(client, session):
# #     token_header = await get_admin_token_header(client, session)
# #     clean_skills = await setup_skill_data(session)
# #     clean_skill = clean_skills[0]
# #     response = await client.post(
# #         f"{base_url}/",
# #         json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
# #         headers=token_header,
# #     )
# #     assert response.status_code == 409
# #     assert response.json() == {"detail": "Skill already registered"}
# ic
