"""
API Tests

Tests to verify that the endpoints work correctly.

TestClient simulates HTTP requests without actually starting a server.
"""

from fastapi.testclient import TestClient
from app.main import app

# Create test client
# This lets us make requests to the app without running a server
client = TestClient(app)


def test_root_endpoint():
    """
    Test the root endpoint (/)

    This sends a GET request and checks the response
    """
    response = client.get("/")

    # Check status code (200 = success)
    assert response.status_code == 200

    # Check response contains expected data
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Object Detection API"


def test_health_endpoint():
    """
    Test the health check endpoint

    This verifies the API can report its status
    """
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "version" in data


def test_predict_without_file():
    """
    Test that predict fails gracefully without a file

    This should return 422 (Unprocessable Entity) because
    the 'file' parameter is required
    """
    response = client.post("/predict")

    # Should fail with validation error
    assert response.status_code == 422


def test_predict_with_invalid_file():
    """
    Test that predict rejects non-image files

    This verifies our file type validation works

    Note: Model might not be loaded in test environment,
    so we accept either 400 (validation error) or 503 (model not loaded)
    """
    # Send a text file instead of an image
    response = client.post(
        "/predict", files={"file": ("test.txt", b"not an image", "text/plain")}
    )

    # Should reject - either validation error or service unavailable
    assert response.status_code in [400, 503]


# To run these tests:
# 1. Make sure you're in the project root directory
# 2. Activate virtual environment: source venv/bin/activate
# 3. Run: pytest tests/test_api.py -v
#
# The -v flag shows verbose output (more details)