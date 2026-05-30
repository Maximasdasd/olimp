from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.db.database import get_db
from app.dependencies.auth import get_current_student

router = APIRouter(tags=["student"])

@router.get("/my-olympiads", response_model=List[schemas.OlympiadResponse])
def get_my_olympiads(
    current_user: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Получение олимпиад, на которые зарегистрирован студент"""
    # Здесь будет логика получения олимпиад студента
    return []

@router.post("/register/{olympiad_id}")
def register_for_olympiad(
    olympiad_id: int,
    current_user: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Регистрация на олимпиаду"""
    # Проверяем, существует ли олимпиада
    olympiad = db.query(models.Olympiad).filter(models.Olympiad.id == olympiad_id).first()
    if not olympiad:
        raise HTTPException(status_code=404, detail="Олимпиада не найдена")
    
    # Проверяем, не зарегистрирован ли уже
    existing = db.query(models.Registration).filter(
        models.Registration.olympiad_id == olympiad_id,
        models.Registration.student_id == current_user.student_profile.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже зарегистрированы на эту олимпиаду")
    
    # Создаем регистрацию
    registration = models.Registration(
        olympiad_id=olympiad_id,
        student_id=current_user.student_profile.id
    )
    
    db.add(registration)
    db.commit()
    
    return {"message": "Вы успешно зарегистрировались на олимпиаду"}

@router.get("/my-results")
def get_my_results(
    current_user: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Получение результатов студента"""
    results = db.query(models.ProtocolResult).filter(
        models.ProtocolResult.student_id == current_user.student_profile.id
    ).all()
    
    return results

@router.put("/profile")
def update_profile(
    profile_data: dict,
    current_user: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Редактирование профиля студента"""
    student = current_user.student_profile
    for key, value in profile_data.items():
        setattr(student, key, value)
    
    db.commit()
    return {"message": "Профиль обновлен"}