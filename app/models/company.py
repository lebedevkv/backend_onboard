from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    address = Column(String, nullable=True)
    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")
    quest_templates = relationship(
        "QuestTemplate",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    users = relationship(
        "User",
        back_populates="company",
        cascade="all, delete-orphan"
    )