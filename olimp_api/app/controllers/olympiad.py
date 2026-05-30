"""Контроллер олимпиад.

Бизнес-логика и работа с БД для олимпиад, заданий и положений.
"""
import os
import shutil
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile

from app.models.olympiad import Olympiad
from app.models.task import Task
from app.schemas.olympiad import OlympiadCreate

REGULATIONS_DIR = "uploads/regulations"


def get_olympiads(db: Session, year: Optional[int] = None):
    """Список всех олимпиад с необязательным фильтром по году."""
    query = db.query(Olympiad)
    if year:
        query = query.filter(Olympiad.year == year)
    return query.all()


def get_olympiad(db: Session, olympiad_id: int) -> Olympiad:
    """Получить олимпиаду по id или вернуть 404."""
    olympiad = db.query(Olympiad).filter(Olympiad.id == olympiad_id).first()
    if not olympiad:
        raise HTTPException(status_code=404, detail="Олимпиада не найдена")
    return olympiad


def get_tasks(db: Session, olympiad_id: int):
    """Задания прошлых лет по олимпиаде."""
    return db.query(Task).filter(Task.olympiad_id == olympiad_id).all()


def get_regulation(db: Session, olympiad_id: int) -> dict:
    """Путь к файлу положения по олимпиаде."""
    olympiad = db.query(Olympiad).filter(Olympiad.id == olympiad_id).first()
    if not olympiad or not olympiad.regulation_file:
        raise HTTPException(status_code=404, detail="Положение не найдено")
    return {"file_path": olympiad.regulation_file}


def create_olympiad(db: Session, olympiad_data: OlympiadCreate, creator_id: int) -> Olympiad:
    """Создание карточки олимпиады администратором."""
    olympiad = Olympiad(**olympiad_data.dict(), creator_id=creator_id)
    db.add(olympiad)
    db.commit()
    db.refresh(olympiad)
    return olympiad


def upload_regulation(db: Session, olympiad_id: int, file: UploadFile) -> dict:
    """Загрузка и прикрепление файла положения к олимпиаде."""
    olympiad = get_olympiad(db, olympiad_id)

    os.makedirs(REGULATIONS_DIR, exist_ok=True)
    file_path = os.path.join(REGULATIONS_DIR, f"regulation_{olympiad_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    olympiad.regulation_file = file_path
    db.commit()
    return {"message": "Положение загружено", "file_path": file_path}
