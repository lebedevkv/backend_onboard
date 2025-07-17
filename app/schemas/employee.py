from pydantic import BaseModel
from typing import Optional, List

class EmployeeBase(BaseModel):
    company_id: int
    department: str
    manager_id: Optional[int] = None
    division: Optional[str] = None
    position: Optional[str] = None
    mentor_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    user_id: int

class EmployeeRead(EmployeeBase):
    id: int
    user_id: int
    supervisor_id: Optional[int] = None
    mentees: Optional[List[int]] = None

    class Config:
        from_attributes = True