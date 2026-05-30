import pytest
from datetime import date

def test_get_olympiads_empty(client):
    """Тест получения пустого списка олимпиад"""
    response = client.get("/api/olympiads")
    
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_get_olympiad(client, admin_headers):
    """Тест создания и получения олимпиады"""
    # Создаем олимпиаду
    create_response = client.post("/api/admin/olympiads", json={
        "title": "Тестовая Олимпиада 2024",
        "description": "Описание тестовой олимпиады",
        "year": 2024,
        "start_date": "2024-12-20",
        "end_date": "2024-12-21",
        "level": "региональный",
        "status": "planned",
        "teacher_id": 1
    }, headers=admin_headers)
    
    assert create_response.status_code == 200
    olympiad_id = create_response.json()["id"]
    
    # Получаем список олимпиад
    response = client.get("/api/olympiads")
    
    assert response.status_code == 200
    olympiads = response.json()
    assert len(olympiads) == 1
    assert olympiads[0]["title"] == "Тестовая Олимпиада 2024"
    assert olympiads[0]["year"] == 2024

def test_filter_olympiads_by_year(client, admin_headers):
    """Тест фильтрации олимпиад по году"""
    # Создаем олимпиады разных годов
    for year in [2023, 2024, 2024, 2025]:
        client.post("/api/admin/olympiads", json={
            "title": f"Олимпиада {year}",
            "year": year,
            "start_date": f"{year}-12-20",
            "end_date": f"{year}-12-21",
            "level": "региональный",
            "status": "planned",
            "teacher_id": 1
        }, headers=admin_headers)
    
    # Фильтруем по 2024 году
    response = client.get("/api/olympiads?year=2024")
    
    assert response.status_code == 200
    olympiads = response.json()
    assert len(olympiads) == 2
    assert all(olympiad["year"] == 2024 for olympiad in olympiads)

def test_get_nonexistent_olympiad(client):
    """Тест получения несуществующей олимпиады"""
    response = client.get("/api/olympiads/999")
    
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"].lower()