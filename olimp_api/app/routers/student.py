from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.dependencies.auth import get_current_student
from app.models.user import User
from app.schemas.olympiad import RegistrationResponse
from app.schemas.user import StudentProfileUpdate, StudentResponse
from app.controllers import student as controller_student

router = APIRouter(prefix="/api/student", tags=["Студент"])


@router.post("/register/{olympiad_id}", response_model=RegistrationResponse)
def register_for_olympiad(
    olympiad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """Записаться на олимпиаду."""
    return controller_student.register_for_olympiad(db, current_user.id, olympiad_id)


@router.get("/my-olympiads", response_model=List[RegistrationResponse])
def get_my_olympiads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """Просмотр своих олимпиад."""
    return controller_student.get_my_olympiads(db, current_user.id)


@router.get("/my-results")
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """Просмотр своих результатов."""
    return controller_student.get_my_results(db, current_user.id)


@router.put("/profile", response_model=StudentResponse)
def update_profile(
    profile_data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """Редактирование своего профиля."""
    return controller_student.update_profile(db, current_user.id, profile_data)
