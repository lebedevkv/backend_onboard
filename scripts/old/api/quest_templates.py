from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
# Schemas
from app.schemas.quest_template import QuestTemplateCreate, QuestTemplateResponse
from app.schemas.quest_assignment import QuestAssignmentCreate, QuestAssignmentResponse
from app.schemas.quest_progress import QuestProgressCreate, QuestProgressUpdate, QuestProgressResponse
# Services
from app.services.quest_template_service import (
    create_quest_template,
    get_all_quest_templates,
    get_quest_template,
    update_quest_template,
    delete_quest_template,
)
from app.services.quest_assignment_service import (
    assign_quest,
    get_assignments_for_user,
    get_all_assignments,
    delete_assignment,
)
from app.services.quest_progress_service import (
    create_progress,
    get_progress,
    update_progress,
)
# Dependencies
from app.utils.dependencies import (
    get_current_user,
    require_admin_or_hr,
    require_super_admin,
    require_manager,
    require_employee,
    require_mentor,
)
# Models
from app.models.user import User
from app.models.quest_assignment import QuestAssignment

router = APIRouter()

# Quest Template Endpoints
@router.post("/templates/", response_model=QuestTemplateResponse)
def create_template(
    template_in: QuestTemplateCreate,
    _: any = Depends(require_admin_or_hr),
    db: Session = Depends(get_db),
):
    return create_quest_template(db, template_in)

@router.get("/templates/", response_model=List[QuestTemplateResponse])
def read_all_templates(
    _: any = Depends(require_admin_or_hr),
    db: Session = Depends(get_db),
):
    return get_all_quest_templates(db)

@router.get("/templates/{template_id}", response_model=QuestTemplateResponse)
def read_template(
    template_id: int,
    _: any = Depends(require_admin_or_hr),
    db: Session = Depends(get_db),
):
    template = get_quest_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return template

@router.put("/templates/{template_id}", response_model=QuestTemplateResponse)
def update_template(
    template_id: int,
    template_in: QuestTemplateCreate,
    _: any = Depends(require_admin_or_hr),
    db: Session = Depends(get_db),
):
    updated = update_quest_template(db, template_id, template_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return updated

@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    _: any = Depends(require_admin_or_hr),
    db: Session = Depends(get_db),
):
    deleted = delete_quest_template(db, template_id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Шаблон не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Quest Assignment Endpoints
@router.post("/assignments/", response_model=QuestAssignmentResponse)
def assign_quest_to_user(
    data: QuestAssignmentCreate,
    db: Session = Depends(get_db),
    _: any = Depends(require_admin_or_hr),
):
    return assign_quest(db, data)

@router.get("/assignments/user/{user_id}", response_model=List[QuestAssignmentResponse])
def read_assignments_for_user(user_id: int, db: Session = Depends(get_db)):
    return get_assignments_for_user(db, user_id)

@router.get("/assignments/", response_model=List[QuestAssignmentResponse])
def read_all_assignments(
    db: Session = Depends(get_db),
    _: any = Depends(require_admin_or_hr),
):
    return get_all_assignments(db)

@router.get("/assignments/my-assignments", response_model=List[QuestAssignmentResponse])
def get_my_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_assignments_for_user(db, current_user.id)

@router.delete("/assignments/{assignment_id}", status_code=204)
def remove_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    _: any = Depends(require_admin_or_hr),
):
    result = delete_assignment(db, assignment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Назначение не найдено")

# Quest Progress Endpoints
@router.post("/progress/", response_model=QuestProgressResponse)
def create_quest_progress(
    data: QuestProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_progress(db, data)

@router.get("/progress/{assignment_id}", response_model=List[QuestProgressResponse])
def read_progress(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # superadmin and hr/admin
    try:
        require_super_admin(current_user)
        return get_progress(db, assignment_id)
    except HTTPException:
        pass
    try:
        require_admin_or_hr(current_user)
        return get_progress(db, assignment_id)
    except HTTPException:
        pass
    # mentor
    try:
        require_mentor(current_user)
        assignment = db.query(QuestAssignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Назначение не найдено")
        mentee = db.query(User).filter_by(id=assignment.user_id).first()
        if mentee and mentee.mentor_id == current_user.id:
            return get_progress(db, assignment_id)
    except HTTPException:
        pass
    # manager
    try:
        require_manager(current_user)
        assignment = db.query(QuestAssignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Назначение не найдено")
        subordinate = db.query(User).filter_by(id=assignment.user_id).first()
        if subordinate and subordinate.manager_id == current_user.id:
            return get_progress(db, assignment_id)
    except HTTPException:
        pass
    # employee
    try:
        require_employee(current_user)
        assignment = db.query(QuestAssignment).filter_by(id=assignment_id).first()
        if assignment and assignment.user_id == current_user.id:
            return get_progress(db, assignment_id)
    except HTTPException:
        pass
    raise HTTPException(status_code=403, detail="Недостаточно прав доступа")

@router.put("/progress/{progress_id}", response_model=QuestProgressResponse)
def update_quest_progress(
    progress_id: int,
    data: QuestProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = update_progress(db, progress_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Прогресс не найден")
    return result