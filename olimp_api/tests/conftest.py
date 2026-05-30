import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, UserRole
from app.utils.security import get_password_hash

# Тестовая БД в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """Фикстура для тестового клиента"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем тестового администратора
    db = TestingSessionLocal()
    admin_user = User(
        email="test_admin@example.com",
        username="test_admin",
        hashed_password=get_password_hash("test123"),
        full_name="Тестовый Админ",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    db.close()
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Удаляем таблицы после тестов
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_token(client):
    """Фикстура для получения токена админа"""
    response = client.post("/api/auth/login", json={
        "username": "test_admin",
        "password": "test123"
    })
    return response.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    """Заголовки с токеном админа"""
    return {"Authorization": f"Bearer {admin_token}"}