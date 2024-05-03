import pytest
from icecream import ic

from tests.conftest import setup_skill_data
from tests.conftest import validate_datetime


base_url = "/v1/skill"


@pytest.mark.anyio
async def test_create_skill_should_return_201_POST(client, session, factory_skill):
    response = await client.post(
        f"{base_url}/", json={"skill_name": factory_skill.skill_name, "category": factory_skill.category}
    )
    response_json = response.json()

    assert response.status_code == 201
    assert isinstance(response_json["id"], int)
    assert response_json["skill_name"] == factory_skill.skill_name
    assert response_json["category"] == factory_skill.category
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_create_skill_should_return_422_unprocessable_entity_POST(client):
    response = await client.post(
        f"{base_url}/",
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_skill_should_return_409_email_already_registered_POST(client, session):
    clean_skills = await setup_skill_data(session)
    clean_user = clean_skills[0]
    response = await client.post(
        f"{base_url}/",
        json={"skill_name": clean_user.skill_name, "category": clean_user.category},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Skill already registered"}


ic
