from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.db.database import engine, Base
from app.routers import auth, public, student, teacher, admin, reports

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Создаем папки для файлов
for folder in ("uploads/protocols", "uploads/tasks", "uploads/regulations",
               "uploads/certificates", "reports"):
    os.makedirs(folder, exist_ok=True)

app = FastAPI(
    title="Система управления олимпиадным движением",
    description=(
        "REST API для учета участия студентов в олимпиадах и конкурсах "
        "профессионального мастерства. Архитектура MVC (Model-View-Controller). "
        "Аутентификация: нажмите Authorize и введите логин и пароль."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры (View). Префиксы заданы внутри самих роутеров.
app.include_router(auth.router)
app.include_router(public.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(admin.router)
app.include_router(reports.router)


@app.get("/", tags=["Служебные"])
def root():
    """Корневой эндпоинт. Документация доступна по адресу /docs."""
    return {"message": "Система управления олимпиадным движением", "docs": "/docs"}
