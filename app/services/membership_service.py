

from __future__ import annotations
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.base import UnitOfWork, GenericRepository
from app.models.models import Membership, User
from app.models.enums import MembershipRole, MembershipStatus
from app.schemas.membership import MembershipCreate


class MembershipService:
    """Service to manage company memberships and hierarchy."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self._repo = GenericRepository[Membership](uow, Membership)

    def invite_user(
        self,
        email: str,
        role: MembershipRole,
        inviter: Membership
    ) -> Membership:
        """Invite an existing user to a company as a membership."""
        with self.uow as uow:
            user = uow.session.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            # Check if already a member
            exists = (
                uow.session.query(Membership)
                .filter(
                    Membership.user_id == user.id,
                    Membership.company_id == inviter.company_id
                )
                .first()
            )
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already invited or a member",
                )
            member = Membership(
                user_id=user.id,
                company_id=inviter.company_id,
                role=role,
                status=MembershipStatus.INVITED,
            )
            uow.session.add(member)
            uow.commit()
            return member

    def activate_applicant(
        self,
        member: Membership,
        role: MembershipRole = MembershipRole.EMPLOYEE
    ) -> Membership:
        """Activate an applicant to become an employee or other role."""
        with self.uow as uow:
            if member.status != MembershipStatus.APPLICANT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Membership is not an applicant",
                )
            member.role = role
            member.status = MembershipStatus.ACTIVE
            uow.commit()
            return member

    def change_role(
        self,
        member: Membership,
        new_role: MembershipRole
    ) -> Membership:
        """Change the membership's role."""
        with self.uow as uow:
            member.role = new_role
            uow.commit()
            return member

    def set_manager(
        self,
        member: Membership,
        manager: Membership
    ) -> Membership:
        """Assign a manager to a membership."""
        if manager.company_id != member.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager and member must belong to the same company",
            )
        with self.uow as uow:
            member.manager_membership_id = manager.id
            uow.commit()
            return member

    def get_subordinates(
        self,
        manager: Membership,
        recursive: bool = True
    ) -> List[Membership]:
        """Return direct or recursive subordinates of a manager."""
        with self.uow as uow:
            session: Session = uow.session  # type: ignore
            if recursive:
                subs: list[Membership] = []
                stack: list[Membership] = [manager]
                while stack:
                    current = stack.pop()
                    direct = (
                        session.query(Membership)
                        .filter(Membership.manager_membership_id == current.id)
                        .all()
                    )
                    subs.extend(direct)
                    stack.extend(direct)
                # exclude the manager itself
                return [m for m in subs if m.id != manager.id]
            else:
                return (
                    session.query(Membership)
                    .filter(Membership.manager_membership_id == manager.id)
                    .all()
                )