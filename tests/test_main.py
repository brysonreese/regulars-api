from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home_returns_welcome_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Regulars API is running!"}


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
