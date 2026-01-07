from fastapi import Depends, HTTPException, status
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users import FastAPIUsers

from src.domain.enums import UserRole

import uuid

from src.settings import settings

from src.services.users.user_manager import get_user_manager

from src.db.models.user import User

SECRET = settings.secret_key
TOKEN_URL = settings.jwt_login_endpoint


bearer_transport = BearerTransport(tokenUrl=TOKEN_URL)

cookie_transport = CookieTransport()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend_api = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

auth_backend_pages = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users_api = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend_api],
)

fastapi_users_pages = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend_pages],
)

current_user_api = fastapi_users_api.current_user()
current_active_user_api = fastapi_users_api.current_user(active=True)
current_active_verified_user_api = fastapi_users_api.current_user(
    active=True, verified=True
)

current_user_pages = fastapi_users_pages.current_user()
current_active_user_pages = fastapi_users_pages.current_user(active=True)
current_active_verified_user_pages = fastapi_users_pages.current_user(
    active=True, verified=True
)


def role_required(current_active_verified_user_variant, *required_roles: UserRole):
    def dependency(
        user: User = Depends(current_active_verified_user_variant),
    ) -> User:
        if user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires any of [{' '.join(required_roles)}] role(s)",
            )
        return user

    return dependency


def role_required_api(*required_roles: UserRole):
    return role_required(current_active_verified_user_api, *required_roles)


def role_required_pages(*required_roles: UserRole):
    return role_required(current_active_user_pages, *required_roles)


current_employee_api = role_required_api(UserRole.DEFAULT)
current_manager_api = role_required_api(UserRole.MANAGER)
current_admin_api = role_required_api(UserRole.ADMIN)
current_staff_api = role_required_api(UserRole.ADMIN, UserRole.MANAGER)

current_employee_pages = role_required_pages(UserRole.DEFAULT)
current_manager_pages = role_required_pages(UserRole.MANAGER)
current_admin_pages = role_required_pages(UserRole.ADMIN)
current_staff_pages = role_required_pages(UserRole.ADMIN, UserRole.MANAGER)
