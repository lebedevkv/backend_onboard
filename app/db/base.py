"""SQLAlchemy metadata export for Alembic autogenerate."""
from __future__ import annotations

from app.models.base import Base  # декларативная база

# ВАЖНО: импортируем все ORM-классы, чтобы Alembic «увидел» их при автогенерации
from app.models.models import (  # noqa: F401
    User,
    Company,
    CompanyDomain,
    Membership,
    MembershipManager,
    Quest,
    QuestStep,
    QuestAssignment,
    QuestStepSubmission,
    ProbationTask,
    ProbationReview,
)