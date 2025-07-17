from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class QuestTemplate(Base):
    __tablename__ = "quest_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    deadline_days = Column(Integer, nullable=True)

    author = relationship("User", back_populates="quest_templates", foreign_keys=[author_id])
    company = relationship("Company", back_populates="quest_templates")
    steps = relationship("QuestStep", back_populates="template", cascade="all, delete-orphan")
    assignments = relationship("QuestAssignment", back_populates="template", cascade="all, delete-orphan")


class QuestStep(Base):
    __tablename__ = "quest_steps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    deadline_days = Column(Integer, nullable=True)
    quest_template_id = Column(Integer, ForeignKey("quest_templates.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    template = relationship("QuestTemplate", back_populates="steps")
    author = relationship("User", back_populates="quest_steps")
    progress = relationship(
        "QuestProgress",
        back_populates="step",
        cascade="all, delete-orphan",
        foreign_keys="QuestProgress.step_id"
    )


class QuestAssignment(Base):
    __tablename__ = "quest_assignments"

    id = Column(Integer, primary_key=True, index=True)
    quest_template_id = Column(Integer, ForeignKey("quest_templates.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employee_profiles.id"), nullable=False)

    template = relationship("QuestTemplate", back_populates="assignments")
    employee = relationship("Employee", back_populates="assignments")
    progress = relationship(
        "QuestProgress",
        back_populates="assignment",
        cascade="all, delete-orphan",
        foreign_keys="QuestProgress.assignment_id"
    )


class QuestProgress(Base):
    __tablename__ = "quest_progress"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("quest_assignments.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(Integer, ForeignKey("quest_steps.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    assignment = relationship("QuestAssignment", back_populates="progress")
    step = relationship("QuestStep", back_populates="progress")