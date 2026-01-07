from src.db.repositories.user import UserRepository
from uuid import UUID
from src.domain.users import User
from src.exceptions import DomainError


class GrantRoleUseCaseError(DomainError): ...


class UserNotFoundError(GrantRoleUseCaseError): ...


class DeleteMeUseCase:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, invoker_user_id: UUID) -> None:
        user = await self._get_user(invoker_user_id)
        user.delete()
        await self.user_repo.save_user(user)

    async def _get_user(self, user_id: UUID) -> User:
        if user := await self.user_repo.get_user(user_id):
            return user
        raise UserNotFoundError(f"User {user_id} not found")
