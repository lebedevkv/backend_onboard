from __future__ import annotations
import uuid
from uuid import UUID

from fastapi import HTTPException, status

from app.services.base import UnitOfWork, GenericRepository
from app.models.models import CompanyDomain


class DomainService:
    """Service for adding and verifying company domains."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self._repo = GenericRepository[CompanyDomain](uow, CompanyDomain)

    def add_domain(self, company_id: UUID, domain: str) -> CompanyDomain:
        """Create a new domain entry with a verification token."""
        with self.uow as uow:
            token = uuid.uuid4().hex
            domain_obj = CompanyDomain(
                company_id=company_id,
                domain=domain,
                verification_token=token
            )
            uow.session.add(domain_obj)
            uow.commit()
            return domain_obj

    def verify_domain(self, domain_id: UUID, token: str) -> CompanyDomain:
        """Verify the domain by matching the token."""
        domain_obj = self._repo.get(domain_id)
        if not domain_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found"
            )
        if domain_obj.verification_token != token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        with self.uow as uow:
            domain_obj.is_verified = True
            uow.commit()
            return domain_obj
