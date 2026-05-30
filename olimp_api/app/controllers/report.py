"""Контроллер отчётов.

Генерация протокола олимпиады и годового отчёта.
"""
import os

from sqlalchemy.orm import Session

from app.models.protocol import Protocol, ProtocolResult
from app.models.olympiad import Olympiad
from app.controllers import protocol as controller_protocol

REPORTS_DIR = "reports"


def generate_protocol_report(db: Session, protocol_id: int) -> dict:
    """Сформировать файл протокола олимпиады."""
    protocol = controller_protocol.get_protocol(db, protocol_id)
    results = db.query(ProtocolResult).filter(ProtocolResult.protocol_id == protocol_id).all()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    file_path = os.path.join(REPORTS_DIR, f"protocol_{protocol_id}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("ПРОТОКОЛ ОЛИМПИАДЫ\n")
        f.write(f"Олимпиада: {protocol.olympiad.title}\n")
        f.write(f"Дата: {protocol.olympiad.start_date}\n\n")
        f.write("Результаты:\n")
        for r in results:
            f.write(
                f"Студент ID {r.student_id}: {r.score} баллов, "
                f"место {r.place}, {r.result_type}\n"
            )

    return {"message": "Протокол сгенерирован", "file_path": file_path}


def generate_annual_report(db: Session, year: int) -> dict:
    """Сформировать годовой отчёт участия в олимпиадном движении."""
    olympiads = db.query(Olympiad).filter(Olympiad.year == year).all()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    file_path = os.path.join(REPORTS_DIR, f"annual_report_{year}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"ГОДОВОЙ ОТЧЕТ ЗА {year} ГОД\n\n")
        for o in olympiads:
            f.write(f"Олимпиада: {o.title}\n")
            protocol = db.query(Protocol).filter(Protocol.olympiad_id == o.id).first()
            if protocol:
                results = db.query(ProtocolResult).filter(
                    ProtocolResult.protocol_id == protocol.id
                ).all()
                f.write(f"  Участников: {len(results)}\n")
            f.write("\n")

    return {"message": "Годовой отчет сгенерирован", "file_path": file_path}
