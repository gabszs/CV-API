from uuid import UUID
from uuid import uuid4

import pytest
from icecream import ic

from tests.conftest import setup_users_data
from tests.conftest import token
from tests.conftest import validate_datetime

base_url = "/v1/user"


async def get_user_by_index(client, index: int):
    response = await client.get(f"{base_url}/?offset=0&limit=100")
    return response.json()["founds"][index]


@pytest.mark.anyio
async def test_get_all_users_should_return_200_OK(session, client):
    clean_users = await setup_users_data(
        session=session, normal_users=2, admin_users=2, disable_users=2, disable_admins=2
    )
    response = await client.get(f"{base_url}/?offset=0&limit=100")
    response_json = response.json()
    users_json = response_json["founds"]

    assert response.status_code == 200
    assert len(users_json) == 8
    assert response_json["search_options"] == {"limit": 100, "offset": 0, "total_count": 8}
    assert all(
        [
            user.username == users_json[count].get("username") and user.email == users_json[count].get("email")
            for count, user in enumerate(clean_users)
        ]
    )
    assert all([validate_datetime(user["created_at"]) for user in users_json])
    assert all([validate_datetime(user["updated_at"]) for user in users_json])


@pytest.mark.anyio
async def test_get_all_users_with_limit_should_return_200_OK(session, client):
    limit = 5
    clean_users = await setup_users_data(
        session=session, normal_users=2, admin_users=2, disable_users=2, disable_admins=2
    )
    response = await client.get(f"{base_url}/?offset=0&limit={limit}")
    response_json = response.json()

    assert response.status_code == 200
    assert all(
        [
            user.username == response_json["founds"][count].get("username")
            and user.email == response_json["founds"][count].get("email")
            for count, user in enumerate(clean_users[:limit])
        ]
    )
    assert len(response_json["founds"]) == 5
    assert response_json["search_options"] == {"limit": limit, "offset": 0, "total_count": limit}
    assert all([validate_datetime(user["created_at"]) for user in response_json["founds"]])
    assert all([validate_datetime(user["updated_at"]) for user in response_json["founds"]])


@pytest.mark.anyio
async def test_get_all_users_with_offset_should_return_200_OK(session, client):
    offset = 3
    clean_users = await setup_users_data(
        session=session, normal_users=2, admin_users=2, disable_users=2, disable_admins=2
    )
    response = await client.get(f"{base_url}/?offset={offset}&limit=100")
    response_json = response.json()

    assert response.status_code == 200
    assert all(
        [
            user.username == response_json["founds"][count].get("username")
            and user.email == response_json["founds"][count].get("email")
            for count, user in enumerate(clean_users[offset:])
        ]
    )
    assert len(response_json["founds"]) == 5
    assert response_json["search_options"] == {"limit": 100, "offset": offset, "total_count": 5}
    assert all([validate_datetime(user["created_at"]) for user in response_json["founds"]])
    assert all([validate_datetime(user["updated_at"]) for user in response_json["founds"]])


@pytest.mark.anyio
async def test_get_all_users_with_pagination_should_return_200_OK(session, client):
    offset = 2
    limit = 3
    clean_users = await setup_users_data(
        session=session, normal_users=2, admin_users=2, disable_users=2, disable_admins=2
    )
    response = await client.get(f"{base_url}/?offset={offset}&limit={limit}")
    response_json = response.json()

    assert response.status_code == 200
    assert all(
        [
            user.username == response_json["founds"][count].get("username")
            and user.email == response_json["founds"][count].get("email")
            for count, user in enumerate(clean_users[offset : limit + offset])
        ]
    )
    assert len(response_json["founds"]) == limit
    assert response_json["search_options"] == {"limit": limit, "offset": offset, "total_count": limit}
    assert all([validate_datetime(user["created_at"]) for user in response_json["founds"]])
    assert all([validate_datetime(user["updated_at"]) for user in response_json["founds"]])


@pytest.mark.anyio
async def test_get_by_id_should_return_200_OK(session, client):
    user_index = 0
    clean_users = await setup_users_data(session=session, normal_users=4)
    clean_user = clean_users[user_index]
    user = await get_user_by_index(client, user_index)

    response = await client.get(f"{base_url}/{user['id']}")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["id"] == user["id"]
    assert response_json["is_active"] is True
    assert response_json["is_superuser"] is False
    assert response_json["email"] == clean_user.email
    assert response_json["username"] == clean_user.username
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_get_by_id_should_return_404_NOT_FOUND(session, client):
    random_uuid = str(uuid4())
    response = await client.get(f"{base_url}/{random_uuid}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"id not found: {random_uuid}"}


@pytest.mark.anyio
async def test_create_normal_user_should_return_422_unprocessable_entity(client):
    response = await client.post(
        f"{base_url}/",
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_normal_user_should_return_201(client, session, factory_user):
    response = await client.post(
        f"{base_url}/",
        json={"email": factory_user.email, "username": factory_user.username, "password": factory_user.password},
    )
    response_json = response.json()

    assert response.status_code == 201
    assert UUID(response_json["id"])
    assert response_json["email"] == factory_user.email
    assert response_json["username"] == factory_user.username
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_create_normal_user_should_return_409_email_already_registered(client, session):
    clean_users = await setup_users_data(session, 1)
    clean_user = clean_users[0]
    response = await client.post(
        f"{base_url}/",
        json={"email": clean_user.email, "username": "different_username", "password": clean_user.password},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


@pytest.mark.anyio
async def test_create_normal_user_should_return_409_username_already_registered(client, session):
    clean_users = await setup_users_data(session, 1)
    clean_user = clean_users[0]
    response = await client.post(
        f"{base_url}/",
        json={"email": "different@email.com", "username": clean_user.username, "password": clean_user.password},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already registered"}


@pytest.mark.anyio
async def test_disable_user_should_return_200_OK(session, client):
    clean_user, auth_token = await token(client, session)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    user = await get_user_by_index(client, 0)

    response = await client.delete(f"{base_url}/disable/{user['id']}", headers=token_header)
    response_json = response.json()
    modified_user = await get_user_by_index(client, 0)

    assert response.status_code == 200
    assert response_json == {"detail": "User has been desabled successfully"}
    assert user["is_active"] is True
    assert modified_user["is_active"] is False
    assert modified_user["email"] == clean_user.email
    assert modified_user["username"] == clean_user.username
    assert modified_user["id"] == user["id"]


@pytest.mark.anyio
async def test_disable_different_user_should_return_403_FORBIDDEN(session, client):
    _, auth_token = await token(client, session, normal_users=2, clean_user_index=0)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    other_user = await get_user_by_index(client, 1)

    response = await client.delete(f"{base_url}/disable/{other_user['id']}", headers=token_header)
    response_json = response.json()

    assert response.status_code == 403
    assert response_json == {"detail": "Not enough permissions"}


@pytest.mark.anyio
async def test_enable_user_user_should_return_200_OK(session, client):
    clean_user, auth_token = await token(client, session, normal_users=0, disable_users=1)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    user = await get_user_by_index(client, 0)

    response = await client.patch(f"{base_url}/enable_user/{user['id']}", headers=token_header)
    response_json = response.json()
    modified_user = await get_user_by_index(client, 0)

    assert response.status_code == 200
    assert response_json == {"detail": "User has been enabled successfully"}
    assert user["is_active"] is False
    assert modified_user["is_active"] is True
    assert modified_user["email"] == clean_user.email
    assert modified_user["username"] == clean_user.username
    assert modified_user["id"] == user["id"]


@pytest.mark.anyio
async def test_enable_user_different_user_should_return_403_FORBIDDEN(session, client):
    _, auth_token = await token(client, session, normal_users=2, clean_user_index=0)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    other_user = await get_user_by_index(client, 1)

    response = await client.patch(f"{base_url}/enable_user/{other_user['id']}", headers=token_header)
    response_json = response.json()

    assert response.status_code == 403
    assert response_json == {"detail": "Not enough permissions"}


@pytest.mark.anyio
async def test_delete_user_should_return_200_OK(session, client):
    clean_user, auth_token = await token(client, session)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    user = await get_user_by_index(client, 0)

    response = await client.delete(f"{base_url}/{user['id']}", headers=token_header)
    response_json = response.json()
    get_users_response = await client.get(f"{base_url}/?offset=0&limit=100")

    assert response.status_code == 200
    assert get_users_response.status_code == 200
    assert response_json == {"detail": "User has been deleted successfully"}
    assert len(get_users_response.json()["founds"]) == 0


@pytest.mark.anyio
async def test_delete_different_user_should_return_403_FORBIDDEN(session, client):
    _, auth_token = await token(client, session, normal_users=2, clean_user_index=0)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    other_user = await get_user_by_index(client, 1)

    response = await client.delete(f"{base_url}/{other_user['id']}", headers=token_header)
    response_json = response.json()

    assert response.status_code == 403
    assert response_json == {"detail": "Not enough permissions"}


@pytest.mark.anyio
async def test_put_user_should_return_200_OK(session, client, factory_user):
    clean_user, auth_token = await token(client, session)
    user = await get_user_by_index(client, index=0)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    different_user = {
        "email": factory_user.email,
        "username": factory_user.username,
        "is_active": False,
        "is_superuser": True,
    }

    response = await client.put(f"{base_url}/{user['id']}", headers=token_header, json=different_user)
    response_json = response.json()

    assert response.status_code == 200
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])
    assert all([response_json[key] == value for key, value in different_user.items()])


@pytest.mark.anyio
async def test_put_user_should_return_403_FORBIDDEN(session, client, factory_user):
    _, auth_token = await token(client, session, normal_users=2)
    user = await get_user_by_index(client, index=1)
    token_header = {"Authorization": f"Bearer {auth_token}"}

    different_user = {
        "email": factory_user.email,
        "username": factory_user.username,
        "is_active": False,
        "is_superuser": True,
    }

    response = await client.put(f"{base_url}/{user['id']}", headers=token_header, json=different_user)

    assert response.json() == {"detail": "Not enough permissions"}
    assert response.status_code == 403


ic
