import os
from datetime import timedelta


class Config:
    """
    Application Configuration
    """

    # ============================================
    # Flask Configuration
    # ============================================

    SECRET_KEY = "SBAS_SECRET_KEY_2026_CHANGE_ME"

    DEBUG = True

    # Session Configuration - Enhanced for Persistence
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    
    # Additional session settings for better reliability
    SESSION_COOKIE_NAME = "sbas_session"
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_USE_SIGNER = True

    # ============================================
    # MySQL Database Configuration
    # ============================================

    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_NAME = "smart_business"
    DB_USER = "root"
    DB_PASSWORD = ""

    # ============================================
    # Project Paths
    # ============================================

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATASET_FOLDER = os.path.join(BASE_DIR, "dataset")
    MODEL_FOLDER = os.path.join(BASE_DIR, "trained_models")
    STATIC_FOLDER = os.path.join(BASE_DIR, "static")
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")

    # ============================================
    # ML Models
    # ============================================

    LINEAR_MODEL = os.path.join(MODEL_FOLDER, "linear_weights.npy")
    LOGISTIC_MODEL = os.path.join(MODEL_FOLDER, "logistic_weights.npy")

    # ============================================
    # Reports
    # ============================================

    REPORT_FOLDER = os.path.join(BASE_DIR, "reports")