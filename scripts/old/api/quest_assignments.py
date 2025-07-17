from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.quest_assignment import QuestAssignmentCreate, QuestAssignmentResponse
from app.services.quest_assignment_service import (
    assign_quest,
    get_assignments_for_user,
    get_all_assignments,
    delete_assignment,
)
from app.utils.dependencies import get_db, require_admin_or_hr
from app.utils.dependencies import get_current_user
from app.models.user import User
from typing import List

router = APIRouter()


@router.post("/", response_model=QuestAssignmentResponse)
def assign_quest_to_user(
    data: QuestAssignmentCreate,
    db: Session = Depends(get_db),
    _: any = Depends(require_admin_or_hr),
):
    return assign_quest(db, data)


@router.get("/user/{user_id}", response_model=List[QuestAssignmentResponse])
def read_assignments_for_user(user_id: int, db: Session = Depends(get_db)):
    return get_assignments_for_user(db, user_id)


@router.get("/", response_model=List[QuestAssignmentResponse])
def read_all_assignments(
    db: Session = Depends(get_db),
    _: any = Depends(require_admin_or_hr),
):
    return get_all_assignments(db)


# New route for getting assignments for the current user
@router.get("/my-assignments", response_model=List[QuestAssignmentResponse])
def get_my_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_assignments_for_user(db, current_user.id)


@router.delete("/{assignment_id}", status_code=204)
def remove_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    _: any = Depends(require_admin_or_hr),
):
    result = delete_assignment(db, assignment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Назначение не найдено")