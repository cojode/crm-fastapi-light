from src.db.models.user import User as UserDB
from src.domain.users import User, UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from src.exceptions import RepositoryError


class SQLAUserRepositoryError(RepositoryError): ...


class SaveUserNotFound(SQLAUserRepositoryError): ...


class SQLAUserRepository(UserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: UUID) -> User | None:
        db_user = await self.session.get(UserDB, user_id)
        return User.from_object(db_user) if db_user else None

    async def save_user(self, user: User) -> None:
        await self.session.merge(UserDB.from_dataclass(user))
