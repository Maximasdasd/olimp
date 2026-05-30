"""Контроллер протоколов.

Бизнес-логика создания протоколов, добавления результатов,
смены статуса и публикации.

Статусы протокола:
    draft     - формируется
    prepared  - подготовлен
    published - опубликован
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.teacher import Teacher
from app.models.olympiad import Olympiad
from app.models.protocol import Protocol, ProtocolResult
from app.schemas.protocol import (
    ProtocolCreate,
    ProtocolResultCreate,
    ProtocolStatusUpdate,
)

STATUS_DRAFT = "draft"
STATUS_PREPARED = "prepared"
STATUS_PUBLISHED = "published"


def get_published_protocol(db: Session, olympiad_id: int) -> Protocol:
    """Опубликованный протокол олимпиады (для публичного просмотра)."""
    protocol = db.query(Protocol).filter(
        Protocol.olympiad_id == olympiad_id,
        Protocol.status == STATUS_PUBLISHED,
    ).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден или не опубликован")
    return protocol


def get_protocol(db: Session, protocol_id: int) -> Protocol:
    """Получить протокол по id или вернуть 404."""
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден")
    return protocol


def get_all_protocols(db: Session):
    """Все протоколы (для администратора)."""
    return db.query(Protocol).all()


def create_protocol(db: Session, user_id: int, protocol_data: ProtocolCreate) -> Protocol:
    """Создание протокола преподавателем."""
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Профиль преподавателя не найден")

    olympiad = db.query(Olympiad).filter(Olympiad.id == protocol_data.olympiad_id).first()
    if not olympiad:
        raise HTTPException(status_code=404, detail="Олимпиада не найдена")

    existing = db.query(Protocol).filter(Protocol.olympiad_id == protocol_data.olympiad_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Протокол для этой олимпиады уже существует")

    protocol = Protocol(
        olympiad_id=protocol_data.olympiad_id,
        teacher_id=teacher.id,
        status=STATUS_DRAFT,
    )
    db.add(protocol)
    db.commit()
    db.refresh(protocol)
    return protocol


def add_result(db: Session, protocol_id: int, result_data: ProtocolResultCreate) -> ProtocolResult:
    """Добавление результата участника в протокол."""
    get_protocol(db, protocol_id)
    result = ProtocolResult(
        protocol_id=protocol_id,
        student_id=result_data.student_id,
        score=result_data.score,
        place=result_data.place,
        result_type=result_data.result_type,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def update_status(db: Session, protocol_id: int, status_data: ProtocolStatusUpdate) -> Protocol:
    """Смена статуса протокола (формируется/подготовлен)."""
    protocol = get_protocol(db, protocol_id)
    protocol.status = status_data.status
    db.commit()
    db.refresh(protocol)
    return protocol


def publish_protocol(db: Session, protocol_id: int) -> Protocol:
    """Публикация подготовленного протокола администратором."""
    protocol = get_protocol(db, protocol_id)
    if protocol.status != STATUS_PREPARED:
        raise HTTPException(
            status_code=400,
            detail="Опубликовать можно только подготовленный протокол (статус 'prepared')",
        )
    protocol.status = STATUS_PUBLISHED
    protocol.olympiad.is_protocol_published = True
    db.commit()
    db.refresh(protocol)
    return protocol
