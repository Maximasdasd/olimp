from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas
from app.db.database import get_db
from app import models

router = APIRouter(tags=["public"])

@router.get("/olympiads", response_model=List[schemas.OlympiadPublic])
def get_olympiads(
    skip: int = 0,
    limit: int = 100,
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Получение списка всех олимпиад (доступно без авторизации)"""
    query = db.query(models.Olympiad).filter(models.Olympiad.is_protocol_published == True)
    
    if year:
        query = query.filter(models.Olympiad.year == year)
    
    olympiads = query.offset(skip).limit(limit).all()
    return olympiads

@router.get("/olympiads/{olympiad_id}", response_model=schemas.OlympiadPublic)
def get_olympiad(olympiad_id: int, db: Session = Depends(get_db)):
    """Получение информации об олимпиаде"""
    olympiad = db.query(models.Olympiad).filter(
        models.Olympiad.id == olympiad_id,
        models.Olympiad.is_protocol_published == True
    ).first()
    
    if not olympiad:
        raise HTTPException(status_code=404, detail="Олимпиада не найдена или не опубликована")
    
    return olympiad

@router.get("/olympiads/{olympiad_id}/protocol")
def get_protocol(olympiad_id: int, db: Session = Depends(get_db)):
    """Получение протокола олимпиады"""
    olympiad = db.query(models.Olympiad).filter(
        models.Olympiad.id == olympiad_id,
        models.Olympiad.is_protocol_published == True
    ).first()
    
    if not olympiad or not olympiad.protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден или не опубликован")
    
    return {
        "message": "Протокол олимпиады", 
        "file_path": olympiad.protocol.file_path,
        "olympiad_title": olympiad.title,
        "year": olympiad.year
    }

@router.get("/olympiads/{olympiad_id}/tasks")
def get_tasks(olympiad_id: int, db: Session = Depends(get_db)):
    """Получение заданий прошлых лет"""
    tasks = db.query(models.Task).filter(models.Task.olympiad_id == olympiad_id).all()
    return tasks

