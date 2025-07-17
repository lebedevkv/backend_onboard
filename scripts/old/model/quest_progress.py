from sqlalchemy import Column, Integer, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class QuestProgress(Base):
    __tablename__ = "quest_progress"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("quest_assignments.id", ondelete="CASCADE"), index=True, nullable=False)
    step_id = Column(Integer, ForeignKey("quest_steps.id", ondelete="CASCADE"), index=True, nullable=False)
    is_completed = Column(Boolean, default=False)
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    assignment = relationship("QuestAssignment", back_populates="progress")
    step = relationship("QuestStep", back_populates="progress")

# Import QuestProgress to avoid relationship initialization errors
from app.models.quest_progress import QuestProgress