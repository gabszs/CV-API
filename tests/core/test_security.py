import pytest

from tests.conftest import token
from tests.routes.v1.test_auth_route import base_auth_route


@pytest.mark.anyio
async def test_security_wrong_bearer_credential_403_FORBIDDEN(client, session):
    _, auth_token = await token(client, session)
    wrong_token_header = {"Authorization": f"Bear {auth_token}"}
    response = await client.get(f"{base_auth_route}/me", headers=wrong_token_header)

    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid authentication credentials"}
