from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.company import Company

from app.db.base_class import Base
from app.models.employee import Employee
from app.models.quest import QuestTemplate
from app.models.quest import QuestStep


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # user, employee, mentor, manager, hr, company_admin, super_admin
    is_active = Column(Boolean, default=True)
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    employee_id = Column(Integer, ForeignKey("employee_profiles.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    employee = relationship(
        "Employee",
        back_populates="user",
        uselist=False,
        foreign_keys=[Employee.user_id]
    )

    company = relationship(
        "Company",
        back_populates="users",
        foreign_keys=[company_id]
    )

    # квесты, созданные пользователем
    quest_templates = relationship(
        "QuestTemplate",
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys=[QuestTemplate.author_id]  # без кавычек
    )

    # шаги квестов, созданные пользователем
    quest_steps = relationship(
        "QuestStep",
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys=[QuestStep.author_id]
    )