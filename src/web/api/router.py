from fastapi.routing import APIRouter
from src.web.api.monitoring import router as monitoring_router
from src.web.api.users import (
    api_login_router,
    api_register_router,
    api_get_user_router,
    router as user_router,
)
from src.web.api.teams import router as teams_router
from src.web.api.tasks import router as tasks_router
from src.web.api.meeting import router as meeting_router

api_router = APIRouter(prefix="/api")
api_router.include_router(monitoring_router, prefix="", tags=["monitoring"])
api_router.include_router(api_login_router, prefix="/auth", tags=["auth"])
api_router.include_router(api_register_router, prefix="/auth", tags=["auth"])
api_router.include_router(api_get_user_router, prefix="/users", tags=["users"])
api_router.include_router(user_router, prefix="/users", tags=["roles"])
api_router.include_router(teams_router, prefix="/teams", tags=["teams"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(meeting_router, prefix="/meeting", tags=["meetings"])
