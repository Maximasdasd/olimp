import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Пути для файлов
    UPLOAD_FOLDER = "uploads"
    PROTOCOLS_FOLDER = "uploads/protocols"
    TASKS_FOLDER = "uploads/tasks"
    REGULATIONS_FOLDER = "uploads/regulations"
    CERTIFICATES_FOLDER = "uploads/certificates"

settings = Settings()