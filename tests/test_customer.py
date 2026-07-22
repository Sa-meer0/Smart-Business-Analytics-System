import pytest
from routes.add_customer import upgrade_segment


# ======================================================
# Unit Tests for Customer Functions
# ======================================================

def test_upgrade_low_value():
    """Low Value customer should become Medium Value."""
    assert upgrade_segment("Low Value") == "Medium Value"


def test_upgrade_medium_value():
    """Medium Value customer should become High Value."""
    assert upgrade_segment("Medium Value") == "High Value"


def test_upgrade_high_value():
    """High Value customer should remain High Value."""
    assert upgrade_segment("High Value") == "High Value"


# ======================================================
# Customer Route Tests
# ======================================================

def test_customer_page_requires_login(client):
    """Customer page should redirect to login if not logged in."""

    response = client.get("/customer/add")

    assert response.status_code == 302
    assert "/" in response.location


def test_customer_page_after_login(client):
    """Customer page should load after successful login."""

    client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    response = client.get("/customer/add")

    assert response.status_code == 200
    assert b"Customer" in response.data


def test_customer_without_name(client):
    """Customer name is required."""

    client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    response = client.post(
        "/customer/add",
        data={
            "product_id": "4",
            "product_category": "Health & Lifestyle",
            "customer_name": "",
            "phone": "9800000000",
            "email": "abc@test.com",
            "unit_price": "100",
            "quantity": "2",
            "total": "200"
        },
        follow_redirects=True
    )

    assert b"Customer name is required!" in response.data


def test_customer_without_phone(client):
    """Phone number is required."""

    client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    response = client.post(
        "/customer/add",
        data={
            "product_id": "1",
            "product_category": "Electronics Accessories",
            "customer_name": "Ram",
            "phone": "",
            "email": "abc@test.com",
            "unit_price": "100",
            "quantity": "2",
            "total": "200"
        },
        follow_redirects=True
    )

    assert b"Phone number is required!" in response.data


def test_customer_without_email(client):
    """Email is required."""

    client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    response = client.post(
        "/customer/add",
        data={
            "product_id": "2",
            "product_category": "Food & Beverages",
            "customer_name": "Ram",
            "phone": "9800000000",
            "email": "",
            "unit_price": "100",
            "quantity": "2",
            "total": "200"
        },
        follow_redirects=True
    )

    assert b"Email address is required!" in response.data


def test_invalid_email(client):
    """Invalid email should not be accepted."""

    client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    response = client.post(
        "/customer/add",
        data={
            "product_id": "3",
            "product_category": "Fashion Accessories",
            "customer_name": "Ram",
            "phone": "9800000000",
            "email": "invalidemail",
            "unit_price": "100",
            "quantity": "2",
            "total": "200"
        },
        follow_redirects=True
    )

    assert b"Invalid email format!" in response.data


def test_invalid_phone(client):
    """Invalid phone number should not be accepted."""

    client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )

    response = client.post(
        "/customer/add",
        data={
            "product_id": "5",
            "product_category": "Sports & Travel",
            "customer_name": "Ram",
            "phone": "123",
            "email": "abc@test.com",
            "unit_price": "100",
            "quantity": "2",
            "total": "200"
        },
        follow_redirects=True
    )

    assert b"Invalid phone number format!" in response.data
