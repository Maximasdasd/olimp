from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import os
from app.db.database import engine, Base
from app.routers import auth, public, student, teacher, admin, reports
from app.utils.config import settings

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Создаем папки для файлов
os.makedirs("uploads/protocols", exist_ok=True)
os.makedirs("uploads/tasks", exist_ok=True)
os.makedirs("uploads/regulations", exist_ok=True)
os.makedirs("uploads/certificates", exist_ok=True)
os.makedirs("reports", exist_ok=True)

app = FastAPI(
    title="Система управления олимпиадным движением",
    description="API для учета участия студентов в олимпиадах и конкурсах",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "persistAuthorization": True,  # Сохраняет авторизацию
        "displayRequestDuration": True,
    }
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth")
app.include_router(public.router, prefix="/api")
app.include_router(student.router, prefix="/api/student")
app.include_router(teacher.router, prefix="/api/teacher")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(reports.router, prefix="/api/reports")