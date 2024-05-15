import pytest
from icecream import ic

from tests.conftest import setup_skill_data
from tests.conftest import token
from tests.conftest import validate_datetime

base_url = "/v1/skill"


async def get_skill_by_index(client, index: int):
    response = await client.get(f"{base_url}/?offset=0&limit=100")
    return response.json()["founds"][index]


@pytest.mark.anyio
async def test_create_normal_skills_should_return_201_POST(client, session, factory_skill):
    response = await client.post(
        f"{base_url}/",
        json={"skill_name": factory_skill.skill_name, "category": factory_skill.category},
    )
    response_json = response.json()

    assert response.status_code == 201
    assert response_json["skill_name"] == factory_skill.skill_name
    assert response_json["category"] == factory_skill.category
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_create_normal_skill_should_return_422_unprocessable_entity_POST(client):
    response = await client.post(
        f"{base_url}/",
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_normal_skill_should_return_409_email_already_registered_POST(client, session):
    clean_skills = await setup_skill_data(session, 1)
    clean_skill = clean_skills[0]
    response = await client.post(
        f"{base_url}/",
        json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Skill already registered"}


@pytest.mark.anyio
async def test_create_skill_should_return_409_email_already_registered_POST(client, session):
    clean_skills = await setup_skill_data(session)
    clean_skill = clean_skills[0]
    response = await client.post(
        f"{base_url}/",
        json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Skill already registered"}


@pytest.mark.anyio
async def test_get_all_skills_should_return_200_OK_GET(session, client):
    clean_skills = await setup_skill_data(session=session, qty_size=8)
    response = await client.get(f"{base_url}/?offset=0&limit=100")
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert len(response_founds) == 8
    assert response_json["search_options"] == {"limit": 100, "offset": 0, "total_count": 8}
    assert all(
        [
            skill.skill_name == response_founds[count]["skill_name"]
            and skill.category == response_founds[count]["category"]
            for count, skill in enumerate(clean_skills)
        ]
    )

    assert all([validate_datetime(skill["created_at"]) for skill in response_founds])
    assert all([validate_datetime(skill["updated_at"]) for skill in response_founds])


@pytest.mark.anyio
async def test_get_all_skills_with_limit_should_return_200_OK_GET(session, client):
    limit = 5
    clean_skills = await setup_skill_data(session, 5)
    response = await client.get(f"{base_url}/?offset=0&limit={limit}")
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert all(
        [
            skill.skill_name == response_founds[count]["skill_name"]
            and skill.category == response_founds[count]["category"]
            for count, skill in enumerate(clean_skills[:limit])
        ]
    )
    assert len(response_founds) == 5
    assert response_json["search_options"] == {"limit": limit, "offset": 0, "total_count": limit}
    assert all([validate_datetime(skill["created_at"]) for skill in response_founds])
    assert all([validate_datetime(skill["updated_at"]) for skill in response_founds])


@pytest.mark.anyio
async def test_get_all_skills_with_offset_should_return_200_OK_GET(session, client):
    offset = 3
    skills_qty_size = 5
    clean_skills = await setup_skill_data(session=session, qty_size=skills_qty_size)
    response = await client.get(f"{base_url}/?offset={offset}&limit=100")
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert all(
        [
            skill.skill_name == response_founds[count]["skill_name"]
            and skill.category == response_founds[count]["category"]
            for count, skill in enumerate(clean_skills[offset:])
        ]
    )
    assert len(response_founds) == 2
    assert response_json["search_options"] == {"limit": 100, "offset": offset, "total_count": 2}
    assert all([validate_datetime(skill["created_at"]) for skill in response_founds])
    assert all([validate_datetime(skill["updated_at"]) for skill in response_founds])


@pytest.mark.anyio
async def test_get_all_skills_with_pagination_should_return_200_OK_GET(session, client):
    offset = 2
    limit = 3
    clean_skills = await setup_skill_data(session=session, qty_size=8)
    response = await client.get(f"{base_url}/?offset={offset}&limit={limit}")
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert all(
        [
            skill.skill_name == response_founds[count]["skill_name"]
            and skill.category == response_founds[count]["category"]
            for count, skill in enumerate(clean_skills[offset : limit + offset])
        ]
    )
    assert len(response_founds) == limit
    assert response_json["search_options"] == {"limit": limit, "offset": offset, "total_count": limit}
    assert all([validate_datetime(skill["created_at"]) for skill in response_founds])
    assert all([validate_datetime(skill["updated_at"]) for skill in response_founds])


@pytest.mark.anyio
async def test_delete_skill_should_return_200_OK_DELETE(session, client):
    _, auth_token = await token(client, session, normal_users=0, admin_users=1)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    _ = await setup_skill_data(session=session, qty_size=1)
    skill = await get_skill_by_index(client, 0)

    response = await client.delete(f"{base_url}/{skill['id']}", headers=token_header)
    response_json = response.json()
    get_users_response = await client.get(f"{base_url}/?offset=0&limit=100")

    assert response.status_code == 200
    assert response_json == {"detail": "Skill has been deleted successfully"}
    assert get_users_response.status_code == 200
    assert len(get_users_response.json()["founds"]) == 0


@pytest.mark.anyio
async def test_delete_skill_should_return_403_FORBIDDEN_DELETE(session, client):
    _, auth_token = await token(client, session, normal_users=1)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    _ = await setup_skill_data(session=session, qty_size=1)
    skill = await get_skill_by_index(client, 0)

    response = await client.delete(f"{base_url}/{skill['id']}", headers=token_header)
    response_json = response.json()
    get_users_response = await client.get(f"{base_url}/?offset=0&limit=100")

    assert response.status_code == 403
    assert response_json == {"detail": "Not enough permissions"}
    assert get_users_response.status_code == 200
    assert len(get_users_response.json()["founds"]) == 1


@pytest.mark.anyio
async def test_get_skill_by_id_should_return_200_OK_GET(session, client):
    skill_index = 0
    clean_skills = await setup_skill_data(session=session)
    clean_skill = clean_skills[skill_index]
    skill = await get_skill_by_index(client, skill_index)

    response = await client.get(f"{base_url}/{skill['id']}")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["skill_name"] == clean_skill.skill_name
    assert response_json["category"] == clean_skill.category
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_get_by_id_should_return_404_NOT_FOUND_GET(session, client):
    id = 10
    response = await client.get(f"{base_url}/{id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"id not found: {id}"}


ic
# @pytest.mark.anyio
# async def test_delete_different_user_should_return_403_FORBIDDEN_DELETE(session, client):
#     _, auth_token = await token(client, session, normal_users=2, clean_user_index=0)
#     token_header = {"Authorization": f"Bearer {auth_token}"}
#     other_user = await get_user_by_index(client, 1)

#     response = await client.delete(f"{base_url}/{other_user['id']}", headers=token_header)
#     response_json = response.json()

#     assert response.status_code == 403
#     assert response_json == {"detail": "Not enough permissions"}


# ic


# from app.schemas.skill_schema import BaseSkill
# from tests.factories import SkillFactory
# from tests.routes.v1.base_route_test import BaseTest


# class TestSkill(BaseTest):
#     def __init__(-> None:
#         # base_url, setup_func, base_schema, model_factory, model_name, id_type
#         super().__init__(
#             base_url=base_url,
#             setup_func=setup_skill_data,
#             base_schema=BaseSkill,
#             model_factory=SkillFactory,
#             model_name="Skills",
#             id_type=int,
#             base_input_keys=["skill_name", "category"]
#         )

# @pytest.mark.anyio
# @pytest.mark.parametrize("test_class", [TestSkill])
# async def test_skill_parametrized(test_class, client, session):
#     # Crie uma instância da classe de teste e execute seus métodos de teste
#     test_instance = test_class()
#     await test_instance.test_create_should_return_201_POST(client, session)
#     await test_instance.test_create_should_return_422_unprocessable_entity_POST(client)
#     await test_instance.test_create_should_return_409_email_already_registered_POST(client, session)
