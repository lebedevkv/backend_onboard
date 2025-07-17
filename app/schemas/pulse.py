from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PulseSurveyCreate(BaseModel):
    question: str

class PulseSurveyRead(BaseModel):
    id: int
    question: str
    created_at: datetime

    class Config:
        from_attributes = True

class PulseResponseCreate(BaseModel):
    survey_id: int
    user_id: int
    answer: str

class PulseResponseRead(BaseModel):
    id: int
    answer: str
    submitted_at: datetime

    class Config:
        from_attributes = True