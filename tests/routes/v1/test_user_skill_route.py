from typing import Dict
from urllib.parse import urlencode
from uuid import UUID

import pytest
from icecream import ic

from app.core.settings import settings
from tests.helpers import validate_datetime
from tests.schemas import UserSkillTest


def compare_factory_and_schema_assoc(fixture_assoc: UserSkillTest, schema_assoc: Dict[str, str]):
    assert str(fixture_assoc.user_id) == (schema_assoc["user_id"])
    assert fixture_assoc.skill_id == schema_assoc["skill_id"]
    assert fixture_assoc.skill_level == schema_assoc["skill_level"]
    assert fixture_assoc.skill_years_experience == schema_assoc["skill_years_experience"]


# POST - CREATE
@pytest.mark.anyio
async def test_create_normal_user_skills_should_return_201_POST(
    client, session, normal_user_token, factory_user_skill, skill, normal_user
):
    response = await client.post(
        f"{settings.base_user_skills_route}/",
        json={
            "user_id": str(normal_user.id),
            "skill_id": str(skill.id),
            "skill_level": factory_user_skill.skill_level,
            "skill_years_experience": factory_user_skill.skill_years_experience,
        },
        headers=normal_user_token,
    )
    response_json = response.json()

    assert response.status_code == 201
    assert UUID(response_json["id"])
    assert response_json["skill_id"] == skill.id
    assert UUID(response_json["user_id"]) == normal_user.id
    assert response_json["skill_level"] == factory_user_skill.skill_level
    assert response_json["skill_years_experience"] == factory_user_skill.skill_years_experience
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_get_skills_by_id_should_return_200_OK_GET(client, session, normal_user_token, factory_user_skill):
    pass


@pytest.mark.anyio
async def test_create_normal_skill_should_return_422_unprocessable_entity_POST(client, session, normal_user_token):
    response = await client.post(f"{settings.base_user_skills_route}/", headers=normal_user_token)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_duplicate_user_skills_should_return_409_POST(
    client, session, normal_user_token, factory_user_skill, skill, normal_user
):
    # First creation should succeed
    await client.post(
        f"{settings.base_user_skills_route}/",
        json={
            "user_id": str(normal_user.id),
            "skill_id": str(skill.id),
            "skill_level": factory_user_skill.skill_level,
            "skill_years_experience": factory_user_skill.skill_years_experience,
        },
        headers=normal_user_token,
    )

    # Second creation should fail due to duplication
    response = await client.post(
        f"{settings.base_user_skills_route}/",
        json={
            "user_id": str(normal_user.id),
            "skill_id": str(skill.id),
            "skill_level": factory_user_skill.skill_level,
            "skill_years_experience": factory_user_skill.skill_years_experience,
        },
        headers=normal_user_token,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Association already created"


@pytest.mark.anyio
async def test_create_user_skills_with_missing_data_should_return_422_POST(client, normal_user_token, skill):
    response = await client.post(
        f"{settings.base_user_skills_route}/",
        json={
            "user_id": "",  # Missing user ID
            "skill_id": str(skill.id),
            "skill_level": "",  # Missing skill level
            "skill_years_experience": 5,
        },
        headers=normal_user_token,
    )

    assert response.status_code == 422


# GET - ALL
@pytest.mark.anyio
async def test_get_all_users_skills_should_return_200_OK_GET(
    client, batch_user_skill_assoc, default_created_search_options, moderator_user_token
):
    response = await client.get(
        f"{settings.base_user_skills_route}/?{urlencode(default_created_search_options)}", headers=moderator_user_token
    )
    response_json = response.json()
    response_founds = response_json["founds"]
    assert response.status_code == 200
    assert len(response_founds) == 8
    assert response_json["search_options"] == default_created_search_options | {"total_count": 8}
    assert all([validate_datetime(user_skill["created_at"]) for user_skill in response_founds])
    assert all([validate_datetime(user_skill["updated_at"]) for user_skill in response_founds])
    assert [
        compare_factory_and_schema_assoc(fixture_assoc=skill, schema_assoc=response_founds[count])
        for count, skill in enumerate(batch_user_skill_assoc)
    ]


@pytest.mark.anyio
async def test_get_all_users_skills_with_page_size_should_return_200_OK_GET(
    client, batch_user_skill_assoc, moderator_user_token
):
    query_find_parameters = {"ordering": "created_at", "page": 1, "page_size": 5}
    response = await client.get(
        f"{settings.base_user_skills_route}/?{urlencode(query_find_parameters)}", headers=moderator_user_token
    )
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert len(response_json["founds"]) == 5
    assert response_json["search_options"] == query_find_parameters | {"total_count": 5}
    assert all([validate_datetime(user["created_at"]) for user in response_json["founds"]])
    assert all([validate_datetime(user["updated_at"]) for user in response_json["founds"]])
    assert [
        compare_factory_and_schema_assoc(fixture_assoc=skill, schema_assoc=response_founds[count])
        for count, skill in enumerate(batch_user_skill_assoc[: query_find_parameters["page_size"]])
    ]


@pytest.mark.anyio
async def test_get_all_users_skills_with_pagination_should_return_200_OK_GET(
    client, batch_user_skill_assoc, moderator_user_token
):
    page_size = 3
    page = 2
    ordering = "created_at"
    query_find_parameters = {"ordering": ordering, "page": page, "page_size": page_size}
    response = await client.get(
        f"{settings.base_user_skills_route}/?{urlencode(query_find_parameters)}", headers=moderator_user_token
    )
    response_json = response.json()

    assert response.status_code == 200
    assert len(response_json["founds"]) == query_find_parameters["page_size"]
    assert response_json["search_options"] == query_find_parameters | {
        "total_count": query_find_parameters["page_size"]
    }
    assert all([validate_datetime(user["created_at"]) for user in response_json["founds"]])
    assert all([validate_datetime(user["updated_at"]) for user in response_json["founds"]])
    assert [
        compare_factory_and_schema_assoc(fixture_assoc=skill, schema_assoc=response_json["founds"][count])
        for count, skill in enumerate(batch_user_skill_assoc[page_size : page_size * page])
    ]


# GET - BY ID
@pytest.mark.anyio
async def test_get_user_skill_by_id_should_return_200_OK_GET(
    client, user_skill_assoc, default_created_search_options, moderator_user_token
):
    response = await client.get(
        f"{settings.base_user_skills_route}/{user_skill_assoc.id}", headers=moderator_user_token
    )
    response_json = response.json()

    assert response.status_code == 200
    compare_factory_and_schema_assoc(user_skill_assoc, response_json)


@pytest.mark.anyio
async def test_get_user_SKILL_by_id_should_return_404_NOT_FOUND_GET(session, client, moderator_user_token, random_uuid):
    response = await client.get(f"{settings.base_users_url}/{random_uuid}", headers=moderator_user_token)

    assert response.status_code == 404
    assert response.json() == {"detail": f"id not found: {random_uuid}"}


# DELETE
@pytest.mark.anyio
async def test_delete_USER_skill_should_return_204_OK_DELETE(session, client, admin_user_token, user_skill_assoc):
    response = await client.delete(f"{settings.base_user_skills_route}/{user_skill_assoc.id}", headers=admin_user_token)
    get_skills_response = await client.get(f"{settings.base_user_skills_route}/", headers=admin_user_token)
    assert response.status_code == 204
    assert get_skills_response.status_code == 200
    assert len(get_skills_response.json()["founds"]) == 0


@pytest.mark.anyio
async def test_delete_USER_skill_should_return_403_FORBIDDEN_DELETE(
    session, client, normal_user_token, user_skill_assoc, admin_user_token
):
    response = await client.delete(
        f"{settings.base_user_skills_route}/{user_skill_assoc.id}", headers=normal_user_token
    )
    response_json = response.json()
    get_skills_response = await client.get(f"{settings.base_user_skills_route}/", headers=admin_user_token)
    assert response.status_code == 403
    assert response_json == {"detail": "Not enough permissions"}
    assert get_skills_response.status_code == 200
    assert len(get_skills_response.json()["founds"]) == 1


# PUT
@pytest.mark.anyio
async def test_put_USER_skill_should_return_200_OK_PUT(
    session, client, factory_user_skill, user_skill_assoc, admin_user_token
):
    different_user_skill = {
        "skill_level": factory_user_skill.skill_level,
        "skill_years_experience": factory_user_skill.skill_years_experience,
    }
    response = await client.put(
        f"{settings.base_user_skills_route}/{user_skill_assoc.id}", headers=admin_user_token, json=different_user_skill
    )
    response_json = response.json()

    assert response.status_code == 200
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])
    assert all([response_json[key] == value for key, value in different_user_skill.items()])


@pytest.mark.anyio
async def test_put_other_id_USER_skill_should_return_404_NOT_FOUND_PUT(
    session, client, factory_user_skill, admin_user_token, random_uuid
):
    different_user_skill = {
        "skill_level": factory_user_skill.skill_level,
        "skill_years_experience": factory_user_skill.skill_years_experience,
    }
    response = await client.put(
        f"{settings.base_user_skills_route}/{random_uuid}", headers=admin_user_token, json=different_user_skill
    )
    response_json = response.json()
    assert response.status_code == 404
    assert response_json == {"detail": f"id not found: {random_uuid}"}


@pytest.mark.anyio
async def test_put_same_USER_skill_should_return_400_BAD_REQUEST_PUT(
    session, client, user_skill_assoc, admin_user_token
):
    different_user_skill = {
        "skill_level": user_skill_assoc.skill_level,
        "skill_years_experience": user_skill_assoc.skill_years_experience,
    }
    response = await client.put(
        f"{settings.base_user_skills_route}/{user_skill_assoc.id}", headers=admin_user_token, json=different_user_skill
    )
    response_json = response.json()
    assert response.status_code == 400
    assert response_json == {"detail": "No changes detected"}


@pytest.mark.anyio
async def test_put_USER_skill_should_return_403_FORBIDDEN(
    session, client, factory_user_skill, user_skill_assoc, normal_user_token
):
    different_skill = {
        "skill_level": factory_user_skill.skill_level,
        "skill_years_experience": factory_user_skill.skill_years_experience,
    }
    response = await client.put(
        f"{settings.base_user_skills_route}/{user_skill_assoc.id}", headers=normal_user_token, json=different_skill
    )
    assert response.json() == {"detail": "Not enough permissions"}
    assert response.status_code == 403


# GET SKILLS - BY USER ID
@pytest.mark.anyio
async def test_get_all_skills_by_USER_id_should_return_200_OK_GET(
    client, session, user_multiples_skills, default_created_search_options, moderator_user_token
):
    response = await client.get(
        f"{settings.base_user_skills_route}/user/{user_multiples_skills.user_id}?{urlencode(default_created_search_options)}",
        headers=moderator_user_token,
    )
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert len(response_founds) == 8
    assert response_json["search_options"] == default_created_search_options | {"total_count": 8}
    assert all([validate_datetime(user_skill["created_at"]) for user_skill in response_founds])
    assert all([validate_datetime(user_skill["updated_at"]) for user_skill in response_founds])
    [
        compare_factory_and_schema_assoc(skill_fac, response_founds[counter])
        for counter, skill_fac in enumerate(user_multiples_skills.founds)
    ]
    assert response_json["search_options"] == default_created_search_options | {"total_count": 8}
    assert response_json["user_id"] == str(user_multiples_skills.user_id)


@pytest.mark.anyio
async def test_get_all_skills_by_USER_id_with_page_size_should_return_200_OK_GET(
    client, session, user_multiples_skills, moderator_user_token
):
    query_find_parameters = {"ordering": "created_at", "page": 1, "page_size": 5}
    response = await client.get(
        f"{settings.base_user_skills_route}/user/{user_multiples_skills.user_id}?{urlencode(query_find_parameters)}",
        headers=moderator_user_token,
    )
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert len(response_founds) == 5
    assert response_json["search_options"] == query_find_parameters | {"total_count": 5}
    assert all([validate_datetime(user["created_at"]) for user in response_founds])
    assert all([validate_datetime(user["updated_at"]) for user in response_founds])
    [
        compare_factory_and_schema_assoc(skill_fac, response_founds[counter])
        for counter, skill_fac in enumerate(user_multiples_skills.founds[: query_find_parameters["page_size"]])
    ]
    assert response_json["search_options"] == query_find_parameters | {"total_count": 5}
    assert response_json["user_id"] == str(user_multiples_skills.user_id)


@pytest.mark.anyio
async def test_get_all_skills_by_USER_id_with_pagination_should_return_200_OK_GET(
    client, session, user_multiples_skills, moderator_user_token
):
    page_size = 3
    page = 2
    ordering = "created_at"
    query_find_parameters = {"ordering": ordering, "page": page, "page_size": page_size}
    response = await client.get(
        f"{settings.base_user_skills_route}/user/{user_multiples_skills.user_id}?{urlencode(query_find_parameters)}",
        headers=moderator_user_token,
    )
    response_json = response.json()
    response_founds = response_json["founds"]

    assert response.status_code == 200
    assert len(response_founds) == query_find_parameters["page_size"]
    assert response_json["search_options"] == query_find_parameters | {
        "total_count": query_find_parameters["page_size"]
    }
    assert all([validate_datetime(user["created_at"]) for user in response_founds])
    assert all([validate_datetime(user["updated_at"]) for user in response_founds])
    assert response_json["search_options"] == query_find_parameters | {"total_count": page_size}
    assert response_json["user_id"] == str(user_multiples_skills.user_id)
    [
        compare_factory_and_schema_assoc(skill_fac, response_founds[counter])
        for counter, skill_fac in enumerate(user_multiples_skills.founds[page_size : page_size * page])
    ]


ic
