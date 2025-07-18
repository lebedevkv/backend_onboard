from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.services.membership_service import MembershipService
from app.services.base import UnitOfWork
from app.models.enums import MembershipRole, MembershipStatus
from app.models.models import Membership
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])

# Dependency: UnitOfWork
def get_uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(lambda: db)

# Dependency: MembershipService
def get_membership_service(uow: UnitOfWork = Depends(get_uow)) -> MembershipService:
    return MembershipService(uow)

@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_new_employee(
    data: EmployeeCreate,
    current_user=Depends(get_current_user),
    service: MembershipService = Depends(get_membership_service)
) -> EmployeeRead:
    # Find inviter membership for current user
    with service.uow as uow:
        inviter = uow.session.query(Membership).filter(
            Membership.user_id == current_user.id,
            Membership.status == MembershipStatus.ACTIVE
        ).first()
        if not inviter:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Current user cannot invite employees"
            )
    # Invite and activate new employee
    member = service.invite_user(
        email=data.email,
        role=MembershipRole.EMPLOYEE,
        inviter=inviter
    )
    activated = service.activate_applicant(member)
    return EmployeeRead.model_validate(activated)

@router.get("/", response_model=list[EmployeeRead])
def list_employees(
    current_user=Depends(get_current_user),
    service: MembershipService = Depends(get_membership_service)
) -> list[EmployeeRead]:
    # Get current user's company
    with service.uow as uow:
        inviter = uow.session.query(Membership).filter(
            Membership.user_id == current_user.id,
            Membership.status == MembershipStatus.ACTIVE
        ).first()
        if not inviter:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Current user has no active membership"
            )
        employees = uow.session.query(Membership).filter(
            Membership.company_id == inviter.company_id,
            Membership.role == MembershipRole.EMPLOYEE,
            Membership.status == MembershipStatus.ACTIVE
        ).all()
    return [EmployeeRead.model_validate(e) for e in employees]

@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(
    employee_id: UUID,
    service: MembershipService = Depends(get_membership_service)
) -> EmployeeRead:
    member = service._repo.get(employee_id)
    if not member or member.role != MembershipRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return EmployeeRead.model_validate(member)