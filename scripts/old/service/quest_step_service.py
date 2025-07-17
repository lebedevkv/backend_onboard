from sqlalchemy.orm import Session
from app.models.quest_template import QuestTemplate
from app.models.quest_step import QuestStep
from app.models.quest_assignment import QuestAssignment
from app.models.quest_progress import QuestProgress

from app.schemas.quest_template import QuestTemplateCreate, QuestTemplateUpdate
from app.schemas.quest_step import QuestStepCreate
from app.schemas.quest_assignment import QuestAssignmentCreate
from app.schemas.quest_progress import QuestProgressCreate, QuestProgressUpdate

# ----------------------------
# QuestTemplate CRUD
# ----------------------------

def create_quest_template(db: Session, data: QuestTemplateCreate) -> QuestTemplate:
    # 1. Create template without steps
    template = QuestTemplate(
        title=data.title,
        description=data.description,
        author_id=data.author_id,
        company_id=data.company_id,
        deadline=data.deadline
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    # 2. Add steps linked to the template
    for step_data in data.steps:
        step = QuestStep(
            title=step_data.title,
            description=step_data.description,
            order=step_data.order,
            points=step_data.points,
            author_id=step_data.author_id,
            deadline=step_data.deadline,
            quest_template_id=template.id
        )
        db.add(step)
    db.commit()
    db.refresh(template)
    return template

def get_all_quest_templates(db: Session):
    return db.query(QuestTemplate).all()

def get_quest_template(db: Session, template_id: int):
    return db.query(QuestTemplate).filter(QuestTemplate.id == template_id).first()

def update_quest_template(db: Session, template_id: int, data: QuestTemplateUpdate):
    template = get_quest_template(db, template_id)
    if not template:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template

def delete_quest_template(db: Session, template_id: int):
    template = get_quest_template(db, template_id)
    if not template:
        return False
    db.delete(template)
    db.commit()
    return True

# ----------------------------
# QuestAssignment CRUD
# ----------------------------

def assign_quest(db: Session, data: QuestAssignmentCreate) -> QuestAssignment:
    assignment = QuestAssignment(**data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

def get_assignments_for_user(db: Session, user_id: int):
    return db.query(QuestAssignment).filter(QuestAssignment.user_id == user_id).all()

def get_assignment(db: Session, assignment_id: int):
    return db.query(QuestAssignment).filter(QuestAssignment.id == assignment_id).first()

def get_all_assignments(db: Session):
    return db.query(QuestAssignment).all()

def delete_assignment(db: Session, assignment_id: int):
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        return False
    db.delete(assignment)
    db.commit()
    return True

# ----------------------------
# QuestProgress CRUD
# ----------------------------

def create_progress(db: Session, data: QuestProgressCreate) -> QuestProgress:
    progress = QuestProgress(**data.model_dump())
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress

def list_progress_by_assignment(db: Session, assignment_id: int):
    return db.query(QuestProgress).filter(QuestProgress.assignment_id == assignment_id).all()

def get_progress(db: Session, assignment_id: int):
    return list_progress_by_assignment(db, assignment_id)

def update_progress(db: Session, progress_id: int, data: QuestProgressUpdate):
    progress = db.query(QuestProgress).filter(QuestProgress.id == progress_id).first()
    if not progress:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(progress, field, value)
    db.commit()
    db.refresh(progress)
    return progress