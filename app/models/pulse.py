from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base_class import Base
from sqlalchemy.sql import func

class PulseSurvey(Base):
    __tablename__ = "pulse_surveys"

    id = Column(Integer, primary_key=True)
    question = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class PulseResponse(Base):
    __tablename__ = "pulse_responses"

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey("pulse_surveys.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    answer = Column(String)
    submitted_at = Column(DateTime, server_default=func.now())