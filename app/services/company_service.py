from __future__ import annotations
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.base import UnitOfWork, GenericRepository
from app.models.models import Company, Membership
from app.models.enums import MembershipRole, MembershipStatus
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Service for creating and managing companies."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self._repo = GenericRepository[Company](uow, Company)

    def create_self_signup(self, data: CompanyCreate, owner_user_id: UUID) -> Company:
        """Create a new company and assign the owner user as CompanyOwner."""
        with self.uow as uow:
            # Create company
            company = Company(**data.model_dump())
            uow.session.add(company)
            uow.commit()
            # Assign owner membership
            membership = Membership(
                user_id=owner_user_id,
                company_id=company.id,
                role=MembershipRole.OWNER,
                status=MembershipStatus.ACTIVE
            )
            uow.session.add(membership)
            uow.commit()
            return company

    def get_by_id(self, company_id: UUID) -> Company | None:
        """Fetch a company by its ID."""
        return self._repo.get(company_id)

    def list(self) -> list[Company]:
        """List all companies."""
        return self._repo.list()

    def update(self, company: Company, data: CompanyUpdate) -> Company:
        """Update fields of an existing company."""
        with self.uow as uow:
            updates = data.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(company, field, value)
            uow.commit()
            return company