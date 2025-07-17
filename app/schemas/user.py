from typing import Optional, List
from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Literal
from .company import CompanyRead


class RoleEnum(str, Enum):
    company_admin = "company_admin"
    super_admin = "super_admin"
    hr = "hr"
    manager = "manager"
    employee = "employee"
    user = "user"

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    company: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["company_admin", "super_admin", "hr", "manager", "employee","user"]] = None
    is_active: Optional[bool] = None
    company: Optional[CompanyRead] = None
    department: Optional[str] = None
    position: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    # Дополнительные поля
    employee_id: Optional[int] = None
    position: Optional[str] = None
    department: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: Literal["company_admin", "super_admin", "hr", "employee", "manager","user"]
    is_active: bool = True
    company: Optional[CompanyRead] = None
    department: Optional[str] = None
    position: Optional[str] = None

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    role: Literal["super_admin", "company_admin", "hr", "manager", "employee","user"]


# Additional models
class QuestAssignmentInfo(BaseModel):
    quest_id: int
    completed: bool


class UserFullInfo(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    company: Optional[CompanyRead]
    role: str
    position: Optional[str]
    department: Optional[str]
    employee_id: Optional[int]
    assigned_quests: List[QuestAssignmentInfo]
    is_mentor: bool


    class Config:
        orm_mode = True