from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_teacher
from app.models.user import User
from app.schemas.user import StudentCreate, StudentResponseFull
from app.schemas.protocol import (
    ProtocolCreate,
    ProtocolResponse,
    ProtocolResultCreate,
    ProtocolResultResponse,
    ProtocolStatusUpdate,
)
from app.controllers import student as controller_student
from app.controllers import olympiad as controller_olympiad
from app.controllers import protocol as controller_protocol

router = APIRouter(prefix="/api/teacher", tags=["Преподаватель"])


@router.post("/students", response_model=StudentResponseFull)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    """Создание учетной записи студента."""
    return controller_student.create_student(db, student_data)


@router.post("/olympiads/{olympiad_id}/regulation")
def upload_regulation(
    olympiad_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    """Загрузка положения по олимпиаде."""
    return controller_olympiad.upload_regulation(db, olympiad_id, file)


@router.post("/protocols", response_model=ProtocolResponse)
def create_protocol(
    protocol_data: ProtocolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    """Создание протокола."""
    return controller_protocol.create_protocol(db, current_user.id, protocol_data)


@router.post("/protocols/{protocol_id}/results", response_model=ProtocolResultResponse)
def add_result(
    protocol_id: int,
    result_data: ProtocolResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    """Добавление результата в протокол."""
    return controller_protocol.add_result(db, protocol_id, result_data)


@router.put("/protocols/{protocol_id}/status", response_model=ProtocolResponse)
def update_protocol_status(
    protocol_id: int,
    status_data: ProtocolStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    """Изменение статуса протокола."""
    return controller_protocol.update_status(db, protocol_id, status_data)
