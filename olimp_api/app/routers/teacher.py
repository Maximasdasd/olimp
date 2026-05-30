from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

from app import schemas, models
from app.db.database import get_db
from app.dependencies.auth import get_current_teacher
from app.utils.config import settings

router = APIRouter(tags=["teacher"])

@router.post("/students")
def create_student(
    student_data: schemas.StudentCreate,
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Создание учетной записи студента"""
    # Создаем пользователя студента
    from app.utils.security import get_password_hash
    
    user_data = student_data.user
    db_user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=models.UserRole.STUDENT,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем профиль студента
    student = models.Student(
        user_id=db_user.id,
        birth_date=student_data.birth_date,
        phone=student_data.phone,
        institution=student_data.institution,
        education_level=student_data.education_level,
        course=student_data.course,
        specialty=student_data.specialty
    )
    
    db.add(student)
    db.commit()
    
    return {"message": "Студент создан", "student_id": student.id}

@router.post("/olympiads/{olympiad_id}/regulation")
async def upload_regulation(
    olympiad_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Загрузка положения об олимпиаде"""
    olympiad = db.query(models.Olympiad).filter(models.Olympiad.id == olympiad_id).first()
    if not olympiad:
        raise HTTPException(status_code=404, detail="Олимпиада не найдена")
    
    # Сохраняем файл
    file_path = os.path.join(settings.REGULATIONS_FOLDER, f"regulation_{olympiad_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Обновляем запись в БД
    olympiad.regulation_file = file_path
    db.commit()
    
    return {"message": "Положение загружено", "file_path": file_path}

@router.post("/protocols")
def create_protocol(
    protocol_data: schemas.ProtocolCreate,
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Создание протокола олимпиады"""
    protocol = models.Protocol(
        olympiad_id=protocol_data.olympiad_id,
        teacher_id=current_user.teacher_profile.id,
        status=protocol_data.status
    )
    
    db.add(protocol)
    db.commit()
    
    return {"message": "Протокол создан", "protocol_id": protocol.id}

@router.post("/protocols/{protocol_id}/results")
def add_protocol_result(
    protocol_id: int,
    result_data: schemas.ProtocolResultBase,
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Добавление результата в протокол"""
    protocol = db.query(models.Protocol).filter(models.Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден")
    
    result = models.ProtocolResult(
        protocol_id=protocol_id,
        student_id=result_data.student_id,
        score=result_data.score,
        place=result_data.place,
        result_type=result_data.result_type
    )
    
    db.add(result)
    db.commit()
    
    return {"message": "Результат добавлен", "result_id": result.id}

@router.put("/protocols/{protocol_id}/status")
def update_protocol_status(
    protocol_id: int,
    status_data: dict,
    current_user: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Изменение статуса протокола"""
    protocol = db.query(models.Protocol).filter(models.Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден")
    
    protocol.status = status_data.get("status", protocol.status)
    db.commit()
    
    return {"message": "Статус протокола обновлен", "status": protocol.status}