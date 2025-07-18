from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.quest import (
    QuestCreate, QuestRead, QuestUpdate,
    QuestAssignmentCreate, QuestAssignmentRead,
    QuestStepSubmissionUpdate, QuestStepSubmissionRead
)
from app.services.quest_service import QuestService
from app.services.base import UnitOfWork
from app.models.models import Membership, MembershipRole, MembershipStatus
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/quests", tags=["quests"])

# Dependency: UnitOfWork

def get_uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(lambda: db)

# Dependency: QuestService
def get_quest_service(uow: UnitOfWork = Depends(get_uow)) -> QuestService:
    return QuestService(uow)

@router.post("/", response_model=QuestRead, status_code=status.HTTP_201_CREATED)
def create_quest(
    data: QuestCreate,
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    service: QuestService = Depends(get_quest_service)
) -> QuestRead:
    # Ensure user has active membership
    with uow as u:
        membership = (
            u.session.query(Membership)
            .filter(
                Membership.user_id == current_user.id,
                Membership.status == MembershipStatus.ACTIVE
            )
            .first()
        )
        if not membership:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No active membership")
    quest = service.create(data, membership)
    return QuestRead.model_validate(quest)

@router.get("/company/{company_id}", response_model=list[QuestRead])
def list_company_quests(
    company_id: UUID,
    service: QuestService = Depends(get_quest_service)
) -> list[QuestRead]:
    quests = service.list(company_id=company_id)
    return [QuestRead.model_validate(q) for q in quests]

@router.get("/{quest_id}", response_model=QuestRead)
def get_quest(
    quest_id: UUID,
    service: QuestService = Depends(get_quest_service)
) -> QuestRead:
    quest = service.get(quest_id)
    if not quest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quest not found")
    return QuestRead.model_validate(quest)

@router.patch("/{quest_id}", response_model=QuestRead)
def update_quest(
    quest_id: UUID,
    data: QuestUpdate,
    service: QuestService = Depends(get_quest_service)
) -> QuestRead:
    quest = service.get(quest_id)
    if not quest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quest not found")
    updated = service.update(quest, data)
    return QuestRead.model_validate(updated)

@router.post("/{quest_id}/publish", response_model=QuestRead)
def publish_quest(
    quest_id: UUID,
    service: QuestService = Depends(get_quest_service)
) -> QuestRead:
    quest = service.get(quest_id)
    if not quest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quest not found")
    published = service.publish(quest)
    return QuestRead.model_validate(published)

@router.post("/{quest_id}/assign", response_model=QuestAssignmentRead)
def assign_quest(
    quest_id: UUID,
    data: QuestAssignmentCreate,
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    service: QuestService = Depends(get_quest_service)
) -> QuestAssignmentRead:
    # Ensure assigner has membership
    with uow as u:
        membership = (
            u.session.query(Membership)
            .filter(
                Membership.user_id == current_user.id,
                Membership.status == MembershipStatus.ACTIVE
            )
            .first()
        )
        if not membership:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No active membership")
    assignment = service.assign_quest(data, assigned_by=membership)
    return QuestAssignmentRead.model_validate(assignment)

@router.patch("/assignments/{submission_id}", response_model=QuestStepSubmissionRead)
def submit_quest_step(
    submission_id: UUID,
    data: QuestStepSubmissionUpdate,
    service: QuestService = Depends(get_quest_service)
) -> QuestStepSubmissionRead:
    # Fetch submission via underlying repository
    submission = service.uow.session.get(QuestStepSubmission, submission_id)  # type: ignore
    if not submission:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")
    updated = service.complete_step(submission, data)
    return QuestStepSubmissionRead.model_validate(updated)

@router.get("/{quest_id}/progress", response_model=list[QuestStepSubmissionRead])
def get_quest_progress(
    quest_id: UUID,
    uow: UnitOfWork = Depends(get_uow)
) -> list[QuestStepSubmissionRead]:
    # List all submissions for this quest assignment
    with uow as u:
        submissions = (
            u.session.query(QuestStepSubmission)
            .join(QuestAssignment)
            .filter(QuestAssignment.quest_id == quest_id)
            .all()
        )
    return [QuestStepSubmissionRead.model_validate(s) for s in submissions]
