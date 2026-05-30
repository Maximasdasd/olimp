from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.schemas.user import TeacherCreate, TeacherResponse
from app.schemas.olympiad import OlympiadCreate, OlympiadResponse
from app.schemas.protocol import ProtocolResponse
from app.controllers import teacher as controller_teacher
from app.controllers import olympiad as controller_olympiad
from app.controllers import protocol as controller_protocol

router = APIRouter(prefix="/api/admin", tags=["Администратор"])


@router.post("/teachers", response_model=TeacherResponse)
def create_teacher(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Создание учетной записи преподавателя."""
    return controller_teacher.create_teacher(db, teacher_data)


@router.post("/olympiads", response_model=OlympiadResponse)
def create_olympiad(
    olympiad_data: OlympiadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Создание олимпиады."""
    return controller_olympiad.create_olympiad(db, olympiad_data, current_user.id)


@router.get("/protocols", response_model=List[ProtocolResponse])
def get_all_protocols(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Просмотр всех протоколов."""
    return controller_protocol.get_all_protocols(db)


@router.put("/protocols/{protocol_id}/publish", response_model=ProtocolResponse)
def publish_protocol(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Публикация протокола."""
    return controller_protocol.publish_protocol(db, protocol_id)
