

from pydantic import BaseModel
from typing import Optional

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase):
    id: int

    class Config:
        from_attributes = True  # заменяет orm_mode в Pydantic V2

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None