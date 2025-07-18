

from __future__ import annotations
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from app.services.base import UnitOfWork, GenericRepository
from app.models.models import ProbationTask, ProbationReview, Membership
from app.models.enums import ReviewDecision, ProbationStatus, ProbationTaskStatus


class ProbationService(GenericRepository[ProbationTask]):
    """Service for managing probation tasks and reviews."""

    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow, ProbationTask)
        self.uow = uow

    def create_task(
        self,
        creator: Membership,
        assignee: Membership,
        title: str,
        *,
        description: str | None = None,
        due_at: datetime | None = None
    ) -> ProbationTask:
        """Create a probation task for an employee under probation period."""
        with self.uow as uow:
            task = ProbationTask(
                company_id=creator.company_id,
                created_by_member=creator.id,
                assigned_to_member=assignee.id,
                title=title,
                description=description,
                due_at=due_at,
                status=ProbationTaskStatus.TODO
            )
            uow.session.add(task)
            uow.commit()
            return task

    def review_task(
        self,
        task: ProbationTask,
        reviewer: Membership,
        score: float,
        decision: ReviewDecision,
        comments: str | None = None
    ) -> ProbationReview:
        """Add a review to a completed probation task."""
        if task.status != ProbationTaskStatus.DONE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task must be marked done before review"
            )
        with self.uow as uow:
            review = ProbationReview(
                task_id=task.id,
                reviewer_member=reviewer.id,
                score=score,
                decision=decision,
                comments=comments,
                created_at=datetime.utcnow(),
            )
            uow.session.add(review)
            uow.commit()
            return review

    def evaluate_member(self, member: Membership) -> ProbationStatus:
        """Evaluate overall probation status based on tasks and reviews."""
        with self.uow as uow:
            # Load all tasks and associated reviews
            tasks = (
                uow.session.query(ProbationTask)
                .filter(ProbationTask.assigned_to_member == member.id)
                .all()
            )
            all_reviews = []
            for task in tasks:
                all_reviews.extend(task.reviews)

            # If any review is a fail, probation failed
            if any(r.decision == ReviewDecision.FAIL for r in all_reviews):
                status = ProbationStatus.FAILED
            # If all tasks done and no fail, passed
            elif tasks and all(t.status == ProbationTaskStatus.DONE for t in tasks) and not any(r.decision == ReviewDecision.FAIL for r in all_reviews):
                status = ProbationStatus.PASSED
            else:
                status = member.probation_status

            member.probation_status = status
            uow.commit()
            return status