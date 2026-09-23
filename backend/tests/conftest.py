import os
import sys
import tempfile

# Point the app at an isolated temp SQLite DB before any app modules are imported.
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["SECRET_KEY"] = "test-secret-key"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(User(employee_code="ADM-TEST", full_name="Test Admin", email="admin@example.com",
                role=UserRole.ADMIN, hashed_password=hash_password("TestPass123")))
    db.add(User(employee_code="INS-TEST", full_name="Test Inspector", email="inspector@example.com",
                role=UserRole.INSPECTOR, hashed_password=hash_password("TestPass123")))
    db.add(User(employee_code="SUP-TEST", full_name="Test Supervisor", email="supervisor@example.com",
                role=UserRole.SUPERVISOR, hashed_password=hash_password("TestPass123")))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def get_token(client, email="admin@example.com", password="TestPass123"):
    res = client.post("/api/auth/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture
def admin_headers(client):
    token = get_token(client)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def inspector_headers(client):
    token = get_token(client, "inspector@example.com", "TestPass123")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def supervisor_headers(client):
    token = get_token(client, "supervisor@example.com", "TestPass123")
    return {"Authorization": f"Bearer {token}"}
