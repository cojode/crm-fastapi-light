from fastapi.routing import APIRouter

from src.web.pages.auth.views import router as auth_router
from src.web.pages.profile.views import router as profile_router
from src.web.pages.teams.views import router as teams_router
from src.web.pages.tasks.views import router as tasks_router
from src.web.pages.meetings.views import router as meeting_router
from src.web.pages.calendar.views import router as calendar_router

pages_router = APIRouter(tags=["frontend"])

pages_router.include_router(auth_router)
pages_router.include_router(profile_router)
pages_router.include_router(teams_router)
pages_router.include_router(tasks_router)
pages_router.include_router(meeting_router)
pages_router.include_router(calendar_router)
