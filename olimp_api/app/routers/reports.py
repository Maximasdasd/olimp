from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_teacher
from app.models.user import User
from app.controllers import report as controller_report

router = APIRouter(prefix="/api/reports", tags=["Отчеты"])


@router.get("/protocols/{protocol_id}/word")
def generate_protocol_word(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    """Генерация протокола олимпиады."""
    return controller_report.generate_protocol_report(db, protocol_id)


@router.get("/annual-report/{year}/excel")
def generate_annual_report(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    """Генерация годового отчета."""
    return controller_report.generate_annual_report(db, year)
