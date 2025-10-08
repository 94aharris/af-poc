"""Tests for orchestrator API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "orchestrator"


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Microsoft Agent Framework Orchestrator"
    assert "endpoints" in data


def test_orchestrator_status():
    """Test the GET /agent endpoint."""
    response = client.get("/agent")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Orchestrator is alive"
    assert data["status"] == "healthy"
    assert data["service"] == "orchestrator"


def test_orchestrator_post_auto_select():
    """Test the POST /agent endpoint with auto agent selection."""
    request_data = {
        "message": "Help me with Python data analysis",
        "conversation_id": "test-123",
        "preferred_agent": "auto",
    }

    response = client.post("/agent", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "selected_agent" in data
    assert len(data["sub_agent_responses"]) > 0


def test_orchestrator_post_python_preference():
    """Test the POST /agent endpoint with Python preference."""
    request_data = {"message": "Test message", "preferred_agent": "python"}

    response = client.post("/agent", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["selected_agent"] == "python"


def test_orchestrator_post_dotnet_preference():
    """Test the POST /agent endpoint with .NET preference."""
    request_data = {"message": "Test message", "preferred_agent": "dotnet"}

    response = client.post("/agent", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["selected_agent"] == "dotnet"
