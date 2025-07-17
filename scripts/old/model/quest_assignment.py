from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class QuestAssignment(Base):
    __tablename__ = "quest_assignments"

    id = Column(Integer, primary_key=True, index=True)
    quest_template_id = Column(Integer, ForeignKey("quest_templates.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employee_profiles.id"), nullable=False)

    # relationships
    template = relationship("QuestTemplate", back_populates="assignments")
    employee = relationship("Employee", back_populates="assignments")
    progress = relationship(
        "QuestProgress",
        back_populates="assignment",
        cascade="all, delete-orphan",
        foreign_keys="[QuestProgress.assignment_id]"
    )

# Import QuestProgress to avoid relationship initialization errors
from app.models.quest_progress import QuestProgress