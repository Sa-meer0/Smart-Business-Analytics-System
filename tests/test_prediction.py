import os


def login(client):
    """Helper function for login."""

    return client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin123"
        },
        follow_redirects=True
    )


# ==========================================================
# Prediction Page Tests
# ==========================================================

def test_prediction_requires_login(client):
    """Prediction page should require login."""

    response = client.get("/prediction/")

    assert response.status_code == 302
    assert response.location.endswith("/")


def test_prediction_page_loads(client):
    """Prediction page should load after login."""

    login(client)

    response = client.get("/prediction/")

    assert response.status_code == 200


# ==========================================================
# Sales Prediction Tests
# ==========================================================

def test_sales_prediction_valid(client):
    """Sales prediction with valid input."""

    login(client)

    response = client.post(
        "/prediction/sales",
        data={
            "product_category": "Electronic accessories",
            "product_name": "Wireless Mouse",
            "city": "Kathmandu",
            "unit_price": "500",
            "month": "6"
        },
        follow_redirects=True
    )

    assert response.status_code == 200


def test_sales_prediction_missing_price(client):
    """Prediction should handle missing price."""

    login(client)

    response = client.post(
        "/prediction/sales",
        data={
            "product_category": "Electronic accessories",
            "product_name": "Wireless Mouse",
            "city": "Kathmandu",
            "unit_price": "",
            "month": "6"
        },
        follow_redirects=True
    )

    assert response.status_code == 200


def test_sales_prediction_invalid_month(client):
    """Prediction should handle invalid month."""

    login(client)

    response = client.post(
        "/prediction/sales",
        data={
            "product_category": "Electronic accessories",
            "product_name": "Wireless Mouse",
            "city": "Kathmandu",
            "unit_price": "500",
            "month": "15"
        },
        follow_redirects=True
    )

    assert response.status_code == 200


# ==========================================================
# Customer Segmentation Tests
# ==========================================================

def test_customer_segmentation_page(client):
    """Customer segmentation page should load."""

    login(client)

    response = client.get("/prediction/customers")

    assert response.status_code == 200


def test_customer_segmentation_filter(client):
    """Filtering customers by segment."""

    login(client)

    response = client.post(
        "/prediction/customers",
        data={
            "segment": "High Value"
        },
        follow_redirects=True
    )

    assert response.status_code == 200


# ==========================================================
# Model File Tests
# ==========================================================

def test_linear_model_exists():
    """Linear Regression model exists."""

    assert os.path.exists(
        "trained_models/linear_weights.npy"
    )


def test_logistic_model_exists():
    """Logistic Regression model exists."""

    assert os.path.exists(
        "trained_models/logistic_weights.npy"
    )


# ==========================================================
# Dataset Tests
# ==========================================================

def test_dataset_exists():
    """Dataset folder exists."""

    assert os.path.exists("dataset")


def test_dataset_has_csv():
    """Dataset contains at least one CSV."""

    csvs = [
        f for f in os.listdir("dataset")
        if f.endswith(".csv")
    ]

    assert len(csvs) > 0


# ==========================================================
# Session Persistence
# ==========================================================

def test_prediction_session(client):
    """Session should persist across prediction pages."""

    login(client)

    response1 = client.get("/prediction/")
    response2 = client.get("/prediction/")

    assert response1.status_code == 200
    assert response2.status_code == 200
