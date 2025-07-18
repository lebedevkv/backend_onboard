from __future__ import annotations
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.base import UnitOfWork, GenericRepository
from app.models.models import Quest, QuestStep, QuestAssignment, QuestStepSubmission, Membership
from app.schemas.quest import (
    QuestCreate, QuestUpdate,
    QuestStepCreate, QuestStepUpdate,
    QuestAssignmentCreate,
    QuestStepSubmissionUpdate
)
from app.models.enums import QuestStatus, StepSubmissionStatus


class QuestService(GenericRepository[Quest]):
    """Service for managing quests and quest assignments."""

    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow, Quest)
        self.uow = uow

    def create(self, data: QuestCreate, creator: Membership) -> Quest:
        """Create a new quest template."""
        with self.uow as uow:
            quest = Quest(**data.model_dump(), created_by_member=creator.id)
            uow.session.add(quest)
            uow.commit()
            return quest

    def update(self, quest: Quest, data: QuestUpdate) -> Quest:
        """Update fields of an existing quest."""
        with self.uow as uow:
            updates = data.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(quest, field, value)
            uow.commit()
            return quest

    def publish(self, quest: Quest) -> Quest:
        """Publish a draft quest."""
        if quest.status != QuestStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft quests can be published"
            )
        with self.uow as uow:
            quest.status = QuestStatus.PUBLISHED
            uow.commit()
            return quest

    def assign_quest(
        self,
        data: QuestAssignmentCreate,
        assigned_by: Membership | None = None
    ) -> QuestAssignment:
        """Assign a quest to a member, auto-calculating due date."""
        with self.uow as uow:
            assignment = QuestAssignment(**data.model_dump())
            assignment.assigned_by_member = assigned_by.id if assigned_by else None
            uow.session.add(assignment)
            # due_at is set by model event listener
            uow.commit()
            return assignment

    def complete_step(
        self,
        submission: QuestStepSubmission,
        data: QuestStepSubmissionUpdate
    ) -> QuestStepSubmission:
        """Submit or approve a quest step."""
        with self.uow as uow:
            updates = data.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(submission, field, value)
            submission.submitted_at = datetime.utcnow()
            if submission.status == StepSubmissionStatus.APPROVED:
                submission.reviewed_at = datetime.utcnow()
            uow.commit()
            return submission

    def compute_progress(self, assignment: QuestAssignment) -> float:
        """Compute completion percentage for a quest assignment."""
        total = len(assignment.submissions)
        if total == 0:
            return 0.0
        completed = sum(1 for s in assignment.submissions if s.status == StepSubmissionStatus.APPROVED)
        return (completed / total) * 100.0
