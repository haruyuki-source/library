import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "library-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-library-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    # Default: SQLite; override via env for MySQL etc.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{os.path.join(BASE_DIR, 'library.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS
    CORS_RESOURCES = {r"/api/*": {"origins": "*"}}

    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
