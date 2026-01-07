import uuid

from fastapi_users import schemas
from src.domain.enums import UserRole


class UserRead(schemas.BaseUser[uuid.UUID]):
    role: UserRole
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool
    is_manager: bool


class UserCreate(schemas.BaseUserCreate):
    first_name: str | None = None
    last_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None
