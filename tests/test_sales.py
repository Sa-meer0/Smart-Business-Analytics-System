import pytest


def login(client):
    """Login helper."""

    return client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )


# ==========================================================
# Sales Transaction Tests
# ==========================================================

def test_sales_page_requires_login(client):
    """Sales page should require login."""

    response = client.get("/customer/add")

    assert response.status_code == 302


def test_sales_page_loads(client):
    """Sales page loads after login."""

    login(client)

    response = client.get("/customer/add")

    assert response.status_code == 200


def test_sales_without_product(client):
    """Product selection is required."""

    login(client)

    response = client.post(
        "/customer/add",
        data={
            "customer_name": "Test User",
            "phone": "9800000001",
            "email": "test1@example.com",
            "product_id": "",
            "unit_price": "100",
            "quantity": "2",
            "total": "200"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Please select a product." in response.data


def test_sales_invalid_unit_price(client):
    """Unit price must be greater than zero."""

    login(client)

    response = client.post(
        "/customer/add",
        data={
            "customer_name": "Test User",
            "phone": "9800000002",
            "email": "test2@example.com",
            "product_id": "1",
            "unit_price": "0",
            "quantity": "2",
            "total": "200"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Unit price must be greater than 0!" in response.data


def test_sales_invalid_quantity(client):
    """Quantity must be greater than zero."""

    login(client)

    response = client.post(
        "/customer/add",
        data={
            "customer_name": "Test User",
            "phone": "9800000003",
            "email": "test3@example.com",
            "product_id": "1",
            "unit_price": "100",
            "quantity": "0",
            "total": "0"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Quantity must be greater than 0!" in response.data


def test_sales_invalid_total(client):
    """Total amount must be greater than zero."""

    login(client)

    response = client.post(
        "/customer/add",
        data={
            "customer_name": "Test User",
            "phone": "9800000004",
            "email": "test4@example.com",
            "product_id": "1",
            "unit_price": "100",
            "quantity": "2",
            "total": "0"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Total amount must be greater than 0!" in response.data


def test_sales_valid_transaction(client):
    """
    Valid sales transaction.

    NOTE:
    Requires product_id=1 to exist in the database.
    """

    login(client)

    response = client.post(
        "/customer/add",
        data={
            "customer_name": "Pytest Customer",
            "gender": "Male",
            "customer_type": "Normal",
            "phone": "9811111111",
            "email": "pytest_customer@example.com",
            "product_line": "Electronic accessories",
            "product_id": "1",
            "unit_price": "500",
            "quantity": "2",
            "tax": "20",
            "discount": "10",
            "total": "1010",
            "payment_method": "Cash",
            "branch": "A",
            "city": "Kathmandu",
            "date": "2026-01-01"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert (
        b"Transaction" in response.data
        or b"saved successfully" in response.data
        or b"success" in response.data.lower()
    )


def test_sales_logout_security(client):
    """After logout, sales page should not be accessible."""

    login(client)

    client.get("/logout", follow_redirects=True)

    response = client.get("/customer/add")

    assert response.status_code == 302
