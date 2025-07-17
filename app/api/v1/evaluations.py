from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.evaluation import EvaluationSubmit, EvaluationRead
from app.services.evaluation_service import submit_evaluation
from app.utils.dependencies import get_db

router = APIRouter()

@router.post("/evaluations", response_model=EvaluationRead, tags=["evaluations"])
def submit(data: EvaluationSubmit, db: Session = Depends(get_db)):
    return submit_evaluation(db, data)