from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter()

@router.post("/", response_model=CompanyRead)
def create_company(company_in: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(name=company_in.name, description=company_in.description)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    return company


@router.put("/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, company_in: CompanyUpdate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    company.name = company_in.name
    company.description = company_in.description
    db.commit()
    db.refresh(company)
    return company
@router.patch("/{company_id}", response_model=CompanyRead)
def partial_update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")

    for field, value in company_in.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    db.delete(company)
    db.commit()
    return

