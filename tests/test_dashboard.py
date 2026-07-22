import pytest


# ======================================================
# Dashboard Tests
# ======================================================

def login(client):
    """Helper function to login."""
    return client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )


def test_dashboard_requires_login(client):
    """Dashboard should redirect if user is not logged in."""

    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/" in response.location


def test_dashboard_loads_after_login(client):
    """Dashboard should open after successful login."""

    login(client)

    response = client.get("/dashboard")

    assert response.status_code == 200


def test_dashboard_contains_expected_content(client):
    """Dashboard page should contain expected text."""

    login(client)

    response = client.get("/dashboard")

    assert response.status_code == 200

    # Adjust these if your dashboard uses different text
    assert (
        b"Dashboard" in response.data
        or b"Sales" in response.data
        or b"Analytics" in response.data
    )


def test_dashboard_multiple_requests(client):
    """Dashboard should remain accessible across multiple requests."""

    login(client)

    for _ in range(3):
        response = client.get("/dashboard")
        assert response.status_code == 200


def test_dashboard_session_persistence(client):
    """Logged-in user should remain authenticated."""

    login(client)

    response = client.get("/dashboard")
    assert response.status_code == 200

    response = client.get("/dashboard")
    assert response.status_code == 200


def test_dashboard_after_logout(client):
    """Dashboard should not be accessible after logout."""

    login(client)

    client.get("/logout", follow_redirects=True)

    response = client.get("/dashboard")

    assert response.status_code == 302
