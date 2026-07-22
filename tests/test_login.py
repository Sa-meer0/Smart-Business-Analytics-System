import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_login_page_loads(client):
    """Test that login page loads successfully."""
    response = client.get("/")

    assert response.status_code == 200


def test_login_empty_fields(client):
    """Test login with empty username and password."""
    response = client.post(
        "/",
        data={
            "username": "",
            "password": ""
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Please enter both username and password" in response.data


def test_invalid_login(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/",
        data={
            "username": "admin",
            "password": "wrongpassword"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_valid_login(client):
    """Test login with valid credentials."""
    response = client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_logout(client):
    """Test logout functionality."""

    # Login first
    client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    # Logout
    response = client.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"You have been logged out" in response.data
