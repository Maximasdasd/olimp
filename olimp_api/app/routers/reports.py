from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from datetime import datetime

from app.db.database import get_db
from app.dependencies.auth import get_current_admin, get_current_teacher
from app.models import Protocol, ProtocolResult, Olympiad

router = APIRouter(tags=["reports"])

@router.get("/protocols/{protocol_id}/word")
def generate_protocol_word(
    protocol_id: int,
    current_user = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Генерация протокола в формате Word (заглушка)"""
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Протокол не найден")
    
    # Создаем простой текстовый файл для примера
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"protocol_{protocol_id}.txt"
    output_path = os.path.join(output_dir, filename)
    
    # Простой текстовый отчет
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"ПРОТОКОЛ ОЛИМПИАДЫ\n")
        f.write(f"===================\n")
        f.write(f"Олимпиада: {protocol.olympiad.title}\n")
        f.write(f"Дата: {protocol.olympiad.start_date}\n")
        f.write(f"Статус: {protocol.status}\n")
        f.write(f"\nСгенерировано: {datetime.now()}\n")
    
    return FileResponse(
        output_path,
        media_type='text/plain',
        filename=f"Протокол_{protocol.olympiad.title}.txt"
    )

@router.get("/annual-report/{year}/excel")
def generate_annual_report(
    year: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Генерация годового отчета в Excel (заглушка)"""
    # Создаем простой текстовый файл для примера
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"annual_report_{year}.txt"
    output_path = os.path.join(output_dir, filename)
    
    # Простой текстовый отчет
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"ГОДОВОЙ ОТЧЕТ {year} ГОДА\n")
        f.write(f"========================\n")
        f.write(f"\nСгенерировано: {datetime.now()}\n")
        f.write(f"Пользователь: {current_user.username}\n")
    
    return FileResponse(
        output_path,
        media_type='text/plain',
        filename=f"Годовой_отчет_{year}.txt"
    )