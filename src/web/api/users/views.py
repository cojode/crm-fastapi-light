from fastapi import APIRouter, Depends

from src.web.api.users.schemas import UserCreate, UserRead, UserUpdate
from src.domain.enums import UserRole
from src.web.dependency import get_grant_role_use_case
from uuid import UUID

from src.services.users.dependency import (
    auth_backend_api,
    auth_backend_pages,
    fastapi_users_api,
    fastapi_users_pages,
    current_staff_api,
)

pages_requires_verification = False

pages_login_router = fastapi_users_pages.get_auth_router(
    auth_backend_pages, pages_requires_verification
)
pages_register_router = fastapi_users_pages.get_register_router(UserRead, UserCreate)
pages_get_user_router = fastapi_users_pages.get_users_router(UserRead, UserUpdate)

pages_current_user_token = fastapi_users_pages.authenticator.current_user_token(
    active=True, verified=pages_requires_verification
)

api_login_router = fastapi_users_api.get_auth_router(auth_backend_api)
api_register_router = fastapi_users_api.get_register_router(UserRead, UserCreate)
api_get_user_router = fastapi_users_api.get_users_router(UserRead, UserUpdate)

router = APIRouter()


@router.patch("/{user_id}/role")
async def grant_role(
    user_id: UUID,
    role: UserRole,
    user=Depends(current_staff_api),
    use_case=Depends(get_grant_role_use_case),
):
    return await use_case.execute(user.id, user_id, role)
