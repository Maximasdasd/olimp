import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # По умолчанию используется SQLite, чтобы проект запускался без настройки БД.
    # Для PostgreSQL задайте переменную окружения DATABASE_URL.
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./olimp.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Пути для файлов
    UPLOAD_FOLDER = "uploads"
    PROTOCOLS_FOLDER = "uploads/protocols"
    TASKS_FOLDER = "uploads/tasks"
    REGULATIONS_FOLDER = "uploads/regulations"
    CERTIFICATES_FOLDER = "uploads/certificates"


settings = Settings()
