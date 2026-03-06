import pytest
from fastapi.testclient import TestClient
from jose import jwt
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from main import app
from core.settings import Settings
from tools import user_uuid

settings = Settings()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_client(client):
    token = jwt.encode({"user_id": user_uuid}, settings.secret_key,
                      algorithm=settings.algorithm)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client