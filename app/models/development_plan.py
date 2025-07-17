from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from app.db.base_class import Base
from sqlalchemy.sql import func

class DevelopmentPlan(Base):
    __tablename__ = "development_plans"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    mentor_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())