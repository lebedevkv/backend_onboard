from .auth import router as auth_router
from .users import router as users_router
from .company import router as company_router
from .employee import router as employee_router
from .tasks import router as tasks_router
from .evaluations import router as evaluations_router
from .pulse import router as pulse_router
from .development import router as development_router
from .quest import router as quest_router

__all__ = [
    "auth_router",
    "users_router",
    "company_router",
    "employee_router",
    "tasks_router",
    "evaluations_router",
    "pulse_router",
    "development_router",
    "quest_router",
]
