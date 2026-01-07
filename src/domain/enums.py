from enum import Enum


class TaskStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskScore(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class TeamRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"
    OWNER = "owner"

    @classmethod
    def _wildcard_permission(cls) -> str:
        return "all"

    @classmethod
    def _permissions(cls) -> dict["TeamRole", set[str]]:
        return {
            cls.OWNER: {
                "all",
            },
            cls.ADMIN: {
                "task_override",
                "meeting_override",
                "generate_invite_code",
                "inspect_invite_codes",
                "remove_invite_code",
                "add_member",
                "remove_member",
                "change_role",
                "create_task",
                "create_meeting",
            },
            cls.MANAGER: {
                "generate_invite_code",
                "inspect_invite_codes",
                "remove_invite_code",
                "add_member",
                "create_task",
                "create_meeting",
            },
            cls.EMPLOYEE: set(),
        }

    @classmethod
    def _protected(cls) -> set["TeamRole"]:
        return {cls.OWNER}

    def is_protected(self) -> bool:
        return self in self._protected()

    def has_permission(self, action: str) -> bool:
        actions = self._permissions().get(self, set())
        return action in actions or self._wildcard_permission() in actions

    def can_affect_other_role(self, target_role: "TeamRole") -> bool:
        hierarchy = {
            self.OWNER: 3,
            self.ADMIN: 2,
            self.MANAGER: 1,
            self.EMPLOYEE: 0,
        }
        return hierarchy[self] > hierarchy[target_role]


class UserRole(str, Enum):
    DEFAULT = "default"
    MANAGER = "manager"
    ADMIN = "admin"

    @property
    def priority(self) -> int:
        role_priority = {
            UserRole.DEFAULT: 0,
            UserRole.MANAGER: 1,
            UserRole.ADMIN: 2,
        }
        return role_priority[self]

    def can_grant(self, role: "UserRole") -> bool:
        return self.priority >= role.priority

    def can_modify(self, other: "UserRole") -> bool:
        return self.priority > other.priority


class CalendarScope(str, Enum):
    SINGLE_DAY = "day"
    SINGLE_MONTH = "month"


class CalendarEventType(str, Enum):
    TASK = "task"
    MEETING = "meeting"
    UNKNOWN = "unknown"
