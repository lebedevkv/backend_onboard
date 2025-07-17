from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    evaluator_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    comments = Column(String)
    created_at = Column(DateTime, server_default=func.now())