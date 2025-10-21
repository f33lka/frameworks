import os, pytest
from app import create_app
from models import User

@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["SECRET_KEY"] = "test"
    os.environ["JWT_SECRET_KEY"] = "test"
    app = create_app()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def token(client, email="admin@example.com", password="admin123"):
    code, data = j(client.post("/api/auth/login", json={"email": email, "password": password}))
    assert code == 200
    return data["access_token"]

def j(resp):
    return resp.status_code, (resp.get_json() or {})
