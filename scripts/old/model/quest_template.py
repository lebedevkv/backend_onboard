from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from sqlalchemy import DateTime, ForeignKey, func


class QuestTemplate(Base):
    __tablename__ = "quest_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    steps = relationship("QuestStep", back_populates="template", cascade="all, delete-orphan")
    author = relationship(
        "User",
        back_populates="quest_templates",
        foreign_keys=[author_id]
    )
    company = relationship("Company", back_populates="quest_templates")
    assignments = relationship("QuestAssignment", back_populates="template", cascade="all, delete-orphan")