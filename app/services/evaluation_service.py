from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvaluationSubmit

def submit_evaluation(db: Session, data: EvaluationSubmit) -> Evaluation:
    evaluation = Evaluation(**data.dict())
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation