from uuid import UUID

import pytest
from freezegun import freeze_time
from icecream import ic

from app.core.settings import settings
from tests.conftest import setup_users_data
from tests.conftest import token
from tests.conftest import validate_datetime

base_auth_route = "/v1/auth"

mock_token = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTQwNzUxMTQsImlkIjoiN2NmMGVmNzAtNGQ1ZC00YjA3LTgyMTEtM2Q0YTZjYjRiYTNkIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwidXNlcm5hbWUiOiJzdHJpbmcifQ.XwHWtlzvw9-ujLyfHPeNR30V6H2uNQoKUWaq2_hrLQM",
    "expiration": "2024-04-25T16:58:33",
    "user_info": {
        "id": "7cf0ef70-4d5d-4b07-8211-3d4a6cb4ba3d",
        "created_at": "2024-04-25T18:25:39.409786Z",
        "updated_at": "2024-04-25T18:25:39.409786Z",
        "email": "user@example.com",
        "username": "string",
        "is_active": True,
        "is_superuser": False,
    },
}


@pytest.mark.anyio
async def test_get_token_should_return_200_OK(client, session):
    clean_users = await setup_users_data(session, normal_users=1)
    clean_user = clean_users[0]

    response = await client.post(
        f"{base_auth_route}/sign-in", json={"email__eq": clean_user.email, "password": clean_user.clean_password}
    )
    response_json = response.json()
    user_info = response_json["user_info"]

    assert response.status_code == 200
    assert "access_token" in response_json
    assert validate_datetime(response_json["expiration"])

    assert UUID(user_info["id"])
    assert user_info["email"] == clean_user.email
    assert user_info["username"] == clean_user.username
    assert user_info["is_active"] is True
    assert user_info["is_superuser"] is False
    assert validate_datetime(user_info["created_at"])
    assert validate_datetime(user_info["updated_at"])


@pytest.mark.anyio
async def test_auth_token_expired_after_time_should_return_403_FORBIDDEN(client, session):
    overtime_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1
    clean_users = await setup_users_data(session, 1)
    clean_user = clean_users[0]
    with freeze_time("2023-12-28 12:00:00"):
        response = await client.post(
            f"{base_auth_route}/sign-in", json={"email__eq": clean_user.email, "password": clean_user.clean_password}
        )

        assert response.status_code == 200
        token = response.json()["access_token"]
        token_header = {"Authorization": f"Bearer {token}"}

    with freeze_time(f"2023-12-28 12:{overtime_minutes}:00"):
        response = await client.get(f"{base_auth_route}/me", headers=token_header)

        assert response.status_code == 403
        assert response.json() == {"detail": "Invalid token or expired token"}


@pytest.mark.anyio
async def test_auth_token_inexistent_user_should_return_401_INVALIDCREDENTIALS(client, session):
    response = await client.post(
        f"{base_auth_route}/sign-in", json={"email__eq": "email@test.com", "password": "test_password"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or user not exist"}


@pytest.mark.anyio
async def test_auth_token_wrong_user_should_return_401_INVALIDCREDENTIALS(client, session):
    clean_users = await setup_users_data(session, normal_users=1)
    clean_user = clean_users[0]

    response = await client.post(
        f"{base_auth_route}/sign-in", json={"email__eq": clean_user.email, "password": "wrong_password"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}


@pytest.mark.anyio
async def test_auth_get_me_route_without_token_should_return_403_FORBIDDEN(client, session):
    response = await client.get(f"{base_auth_route}/me", headers={"Authorization": ""})

    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.anyio
async def test_auth_get_me_should_return_200_OK(client, session):
    clean_user, auth_token = await token(client, session)
    token_header = {"Authorization": f"Bearer {auth_token}"}
    # response = await client.post(f"{base_auth_route}/refresh_token", headers=token_header)
    response = await client.get(f"{base_auth_route}/me", headers=token_header)
    response_json = response.json()

    assert response.status_code == 200
    assert UUID(response_json["id"])
    assert response_json["email"] == clean_user.email
    assert response_json["username"] == clean_user.username
    assert response_json["is_active"] is True
    assert response_json["is_superuser"] is False
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_auth_token_expired_after_dont_refresh_should_return_403_FORBIDDEN(client, session):
    overtime_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1
    clean_users = await setup_users_data(session, 1)
    clean_user = clean_users[0]
    with freeze_time("2023-12-28 12:00:00"):
        response = await client.post(
            f"{base_auth_route}/sign-in", json={"email__eq": clean_user.email, "password": clean_user.clean_password}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        token_header = {"Authorization": f"Bearer {token}"}

    with freeze_time(f"2023-12-28 12:{overtime_minutes}:00"):
        response = await client.post(f"{base_auth_route}/refresh_token", headers=token_header)

        assert response.status_code == 403
        assert response.json() == {"detail": "Invalid token or expired token"}


@pytest.mark.anyio
async def test_refresh_token_should_return_200_OK(client, session):
    overtime_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1
    clean_users = await setup_users_data(session, 1)
    clean_user = clean_users[0]
    with freeze_time("2023-12-28 12:00:00"):
        response = await client.post(
            f"{base_auth_route}/sign-in", json={"email__eq": clean_user.email, "password": clean_user.clean_password}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        token_header = {"Authorization": f"Bearer {token}"}

    with freeze_time(f"2023-12-28 12:{overtime_minutes}:00"):
        response = await client.post(f"{base_auth_route}/refresh_token", headers=token_header)

        response_json = response.json()
        user_info = response_json["user_info"]

        assert response.status_code == 200
        assert "access_token" in response_json
        assert validate_datetime(response_json["expiration"])

        assert UUID(user_info["id"])
        assert user_info["email"] == clean_user.email
        assert user_info["username"] == clean_user.username
        assert user_info["is_active"] is True
        assert user_info["is_superuser"] is False
        assert validate_datetime(user_info["created_at"])
        assert validate_datetime(user_info["updated_at"])


@pytest.mark.anyio
async def test_auth_sign_up_should_return_200_OK(client, session, factory_user):
    response = await client.post(
        f"{base_auth_route}/sign-up",
        json={"email": factory_user.email, "password": factory_user.password, "username": factory_user.username},
    )
    response_json = response.json()

    assert response.status_code == 201
    assert UUID(response_json["id"])
    assert response_json["email"] == factory_user.email
    assert response_json["username"] == factory_user.username
    assert response_json["is_active"] is True
    assert response_json["is_superuser"] is False
    assert validate_datetime(response_json["created_at"])
    assert validate_datetime(response_json["updated_at"])


@pytest.mark.anyio
async def test_auth_sign_up_should_return_409_username_already_registered(client, session):
    clean_users = await setup_users_data(session, 1)
    clean_user = clean_users[0]
    response = await client.post(
        f"{base_auth_route}/sign-up",
        json={"email": "different@email.com", "username": clean_user.username, "password": clean_user.password},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already registered"}


@pytest.mark.anyio
async def test_auth_sign_up_should_return_409_email_already_registered(client, session):
    clean_users = await setup_users_data(session, 1)
    clean_user = clean_users[0]
    response = await client.post(
        f"{base_auth_route}/sign-up",
        json={"email": clean_user.email, "username": "different_username", "password": clean_user.password},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


ic
