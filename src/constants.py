import os

from dotenv import load_dotenv

load_dotenv()

# Meta
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "change-me")
MIGRATE_DATABASE_URL = os.getenv("MIGRATE_DATABASE_URL", "change-me")
