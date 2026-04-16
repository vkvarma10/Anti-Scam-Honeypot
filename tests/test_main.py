import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_chat_endpoint_validation():
    # Test missing payload
    response = client.post("/api/chat", json={})
    assert response.status_code == 422 # Unprocessable Entity

def test_chat_endpoint_mock():
    # If the database and models are mocked, we can test deeply.
    # We do a basic integration test.
    payload = {"session_id": "test_session_123", "message": "hello my bank account is 123456789"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    
def test_reset_session():
    response = client.delete("/api/reset/test_session_123")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Session cleared"}
