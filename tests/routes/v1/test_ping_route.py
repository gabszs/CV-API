import pytest


@pytest.mark.anyio
async def test_ping_route_should_return_200_OK(client):
    response = await client.get("/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"detail": "Pong"}
