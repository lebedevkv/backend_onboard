from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DevelopmentPlanBase(BaseModel):
    description: str
    is_acknowledged: Optional[bool] = False

class DevelopmentPlanCreate(DevelopmentPlanBase):
    employee_id: int
    mentor_id: int

class DevelopmentPlanRead(DevelopmentPlanBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True