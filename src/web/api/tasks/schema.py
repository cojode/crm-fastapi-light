from pydantic import BaseModel, ConfigDict

from uuid import UUID
import datetime

from src.domain.tasks import TaskComment
from src.domain.enums import TaskScore, TaskStatus
from src.schemas import GenericResponse, GenericListResponse


class CreateTaskRequest(BaseModel):
    team_id: UUID
    title: str
    deadline: datetime.datetime
    description: str | None = None


class AssignToTaskRequest(BaseModel):
    assignee_id: UUID


class RateTaskRequest(BaseModel):
    score: TaskScore


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime.datetime | None = None


class TaskCommentRequest(BaseModel):
    text: str


class TaskModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    deadline: datetime.datetime

    author_id: UUID
    team_id: UUID
    assignee_id: UUID | None
    created_at: datetime.datetime | None
    description: str | None
    status: TaskStatus = TaskStatus.OPEN
    score: TaskScore | None = None


class SingleTaskResponse(GenericResponse[TaskModel]): ...


class ManyTasksResponse(GenericListResponse[TaskModel]): ...


class ListOwnedTasksResponse(ManyTasksResponse): ...


class ListAssignedTasksResponse(ManyTasksResponse): ...


class CreateTaskResponse(SingleTaskResponse): ...


class GetTaskResponse(SingleTaskResponse): ...


class UpdateTaskResponse(SingleTaskResponse): ...


class AssignToTaskResponse(SingleTaskResponse): ...


class CompleteTaskResponse(SingleTaskResponse): ...


class RateTaskResponse(SingleTaskResponse): ...


class TaskCommentResponse(GenericResponse[TaskComment]): ...
