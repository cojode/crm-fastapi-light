import uuid
from typing import Optional

from fastapi import Request, Depends
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.db.models.user import User

from src.settings import settings
from src.logger import logger

from fastapi_users.db import SQLAlchemyUserDatabase
from src.db.models.user import get_user_db

SECRET = settings.secret_key


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def _user_verification(self, user: User, _: Optional[Request] = None) -> bool:
        """
        Verify the user by setting the is_verified flag to True.
        !!! Note: This is a placeholder implementation. !!!
        """
        await self.user_db.update(user, {"is_verified": True})
        return True

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        if await self._user_verification(user, request):
            logger.info("User %s has verified.", user.id)
        logger.info("User %s has registered.", user.id)

    async def get(self, id: uuid.UUID) -> User:
        logger.info("[GET USER] Fetching user with ID: %s", id)
        user = await super().get(id)
        logger.info(
            "[USER STATUS] User: %s, Role: %s, Active: %s, Verified: %s",
            user.id,
            user.role,
            user.is_active,
            user.is_verified,
        )
        return user


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
):
    yield UserManager(user_db)
