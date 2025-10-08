"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_agent_get_endpoint():
    """Test the GET /agent endpoint."""
    response = client.get("/agent")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "it's alive"
    assert data["status"] == "healthy"
    assert data["agent_type"] == "python-fastapi"


def test_agent_post_endpoint():
    """Test the POST /agent endpoint."""
    request_data = {
        "message": "Hello, agent!",
        "conversation_id": "test-123",
        "metadata": {"test": True},
    }

    response = client.post("/agent", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "it's alive"
    assert data["status"] == "healthy"
    assert data["agent_type"] == "python-fastapi"
    assert data["conversation_id"] == "test-123"


def test_agent_post_minimal():
    """Test the POST /agent endpoint with minimal data."""
    request_data = {"message": "Test message"}

    response = client.post("/agent", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "it's alive"
    assert data["status"] == "healthy"


def test_agent_post_missing_message():
    """Test the POST /agent endpoint without required message field."""
    request_data = {}

    response = client.post("/agent", json=request_data)
    assert response.status_code == 422  # Validation error
