from dotenv import load_dotenv
import os

load_dotenv()

# =====================================================
# MongoDB
# =====================================================

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "social_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "posts")

# =====================================================
# PostgreSQL
# =====================================================

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "sports_analytics")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# =====================================================
# Superset
# =====================================================

SUPERSET_SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "secret_key")

SUPERSET_ADMIN_USER = os.getenv("SUPERSET_ADMIN_USER", "admin")
SUPERSET_ADMIN_PASSWORD = os.getenv("SUPERSET_ADMIN_PASSWORD", "admin")
SUPERSET_ADMIN_EMAIL = os.getenv("SUPERSET_ADMIN_EMAIL", "admin@admin.com")
SUPERSET_ADMIN_FIRSTNAME = os.getenv("SUPERSET_ADMIN_FIRSTNAME", "Admin")
SUPERSET_ADMIN_LASTNAME = os.getenv("SUPERSET_ADMIN_LASTNAME", "User")