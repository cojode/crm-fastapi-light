from uuid import UUID, uuid4
import datetime

from src.domain.users import User
from src.domain.enums import TaskScore, TaskStatus
from src.exceptions import DomainError, ForbiddenDomainError
from src.domain.teams import Team
from src.domain.utils import FromObjectMixin

from abc import ABC, abstractmethod

from dataclasses import dataclass, field

from src.settings import settings


class TaskError(DomainError): ...


class TaskNotAssignableError(TaskError): ...


class TaskNotIdentifiedError(TaskError): ...


class TaskNotCompletableError(TaskError): ...


class TaskNotCompleteError(TaskError): ...


class TaskAccessError(TaskError, ForbiddenDomainError): ...


class TaskAssigneeMismatchError(TaskAccessError): ...


class TaskAuthorMismatchError(TaskAccessError): ...


@dataclass
class TaskComment(FromObjectMixin):
    text: str
    task_id: UUID
    author_id: UUID
    created_at: datetime.datetime | None = None
    author: User | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class Task(FromObjectMixin):
    title: str
    deadline: datetime.datetime

    author_id: UUID
    team_id: UUID
    assignee_id: UUID | None = None

    created_at: datetime.datetime | None = None
    period_offset: datetime.timedelta | None = None
    author: User | None = None
    assignee: User | None = None
    description: str | None = None
    status: TaskStatus = TaskStatus.OPEN
    score: TaskScore | None = None
    team: Team | None = None
    comments: list[TaskComment] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    @property
    def is_assignable(self) -> bool:
        return self.status == TaskStatus.OPEN

    @property
    def is_completable(self):
        return self.status == TaskStatus.IN_PROGRESS

    @property
    def is_completed(self):
        return self.status == TaskStatus.COMPLETED

    @property
    def is_expired(self):
        return self.deadline < settings.datetime_now()

    # @property
    # def is_periodic(self):
    #     return self.period_offset is not None

    # @property
    # def next_deadline(self) -> datetime.datetime | None:
    #     if not self.is_periodic or self.period_offset is None:
    #         return None
    #     return self.deadline + self.period_offset

    # @property
    # def next_periodic_task(self) -> "Task | None":
    #     if not self.is_periodic:
    #         return None
    #     next_deadline = self.next_deadline
    #     if next_deadline is None:
    #         return None
    #     new_task_dict = dict(self.__dict__)
    #     new_task_dict["deadline"] = next_deadline
    #     return Task(**new_task_dict)

    # def as_period_list(self, period_limit: datetime.datetime) -> list["Task"]:
    #     result: list["Task"] = [self]
    #     if not self.is_periodic:
    #         return result
    #     current_task = self
    #     while current_task and current_task.deadline < period_limit:
    #         result.append(current_task)
    #         current_task = current_task.next_periodic_task
    #     return result

    def is_author(self, user_id: UUID):
        return self.author_id == user_id

    def is_assignee(self, user_id: UUID):
        return self.assignee_id == user_id

    def is_related(self, user_id: UUID):
        return user_id in {self.assignee_id, self.author_id}

    def verify_author(self, user_id: UUID, exc_details: str | None = None):
        if not self.is_author(user_id):
            raise TaskAuthorMismatchError(exc_details)

    def verify_assignee(self, user_id: UUID, exc_details: str | None = None):
        if not self.is_assignee(user_id):
            raise TaskAssigneeMismatchError(exc_details)

    def verify_related(self, user_id: UUID, exc_details: str | None = None):
        if not self.is_related(user_id):
            raise TaskAccessError(exc_details)

    def inspect(self, user_id: UUID, override: bool = False) -> "Task":
        if not override:
            self.verify_related(
                user_id, "Task can be accessed only by an author and assignee"
            )

        return self

    def reset_status(self):
        self.status = TaskStatus.OPEN

    def reset_score(self):
        self.score = None

    def update(
        self,
        invoker_id: UUID,
        title: str | None = None,
        description: str | None = None,
        deadline: datetime.datetime | None = None,
        override: bool = False,
        reset_task: bool = False,
    ):
        if not override:
            self.verify_author(invoker_id, "Only task author can update task")
        self.title = title if title is not None else self.title
        self.description = description if description is not None else self.description
        self.deadline = deadline if deadline is not None else self.deadline
        if reset_task:
            self.reset_status()
            self.reset_score()

    def assign(self, invoker_id: UUID, assignee_id: UUID, override: bool = False):
        if not override:
            self.verify_author(invoker_id, "Only task author can assign to a task")
        if not self.is_assignable:
            raise TaskNotAssignableError("Task is not assignable")
        self.assignee_id = assignee_id
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, user_id: UUID, override: bool = False):
        if not override:
            self.verify_assignee(user_id, "Only task assignee can complete a task")
        if not self.is_completable:
            raise TaskNotCompletableError("Task could not be completed")
        self.status = TaskStatus.COMPLETED

    def delete(self, invoker_id: UUID, override: bool = False):
        if not override:
            self.verify_author(invoker_id, "Only task author can delete a task")

    def rate(self, invoker_id: UUID, score: TaskScore, override: bool = False):
        if not override:
            self.verify_author(invoker_id, "Only task author can rate a task")
        if not self.is_completed:
            raise TaskNotCompleteError("Task is not complete to be rated yet")
        self.score = score

    def comment(self, invoker_id: UUID, text: str, override: bool) -> TaskComment:
        if not self.id:
            raise TaskNotIdentifiedError("Task is not identified")
        if not override:
            self.verify_related(
                invoker_id,
                "Comment can be created only by an author and assignee",
            )
        return TaskComment(text, self.id, invoker_id)


class TaskRepository(ABC):
    @abstractmethod
    async def save_task(self, task: Task) -> Task: ...

    @abstractmethod
    async def get_task(self, task_id: UUID) -> Task | None: ...

    @abstractmethod
    async def list_tasks(
        self,
        statuses: list[TaskStatus],
        author_id: UUID | None,
        assignee_id: UUID | None,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
    ) -> list[Task]: ...

    @abstractmethod
    async def delete_task(self, task: Task) -> None: ...

    @abstractmethod
    async def save_comment(self, comment: TaskComment) -> TaskComment: ...

    @abstractmethod
    async def list_comments(self, task_id: UUID) -> list[TaskComment]: ...
