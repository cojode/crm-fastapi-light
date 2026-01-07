from src.domain.enums import UserRole

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.exceptions import DomainError

from src.domain.utils import FromObjectMixin


class UserError(DomainError): ...


class InsufficientRoleError(UserError): ...


class RoleModifyError(InsufficientRoleError): ...


class RoleGrantError(InsufficientRoleError): ...


@dataclass
class User(FromObjectMixin):
    id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool
    role: UserRole

    def change_role(self, new_role: UserRole, requester_role: UserRole):
        if not requester_role.can_modify(self.role):
            raise RoleModifyError("Cannot modify user with higher role")
        if not requester_role.can_grant(new_role):
            raise RoleGrantError("Cannot grant this role")
        self.role = new_role

    def delete(self):
        self.is_active = False


class UserRepository(ABC):
    @abstractmethod
    async def get_user(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def save_user(self, user: User) -> None: ...
