from src.db.repositories.user import UserRepository
from uuid import UUID
from src.domain.users import User
from src.domain.enums import UserRole
from src.exceptions import DomainError


class GrantRoleUseCaseError(DomainError): ...


class UserNotFoundError(GrantRoleUseCaseError): ...


class GrantRoleUseCase:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(
        self, invoker_user_id: UUID, target_user_id: UUID, new_role: UserRole
    ) -> None:
        invoker = await self._get_user(invoker_user_id)
        target = await self._get_user(target_user_id)

        target.change_role(new_role, invoker.role)

        await self.user_repo.save_user(target)

    async def _get_user(self, user_id: UUID) -> User:
        if user := await self.user_repo.get_user(user_id):
            return user
        raise UserNotFoundError(f"User {user_id} not found")
