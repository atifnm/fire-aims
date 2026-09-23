def test_login_success(client):
    res = client.post("/api/auth/login", data={"username": "admin@example.com", "password": "TestPass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", data={"username": "admin@example.com", "password": "wrong"})
    assert res.status_code == 401


def test_me_requires_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_with_token(client, admin_headers):
    res = client.get("/api/auth/me", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "admin@example.com"


def test_inspector_cannot_create_asset(client, inspector_headers):
    res = client.post("/api/assets", json={"asset_type": "extinguisher"}, headers=inspector_headers)
    assert res.status_code == 403


def test_inspector_cannot_create_user(client, inspector_headers):
    res = client.post("/api/users", json={
        "employee_code": "X-1", "full_name": "X", "email": "x@example.com", "password": "abc123"
    }, headers=inspector_headers)
    assert res.status_code == 403
