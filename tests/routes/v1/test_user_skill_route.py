from uuid import UUID

import pytest
from icecream import ic

from app.core.settings import settings
from tests.helpers import validate_datetime


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


ic
