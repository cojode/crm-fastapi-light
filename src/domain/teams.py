from src.domain.enums import TeamRole
from functools import wraps

import datetime

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from abc import abstractmethod, ABC

from src.settings import settings

from src.exceptions import DomainError, ForbiddenDomainError

from src.domain.utils import FromObjectMixin

from src.domain.users import User


class TeamError(DomainError): ...


class TeamMemberError(DomainError): ...


class TeamInviteError(DomainError): ...


class InsufficientPermissionsError(TeamMemberError, ForbiddenDomainError): ...


class RoleHierarchyError(TeamMemberError, ForbiddenDomainError): ...


class ProtectedRoleError(TeamMemberError, ForbiddenDomainError): ...


class ProtectedRoleRemoveError(ProtectedRoleError): ...


class ProtectedRoleGrantError(ProtectedRoleError): ...


@dataclass
class Team(FromObjectMixin):
    name: str
    id: UUID = field(default_factory=uuid4)

    created_at: datetime.datetime = field(
        default_factory=settings.datetime_now
    )

    members: list["TeamMember"] | None = None
    invites: list["TeamInvite"] | None = None

    def rename(self, new_name: str):
        self.name = new_name


from src.domain.tasks import Task
from src.domain.meetings import Meeting


@dataclass
class TeamMember(FromObjectMixin):
    team_id: UUID
    user_id: UUID
    user: User | None = None
    joined_at: datetime.datetime | None = None
    role: TeamRole = TeamRole.EMPLOYEE

    def has_permission(self, action: str):
        return self.role.has_permission(action)

    @staticmethod
    def _permission_required(func):
        @wraps(func)
        def wrapper(self: "TeamMember", *args, **kwargs):
            action = func.__name__
            invoker_role = self.role

            if invoker_role is None or not invoker_role.has_permission(action):
                raise InsufficientPermissionsError(
                    "Insufficient permissions to perform this action"
                )

            return func(self, *args, **kwargs)

        return wrapper

    def _validate_member_affected(self, target: "TeamMember"):
        if not self.role.can_affect_other_role(target.role):
            raise RoleHierarchyError("Can not perform: insufficient team role")

    @_permission_required
    def add_member(self, new_member_id: UUID) -> "TeamMember":
        return TeamMember(self.team_id, new_member_id)

    @_permission_required
    def change_role(self, target: "TeamMember", new_role: TeamRole) -> None:
        if new_role.is_protected():
            raise ProtectedRoleGrantError("Can not grant protected role")
        self._validate_member_affected(target)
        target.role = new_role

    @_permission_required
    def remove_member(self, target: "TeamMember"):
        if target.role.is_protected():
            raise ProtectedRoleRemoveError(
                "Can not remove member with protected role"
            )
        self._validate_member_affected(target)

    @_permission_required
    def generate_invite_code(self) -> "TeamInvite":
        return TeamInvite(team_id=self.team_id, creator_id=self.user_id)

    @_permission_required
    def create_task(
        self,
        title: str,
        deadline: datetime.datetime,
        description: str | None = None,
        assignee_id: UUID | None = None,
        period_offset: datetime.timedelta | None = None,
    ) -> Task:
        return Task(
            title=title,
            description=description,
            deadline=deadline,
            author_id=self.user_id,
            team_id=self.team_id,
            assignee_id=assignee_id,
            period_offset=period_offset,
        )

    @_permission_required
    def task_override(self): ...

    @_permission_required
    def meeting_override(self): ...

    @property
    def can_override_task(self) -> bool:
        try:
            self.task_override()
        except InsufficientPermissionsError:
            return False
        return True

    @property
    def can_override_meeting(self) -> bool:
        try:
            self.meeting_override()
        except InsufficientPermissionsError:
            return False
        return True

    def access_task(self, task: Task) -> Task:
        task.inspect(self.user_id, override=self.can_override_task)
        return task

    @_permission_required
    def create_meeting(
        self,
        title: str,
        start_time: datetime.datetime,
        duration: datetime.timedelta,
        participant_ids: list[UUID],
    ) -> Meeting:
        return Meeting(
            team_id=self.team_id,
            title=title,
            start_time=start_time,
            duration=duration,
            organizer_id=self.user_id,
            participant_ids=participant_ids,
            is_new_meeting=True,
        )

    def access_meeting(self, meeting: Meeting) -> Meeting:
        meeting.inspect(self.user_id, override=self.can_override_meeting)
        return meeting

    @_permission_required
    def rename_team(self, team: "Team", new_name: str) -> "Team":
        team.rename(new_name)
        return team

    @property
    def is_team_owner(self):
        return self.role == TeamRole.OWNER

    @property
    def is_team_admin(self):
        return self.role == TeamRole.ADMIN

    @property
    def is_team_manager(self):
        return self.role == TeamRole.MANAGER

    @property
    def is_team_employee(self):
        return self.role == TeamRole.EMPLOYEE

    @_permission_required
    def remove_invite_code(self): ...


@dataclass
class TeamInvite(FromObjectMixin):
    team_id: UUID
    creator_id: UUID
    creator: User | None = None
    expires_at: datetime.datetime = (
        settings.datetime_now() + settings.invite_expiration_time
    )
    max_uses: int = 1
    used_count: int = 0
    code: UUID = field(default_factory=uuid4)

    def use(self):
        if self.is_expired:
            raise DomainError("Invite expired")
        if self.max_uses <= self.used_count:
            raise DomainError("No remaining uses")
        self.used_count += 1

    @property
    def is_expired(self) -> bool:
        return settings.datetime_now() > self.expires_at


class TeamRepository(ABC):
    @abstractmethod
    async def get_team(self, team_id: UUID) -> Team | None: ...

    @abstractmethod
    async def list_teams(
        self, member_id: UUID | None = None
    ) -> list[Team]: ...

    @abstractmethod
    async def save_team(self, team: Team) -> Team: ...

    @abstractmethod
    async def get_member(
        self, team_id: UUID, user_id: UUID
    ) -> TeamMember | None: ...

    @abstractmethod
    async def save_member(self, member: TeamMember) -> TeamMember: ...

    @abstractmethod
    async def delete_member(self, member: TeamMember) -> None: ...

    @abstractmethod
    async def list_members(self, team_id: UUID) -> list[TeamMember]: ...

    @abstractmethod
    async def get_invite(
        self,
        code: UUID,
        expires_at: datetime.datetime | None = None,
        is_used_up: bool | None = None,
    ) -> TeamInvite | None: ...

    @abstractmethod
    async def save_invite(self, invite: TeamInvite) -> TeamInvite: ...

    @abstractmethod
    async def delete_invite(self, code: UUID) -> None: ...
