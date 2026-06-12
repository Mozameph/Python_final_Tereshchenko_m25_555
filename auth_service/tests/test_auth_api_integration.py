"""Интеграционные тесты Auth Service: полный пользовательский сценарий по HTTP."""


EMAIL = "ivanov@email.com"
PASSWORD = "strong_password_1"


async def _register(client, email=EMAIL, password=PASSWORD):
    return await client.post("/auth/register", json={"email": email, "password": password})


async def _login(client, email=EMAIL, password=PASSWORD):
    # OAuth2PasswordRequestForm -> form-data с полями username/password
    return await client.post("/auth/login", data={"username": email, "password": password})


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_full_auth_flow_register_login_me(client):
    # 1. Регистрация
    resp = await _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == EMAIL
    assert body["role"] == "user"
    assert "password_hash" not in body

    # 2. Логин (form-data, OAuth2PasswordRequestForm)
    resp = await _login(client)
    assert resp.status_code == 200
    token_body = resp.json()
    assert token_body["token_type"] == "bearer"
    token = token_body["access_token"]
    assert token

    # 3. /auth/me с Bearer-токеном
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me_body = resp.json()
    assert me_body["email"] == EMAIL
    assert me_body["id"] == body["id"]
    assert "password_hash" not in me_body


async def test_register_duplicate_email_returns_409(client):
    resp = await _register(client)
    assert resp.status_code == 201
    resp = await _register(client)
    assert resp.status_code == 409


async def test_login_wrong_password_returns_401(client):
    await _register(client)
    resp = await _login(client, password="totally_wrong")
    assert resp.status_code == 401


async def test_login_unknown_user_returns_401(client):
    resp = await _login(client, email="nobody@email.com")
    assert resp.status_code == 401


async def test_me_without_token_returns_401(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_with_invalid_token_returns_401(client):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401
