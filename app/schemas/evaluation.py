from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvaluationBase(BaseModel):
    score: int
    comments: Optional[str]

class EvaluationSubmit(EvaluationBase):
    employee_id: int
    evaluator_id: int

class EvaluationRead(EvaluationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True