from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class QuestStep(Base):
    __tablename__ = "quest_steps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    quest_template_id = Column(Integer, ForeignKey("quest_templates.id"), nullable=False)
    template = relationship("QuestTemplate", back_populates="steps")
    description = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

    points = Column(Integer, nullable=False)
    deadline = Column(DateTime, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Связь с QuestTemplate

    author = relationship("User", back_populates="quest_steps")