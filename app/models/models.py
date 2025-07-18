from __future__ import annotations
from datetime import datetime, date, timedelta
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as PgEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

from .enums import (
    GlobalRole, CompanyStatus, PlanTier, SignupMode,
    MembershipRole, MembershipStatus, QuestStatus,
    QuestStepApprovalRole, QuestAssignmentStatus,
    ProbationTaskStatus, ProbationStatus,
    ReviewDecision, StepSubmissionStatus
)

Base = declarative_base()
now = datetime.utcnow

# Users
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locale: Mapped[str | None] = mapped_column(String(10))
    global_role: Mapped[GlobalRole] = mapped_column(PgEnum(GlobalRole), default=GlobalRole.NONE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="user", cascade="all, delete-orphan")

# Companies and domains
class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(255), unique=True)
    timezone: Mapped[str | None] = mapped_column(String(64))
    plan_tier: Mapped[PlanTier] = mapped_column(PgEnum(PlanTier), default=PlanTier.FREE)
    signup_mode: Mapped[SignupMode] = mapped_column(PgEnum(SignupMode), default=SignupMode.SELF)
    status: Mapped[CompanyStatus] = mapped_column(PgEnum(CompanyStatus), default=CompanyStatus.PENDING)
    default_quest_duration_days: Mapped[int | None] = mapped_column(Integer)
    blocked_until_onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    default_quest_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("quests.id", ondelete="set null"))
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    domains: Mapped[list["CompanyDomain"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    quests: Mapped[list["Quest"]] = relationship(back_populates="company", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_companies_name", "name"),
    )

class CompanyDomain(Base):
    __tablename__ = "company_domains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="cascade"), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    company: Mapped["Company"] = relationship(back_populates="domains")

    __table_args__ = (
        Index("ix_company_domains_domain", "domain"),
    )

# Membership and hierarchy
class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="cascade"))
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="cascade"))
    role: Mapped[MembershipRole] = mapped_column(PgEnum(MembershipRole), default=MembershipRole.APPLICANT)
    status: Mapped[MembershipStatus] = mapped_column(PgEnum(MembershipStatus), default=MembershipStatus.INVITED)
    manager_membership_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id", ondelete="set null"))
    employment_type: Mapped[str | None] = mapped_column(String(32))
    probation_start_at: Mapped[date | None] = mapped_column(Date)
    probation_end_at: Mapped[date | None] = mapped_column(Date)
    probation_status: Mapped[ProbationStatus] = mapped_column(PgEnum(ProbationStatus), default=ProbationStatus.ONGOING)
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    user: Mapped["User"] = relationship(back_populates="memberships")
    company: Mapped["Company"] = relationship(back_populates="memberships")
    manager: Mapped["Membership"] = relationship(remote_side="Membership.id", back_populates="subordinates")
    subordinates: Mapped[list["Membership"]] = relationship(back_populates="manager")
    quest_assignments: Mapped[list["QuestAssignment"]] = relationship(back_populates="membership", cascade="all, delete-orphan")
    created_tasks: Mapped[list["ProbationTask"]] = relationship(back_populates="creator", cascade="all, delete-orphan", foreign_keys="ProbationTask.created_by_member")
    assigned_tasks: Mapped[list["ProbationTask"]] = relationship(back_populates="assignee", foreign_keys="ProbationTask.assigned_to_member")

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_memberships_user_company"),
        Index("ix_memberships_company_role", "company_id", "role"),
    )

class MembershipManager(Base):
    __tablename__ = "membership_managers"

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id", ondelete="cascade"), primary_key=True)
    manager_member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id", ondelete="cascade"), primary_key=True)
    relation: Mapped[str] = mapped_column(String(32), default="project")

    __table_args__ = (
        Index("ix_membership_managers_manager", "manager_member_id"),
    )

# Quests
class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="cascade"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    duration_days: Mapped[int | None] = mapped_column(Integer)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[QuestStatus] = mapped_column(PgEnum(QuestStatus), default=QuestStatus.DRAFT)
    created_by_member: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    company: Mapped["Company"] = relationship(back_populates="quests")
    steps: Mapped[list["QuestStep"]] = relationship(back_populates="quest", cascade="all, delete-orphan", order_by="QuestStep.sort_order")

    __table_args__ = (
        Index("ix_quests_company_status", "company_id", "status"),
    )

class QuestStep(Base):
    __tablename__ = "quest_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quests.id", ondelete="cascade"))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(String(32))  # doc/form/upload/meeting/quiz
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    content_json: Mapped[dict | None] = mapped_column(JSONB)
    approval_required_role: Mapped[QuestStepApprovalRole] =            mapped_column(PgEnum(QuestStepApprovalRole), default=QuestStepApprovalRole.NONE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    quest: Mapped["Quest"] = relationship(back_populates="steps")

    __table_args__ = (
        UniqueConstraint("quest_id", "sort_order", name="uq_quest_steps_order"),
    )

class QuestAssignment(Base):
    __tablename__ = "quest_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quests.id", ondelete="cascade"))
    membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id", ondelete="cascade"))
    assigned_by_member: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"))
    override_duration_days: Mapped[int | None] = mapped_column(Integer)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[QuestAssignmentStatus] = mapped_column(PgEnum(QuestAssignmentStatus), default=QuestAssignmentStatus.ASSIGNED)
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)

    membership: Mapped["Membership"] = relationship(back_populates="quest_assignments")
    quest: Mapped["Quest"] = relationship()
    submissions: Mapped[list["QuestStepSubmission"]] = relationship(back_populates="quest_assignment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_quest_assignments_company", "membership_id", "status"),
    )

class QuestStepSubmission(Base):
    __tablename__ = "quest_step_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_assignment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quest_assignments.id", ondelete="cascade"))
    quest_step_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quest_steps.id", ondelete="cascade"))
    status: Mapped[StepSubmissionStatus] = mapped_column(PgEnum(StepSubmissionStatus), default=StepSubmissionStatus.PENDING)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_member: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_json: Mapped[dict | None] = mapped_column(JSONB)

    quest_assignment: Mapped["QuestAssignment"] = relationship(back_populates="submissions")

    __table_args__ = (
        UniqueConstraint("quest_assignment_id", "quest_step_id", name="uq_submission_unique"),
    )

class ProbationTask(Base):
    __tablename__ = "probation_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="cascade"))
    created_by_member: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id", ondelete="cascade"))
    assigned_to_member: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id", ondelete="cascade"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[ProbationTaskStatus] = mapped_column(PgEnum(ProbationTaskStatus), default=ProbationTaskStatus.TODO)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result_text: Mapped[str | None] = mapped_column(Text)

    creator: Mapped["Membership"] = relationship(back_populates="created_tasks", foreign_keys=[created_by_member])
    assignee: Mapped["Membership"] = relationship(back_populates="assigned_tasks", foreign_keys=[assigned_to_member])
    reviews: Mapped[list["ProbationReview"]] = relationship(back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_probation_tasks_company_status", "company_id", "status"),
    )

class ProbationReview(Base):
    __tablename__ = "probation_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("probation_tasks.id", ondelete="cascade"))
    reviewer_member: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id", ondelete="set null"))
    score: Mapped[float | None] = mapped_column(Numeric(3, 1))
    decision: Mapped[ReviewDecision] = mapped_column(PgEnum(ReviewDecision))
    comments: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    task: Mapped["ProbationTask"] = relationship(back_populates="reviews")

    __table_args__ = (
        Index("ix_probation_reviews_task", "task_id"),
    )

# Listener to auto-calculate due_at for quest assignments
from sqlalchemy import event

@event.listens_for(QuestAssignment, "before_insert")
def set_due_at(mapper, connection, target):  # type: ignore
    if target.due_at is None:
        dur = target.override_duration_days or (target.quest.duration_days if target.quest else None) or target.membership.company.default_quest_duration_days or 14
        target.due_at = (target.assigned_at or now()) + timedelta(days=dur)
