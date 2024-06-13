from urllib.parse import urlencode

import pytest
from icecream import ic

from app.core.settings import settings
from tests.helpers import setup_skill_data
from tests.helpers import validate_datetime


@pytest.mark.anyio
async def test_create_normal_skills_should_return_201_POST(client, session, factory_skill, admin_user_token):
    response = await client.post(
        f"{settings.base_skill_url}/",
        json={"skill_name": factory_skill.skill_name, "category": factory_skill.category},
        headers=admin_user_token,
    )
    response_json = response.json()
    assert response.status_code == 201
    assert response_json["skill_name"] == factory_skill.skill_name
    assert response_json["category"] == factory_skill.category
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_create_normal_skill_should_return_422_unprocessable_entity_POST(client, session, admin_user_token):
    response = await client.post(f"{settings.base_skill_url}/", headers=admin_user_token)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_normal_skill_should_return_409_email_already_registered_POST(
    client, session, admin_user_token, skill
):
    response = await client.post(
        f"{settings.base_skill_url}/",
        json={"skill_name": skill.skill_name, "category": skill.category},
        headers=admin_user_token,
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Skill already registered"}


@pytest.mark.anyio
async def test_get_all_skills_should_return_200_OK_GET(session, client, default_search_options):
    clean_skills = await setup_skill_data(session, skills_qty=8)
    response = await client.get(f"{settings.base_skill_url}/?{urlencode(default_search_options)}")
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
async def test_create_skill_should_return_409_email_already_registered_POST(client, session, admin_user_token, skill):
    response = await client.post(
        f"{settings.base_skill_url}/",
        json={"skill_name": skill.skill_name, "category": skill.category},
        headers=admin_user_token,
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Skill already registered"}


@pytest.mark.anyio
async def test_get_all_skills_with_page_size_should_return_200_OK_GET(session, client):
    query_find_parameters = {"ordering": "id", "page": 1, "page_size": 5}
    clean_skills = await setup_skill_data(session, 5)
    response = await client.get(f"{settings.base_skill_url}/?{urlencode(query_find_parameters)}")
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
    query_find_parameters = {"ordering": "id", "page": 2, "page_size": 4}
    clean_skills = await setup_skill_data(session, skills_qty=8)
    response = await client.get(f"{settings.base_skill_url}/?{urlencode(query_find_parameters)}")
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
async def test_delete_skill_should_return_204_OK_DELETE(session, client, admin_user_token, skill):
    response = await client.delete(f"{settings.base_skill_url}/{skill.id}", headers=admin_user_token)
    get_skills_response = await client.get(f"{settings.base_skill_url}/")

    assert response.status_code == 204
    assert get_skills_response.status_code == 200
    assert len(get_skills_response.json()["founds"]) == 0


@pytest.mark.anyio
async def test_delete_skill_should_return_403_FORBIDDEN_DELETE(session, client, normal_user_token, skill):
    response = await client.delete(f"{settings.base_skill_url}/{skill.id}", headers=normal_user_token)
    response_json = response.json()
    get_skills_response = await client.get(f"{settings.base_skill_url}/")

    assert response.status_code == 403
    assert response_json == {"detail": "Not enough permissions"}
    assert get_skills_response.status_code == 200
    assert len(get_skills_response.json()["founds"]) == 1


@pytest.mark.anyio
async def test_get_skill_by_id_should_return_200_OK_GET(session, client, skill):
    response = await client.get(f"{settings.base_skill_url}/{skill.id}")
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["skill_name"] == skill.skill_name
    assert response_json["category"] == skill.category
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_get_by_id_should_return_404_NOT_FOUND_GET(session, client):
    id = 10
    response = await client.get(f"{settings.base_skill_url}/{id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"id not found: {id}"}


@pytest.mark.anyio
async def test_put_skill_should_return_200_OK_PUT(session, client, factory_skill, skill, admin_user_token):
    different_skill = {
        "skill_name": factory_skill.skill_name,
        "category": factory_skill.category,
    }
    response = await client.put(f"{settings.base_skill_url}/{skill.id}", headers=admin_user_token, json=different_skill)
    response_json = response.json()
    assert response.status_code == 200
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])
    assert all([response_json[key] == value for key, value in different_skill.items()])


@pytest.mark.anyio
async def test_put_other_id_skill_should_return_404_NOT_FOUND_PUT(
    session, client, factory_skill, skill, admin_user_token
):
    id = 2
    different_skill = {
        "skill_name": skill.skill_name,
        "category": skill.category,
    }
    response = await client.put(f"{settings.base_skill_url}/{id}", headers=admin_user_token, json=different_skill)
    response_json = response.json()
    assert response.status_code == 404
    assert response_json == {"detail": f"id not found: {id}"}


@pytest.mark.anyio
async def test_put_same_skill_should_return_400_BAD_REQUEST_PUT(session, client, skill, admin_user_token):
    different_skill = {
        "skill_name": skill.skill_name,
        "category": skill.category,
    }
    response = await client.put(f"{settings.base_skill_url}/{skill.id}", headers=admin_user_token, json=different_skill)
    response_json = response.json()
    assert response.status_code == 400
    assert response_json == {"detail": "No changes detected"}


@pytest.mark.anyio
async def test_put_skill_should_return_403_FORBIDDEN(session, client, factory_skill, skill, normal_user_token):
    different_skill = {
        "skill_name": factory_skill.skill_name,
        "category": factory_skill.category,
    }
    response = await client.put(
        f"{settings.base_skill_url}/{skill.id}", headers=normal_user_token, json=different_skill
    )
    assert response.json() == {"detail": "Not enough permissions"}
    assert response.status_code == 403


# periodic erros here
@pytest.mark.anyio
async def test_patch_skill_category_should_return_200_OK_PUT(session, client, factory_skill, skill, admin_user_token):
    enpoint = f"{settings.base_skill_url}/{skill.id}/category/{factory_skill.category.value}"
    response = await client.patch(enpoint, headers=admin_user_token)
    response_json = response.json()

    assert response.status_code == 200
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])
    assert response_json["category"] == factory_skill.category


# ERROR BROKEN TEST, PERIODIC
@pytest.mark.anyio
async def test_patch_same_skill_category_should_return_400_BAD_REQUEST_PATCH(session, client, skill, admin_user_token):
    response = await client.patch(
        f"{settings.base_skill_url}/{skill.id}/category/{skill.category.value}", headers=admin_user_token
    )
    response_json = response.json()
    assert response.status_code == 400
    assert response_json == {"detail": "No changes detected"}


# ERROR BROKEN TEST, PERIODIC
@pytest.mark.anyio
async def test_patch_skill_category_should_return_404_NOT_FOUND_PATCH(
    session, client, factory_skill, skill, admin_user_token
):
    id = 33
    response = await client.patch(
        f"{settings.base_skill_url}/{id}/category/{factory_skill.category.value}", headers=admin_user_token
    )
    response_json = response.json()
    assert response.status_code == 404
    assert response_json == {"detail": f"id not found: {id}"}


@pytest.mark.anyio
async def test_patch_skill_skill_name_should_return_200_OK_PUT(session, client, factory_skill, skill, admin_user_token):
    response = await client.patch(
        f"{settings.base_skill_url}/{skill.id}/skill_name/{factory_skill.skill_name}", headers=admin_user_token
    )
    response_json = response.json()
    assert response.status_code == 200
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])
    assert response_json["skill_name"] == factory_skill.skill_name


@pytest.mark.anyio
async def test_patch_same_skill_skill_name_should_return_400_BAD_REQUEST_PATCH(
    session, client, factory_skill, skill, admin_user_token
):
    response = await client.patch(
        f"{settings.base_skill_url}/{skill.id}/skill_name/{skill.skill_name}", headers=admin_user_token
    )
    response_json = response.json()
    assert response.status_code == 400
    assert response_json == {"detail": "No changes detected"}


@pytest.mark.anyio
async def test_patch_skill_skill_name_should_return_404_NOT_FOUND_PATCH(
    session, client, factory_skill, skill, admin_user_token
):
    id = 33
    response = await client.patch(
        f"{settings.base_skill_url}/{id}/skill_name/{factory_skill.skill_name}", headers=admin_user_token
    )
    response_json = response.json()
    assert response.status_code == 404
    assert response_json == {"detail": f"id not found: {id}"}


ic
