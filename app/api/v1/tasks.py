from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.probation_service import ProbationService
from app.services.base import UnitOfWork
from app.models.models import Membership, ProbationTask
from app.models.enums import MembershipStatus, ProbationTaskStatus
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

# Dependency: UnitOfWork
def get_uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(lambda: db)

# Dependency: ProbationService
def get_task_service(uow: UnitOfWork = Depends(get_uow)) -> ProbationService:
    return ProbationService(uow)

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    service: ProbationService = Depends(get_task_service)
) -> TaskRead:
    # Verify current user membership
    with uow as u:
        creator = u.session.query(Membership).filter(
            Membership.user_id == current_user.id,
            Membership.status == MembershipStatus.ACTIVE
        ).first()
        if not creator:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No active membership")
        assignee = u.session.get(Membership, data.assigned_to_member)
        if not assignee:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignee not found")
    task = service.create_task(
        creator=creator,
        assignee=assignee,
        title=data.title,
        description=data.description,
        due_at=data.due_at
    )
    return TaskRead.model_validate(task)

@router.get("/", response_model=list[TaskRead])
def list_tasks(
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
) -> list[TaskRead]:
    with uow as u:
        membership = u.session.query(Membership).filter(
            Membership.user_id == current_user.id,
            Membership.status == MembershipStatus.ACTIVE
        ).first()
        if not membership:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No active membership")
        tasks = u.session.query(ProbationTask).filter(
            ProbationTask.company_id == membership.company_id
        ).all()
    return [TaskRead.model_validate(t) for t in tasks]

@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: UUID,
    service: ProbationService = Depends(get_task_service)
) -> TaskRead:
    task = service._repo.get(task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return TaskRead.model_validate(task)

@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
) -> TaskRead:
    with uow as u:
        task = u.session.get(ProbationTask, task_id)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(task, field, value)
        if updates.get("status") == ProbationTaskStatus.DONE:
            task.completed_at = datetime.utcnow()
        u.commit()
    return TaskRead.model_validate(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    service: ProbationService = Depends(get_task_service)
) -> None:
    task = service._repo.get(task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    with service.uow as u:
        service.remove(task)
        u.commit()
    return