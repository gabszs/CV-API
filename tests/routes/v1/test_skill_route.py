from urllib.parse import urlencode

import pytest
from icecream import ic

from tests.conftest import get_admin_token_header
from tests.conftest import setup_skill_data
from tests.conftest import token
from tests.conftest import validate_datetime

base_url = "/v1/skill"


async def get_skill_by_index(client, index: int):
    response = await client.get(f"{base_url}/?ordering=created_at")
    return response.json()["founds"][index]


@pytest.mark.anyio
async def test_create_normal_skills_should_return_201_POST(client, session, factory_skill):
    token_header = await get_admin_token_header(client, session)
    response = await client.post(
        f"{base_url}/",
        json={"skill_name": factory_skill.skill_name, "category": factory_skill.category},
        headers=token_header,
    )
    response_json = response.json()

    assert response.status_code == 201
    assert response_json["skill_name"] == factory_skill.skill_name
    assert response_json["category"] == factory_skill.category
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_create_normal_skill_should_return_422_unprocessable_entity_POST(client, session):
    token_header = await get_admin_token_header(client, session)
    response = await client.post(f"{base_url}/", headers=token_header)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_normal_skill_should_return_409_email_already_registered_POST(client, session):
    token_header = await get_admin_token_header(client, session)
    clean_skills = await setup_skill_data(session, 1)
    clean_skill = clean_skills[0]
    response = await client.post(
        f"{base_url}/",
        json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
        headers=token_header,
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Skill already registered"}


@pytest.mark.anyio
async def test_create_skill_should_return_409_email_already_registered_POST(client, session):
    token_header = await get_admin_token_header(client, session)
    clean_skills = await setup_skill_data(session)
    clean_skill = clean_skills[0]
    response = await client.post(
        f"{base_url}/",
        json={"skill_name": clean_skill.skill_name, "category": clean_skill.category},
        headers=token_header,
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Skill already registered"}


@pytest.mark.anyio
async def test_get_all_skills_should_return_200_OK_GET(session, client, default_search_options):
    clean_skills = await setup_skill_data(session=session, qty_size=8)
    response = await client.get(f"{base_url}/?{urlencode(default_search_options)}")
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert len(response_founds) == 8
    assert response_json["search_options"] == default_search_options | {"total_count": 8}
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
async def test_get_all_skills_with_page_size_should_return_200_OK_GET(session, client):
    query_find_parameters = {"ordering": "created_at", "page": 1, "page_size": 5}
    clean_skills = await setup_skill_data(session, 5)
    response = await client.get(f"{base_url}/?{urlencode(query_find_parameters)}")
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert all(
        [
            skill.skill_name == response_founds[count]["skill_name"]
            and skill.category == response_founds[count]["category"]
            for count, skill in enumerate(clean_skills[: query_find_parameters["page_size"]])
        ]
    )
    assert len(response_founds) == 5
    assert response_json["search_options"] == query_find_parameters | {"total_count": 5}
    assert all([validate_datetime(skill["created_at"]) for skill in response_founds])
    assert all([validate_datetime(skill["updated_at"]) for skill in response_founds])


@pytest.mark.anyio
async def test_get_all_skills_with_pagination_should_return_200_OK_GET(session, client):
    query_find_parameters = {"ordering": "created_at", "page": 2, "page_size": 4}
    clean_skills = await setup_skill_data(session=session, qty_size=8)
    response = await client.get(f"{base_url}/?{urlencode(query_find_parameters)}")
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert all(
        [
            skill.skill_name == response_founds[count]["skill_name"]
            and skill.category == response_founds[count]["category"]
            for count, skill in enumerate(clean_skills[4:])
        ]
    )
    assert len(response_founds) == query_find_parameters["page_size"]
    assert response_json["search_options"] == query_find_parameters | {
        "total_count": query_find_parameters["page_size"]
    }
    assert all([validate_datetime(skill["created_at"]) for skill in response_founds])
    assert all([validate_datetime(skill["updated_at"]) for skill in response_founds])


@pytest.mark.anyio
async def test_delete_skill_should_return_200_OK_DELETE(session, client):
    token_header = await get_admin_token_header(client, session)
    _ = await setup_skill_data(session=session, qty_size=1)
    skill = await get_skill_by_index(client, 0)

    response = await client.delete(f"{base_url}/{skill['id']}", headers=token_header)
    response_json = response.json()
    get_skills_response = await client.get(f"{base_url}/?offset=0&limit=100")

    assert response.status_code == 200
    assert response_json == {"detail": "Skill has been deleted successfully"}
    assert get_skills_response.status_code == 200
    assert len(get_skills_response.json()["founds"]) == 0


@pytest.mark.anyio
async def test_delete_skill_should_return_403_FORBIDDEN_DELETE(session, client):
    _, auth_token = await token(client, session, normal_users=1)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    _ = await setup_skill_data(session=session, qty_size=1)
    skill = await get_skill_by_index(client, 0)

    response = await client.delete(f"{base_url}/{skill['id']}", headers=token_header)
    response_json = response.json()
    get_skills_response = await client.get(f"{base_url}/?offset=0&limit=100")

    assert response.status_code == 403
    assert response_json == {"detail": "Not enough permissions"}
    assert get_skills_response.status_code == 200
    assert len(get_skills_response.json()["founds"]) == 1


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
