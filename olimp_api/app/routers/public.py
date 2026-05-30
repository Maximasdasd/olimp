from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.olympiad import OlympiadResponse
from app.schemas.protocol import ProtocolResponse
from app.controllers import olympiad as controller_olympiad
from app.controllers import protocol as controller_protocol

router = APIRouter(prefix="/api", tags=["Публичные"])


@router.get("/olympiads", response_model=List[OlympiadResponse])
def get_olympiads(
    year: Optional[int] = Query(None, description="Фильтр по году"),
    db: Session = Depends(get_db),
):
    """Просмотр списка всех олимпиад (доступно всем)."""
    return controller_olympiad.get_olympiads(db, year=year)


@router.get("/olympiads/{olympiad_id}", response_model=OlympiadResponse)
def get_olympiad(olympiad_id: int, db: Session = Depends(get_db)):
    """Просмотр информации об олимпиаде."""
    return controller_olympiad.get_olympiad(db, olympiad_id)


@router.get("/olympiads/{olympiad_id}/protocol", response_model=ProtocolResponse)
def get_olympiad_protocol(olympiad_id: int, db: Session = Depends(get_db)):
    """Просмотр протокола победителей (только опубликованные)."""
    return controller_protocol.get_published_protocol(db, olympiad_id)


@router.get("/olympiads/{olympiad_id}/tasks")
def get_olympiad_tasks(olympiad_id: int, db: Session = Depends(get_db)):
    """Просмотр заданий прошлых лет."""
    return controller_olympiad.get_tasks(db, olympiad_id)


@router.get("/olympiads/{olympiad_id}/regulation")
def get_regulation(olympiad_id: int, db: Session = Depends(get_db)):
    """Просмотр положения по олимпиаде."""
    return controller_olympiad.get_regulation(db, olympiad_id)
