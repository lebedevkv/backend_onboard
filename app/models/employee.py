from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.company import Company

class Employee(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="employees")
    department = Column(String, nullable=False)
    division = Column(String, nullable=True)  # отдел (необязательный)
    position = Column(String, nullable=True)
    user = relationship("User", back_populates="employee", foreign_keys=[user_id])
    supervisor_id = Column(Integer, ForeignKey("employee_profiles.id"), nullable=True)

    assignments = relationship("QuestAssignment", back_populates="employee")
    # establish backref on User dynamically (for clarity, but this line is not standard usage)
    # user.employee_profile = relationship("Employee", back_populates="user", uselist=False)
    supervisor = relationship(
        "Employee",
        back_populates="mentees",
        foreign_keys=[supervisor_id],
        remote_side=[id]
    )
    mentees = relationship(
        "Employee",
        back_populates="supervisor",
        foreign_keys=[supervisor_id]
    )
    # Backref for user -> employee_profile
    # This is for clarity, but normally you'd add this in User model:
    # user.employee_profile = relationship("Employee", back_populates="user", uselist=False)
    # В EmployeeProfile
    assigned_quests = relationship("QuestAssignment", back_populates="employee")