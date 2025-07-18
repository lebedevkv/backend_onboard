from __future__ import annotations
from enum import Enum


class GlobalRole(str, Enum):
    SUPER_ADMIN = "SuperAdmin"
    NONE = "None"


class CompanyStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SignupMode(str, Enum):
    SELF = "self"
    INVITE = "invite"
    DOMAIN = "domain"


class MembershipRole(str, Enum):
    OWNER = "CompanyOwner"
    ADMIN = "CompanyAdmin"
    HR = "HR"
    MANAGER = "Manager"
    EMPLOYEE = "Employee"
    APPLICANT = "Applicant"


class MembershipStatus(str, Enum):
    INVITED = "invited"
    APPLICANT = "applicant"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class QuestStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class QuestStepApprovalRole(str, Enum):
    NONE = "None"
    MANAGER = "Manager"
    HR = "HR"


class QuestAssignmentStatus(str, Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    EXPIRED = "expired"


class ProbationTaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProbationStatus(str, Enum):
    ONGOING = "ongoing"
    EXTENDED = "extended"
    PASSED = "passed"
    FAILED = "failed"


class ReviewDecision(str, Enum):
    PASS_ = "pass"
    EXTEND = "extend"
    FAIL = "fail"


class StepSubmissionStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"
