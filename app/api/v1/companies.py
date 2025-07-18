from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.company_service import CompanyService
from app.services.base import UnitOfWork
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])

# Dependency: UnitOfWork
def get_uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(lambda: db)

# Dependency: CompanyService
def get_company_service(uow: UnitOfWork = Depends(get_uow)) -> CompanyService:
    return CompanyService(uow)

@router.post("/self-signup", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def self_signup(
    data: CompanyCreate,
    current_user=Depends(get_current_user),
    service: CompanyService = Depends(get_company_service)
) -> CompanyRead:
    company = service.create_self_signup(data, current_user.id)
    return CompanyRead.model_validate(company)

@router.get("/", response_model=list[CompanyRead])
def list_companies(
    service: CompanyService = Depends(get_company_service)
) -> list[CompanyRead]:
    companies = service.list()
    return [CompanyRead.model_validate(c) for c in companies]

@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: UUID,
    service: CompanyService = Depends(get_company_service)
) -> CompanyRead:
    company = service.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return CompanyRead.model_validate(company)

@router.patch("/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    service: CompanyService = Depends(get_company_service)
) -> CompanyRead:
    company = service.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    updated = service.update(company, data)
    return CompanyRead.model_validate(updated)

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: UUID,
    service: CompanyService = Depends(get_company_service)
) -> None:
    company = service.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    with service.uow as uow:
        uow.session.delete(company)
        uow.commit()
    return
