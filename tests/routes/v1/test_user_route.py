def test_create_user_should_return_201_success(client, db, user_factory):
    response = client.post(
        "/v1/user",
        json={"email": user_factory.email, "username": user_factory.username, "password": user_factory.password},
    )

    assert response.status_code == 201
    print(response.json())
