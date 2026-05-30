from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.db.database import get_db
from app.dependencies.auth import get_current_admin

router = APIRouter(tags=["admin"])

@router.post("/teachers", response_model=schemas.TeacherResponse)
def create_teacher(
    teacher_data: schemas.TeacherCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Создание учетной записи преподавателя"""
    from app.utils.security import get_password_hash
    from app.crud.user import get_user_by_email, get_user_by_username
    
    # Проверяем, существует ли пользователь
    if get_user_by_email(db, email=teacher_data.user.email):
        raise HTTPException(status_code=400, detail="Email уже используется")
    
    if get_user_by_username(db, username=teacher_data.user.username):
        raise HTTPException(status_code=400, detail="Имя пользователя уже используется")
    
    # Создаем пользователя
    user = models.User(
        email=teacher_data.user.email,
        username=teacher_data.user.username,
        hashed_password=get_password_hash(teacher_data.user.password),
        full_name=teacher_data.user.full_name,
        role=models.UserRole.TEACHER,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Создаем профиль преподавателя
    teacher = models.Teacher(
        user_id=user.id,
        department=teacher_data.department,
        position=teacher_data.position,
        academic_degree=teacher_data.academic_degree
    )
    
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return teacher

@router.post("/olympiads", response_model=schemas.OlympiadResponse)
def create_olympiad(
    olympiad_data: schemas.OlympiadCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Создание карточки олимпиады"""
    olympiad = models.Olympiad(
        title=olympiad_data.title,
        description=olympiad_data.description,
        year=olympiad_data.year,
        start_date=olympiad_data.start_date,
        end_date=olympiad_data.end_date,
        registration_deadline=olympiad_data.registration_deadline,
        location=olympiad_data.location,
        level=olympiad_data.level,
        status=olympiad_data.status,
        teacher_id=olympiad_data.teacher_id,
        creator_id=current_user.id
    )
    
    db.add(olympiad)
    db.commit()
    db.refresh(olympiad)
    
    return olympiad

@router.get("/protocols", response_model=List[schemas.ProtocolResponse])
def get_protocols(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Просмотр протоколов"""
    protocols = db.query(models.Protocol).offset(skip).limit(limit).all()
    return protocols

@router.put("/protocols/{protocol_id}/publish")
def publish_protocol(
    protocol_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Публикация протокола"""
    protocol = db.query(models.Protocol).filter(models.Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден")
    
    if protocol.status != "prepared":
        raise HTTPException(status_code=400, detail="Протокол должен быть в статусе 'подготовлен'")
    
    protocol.status = "published"
    protocol.olympiad.is_protocol_published = True
    db.commit()
    
    return {"message": "Протокол опубликован"}