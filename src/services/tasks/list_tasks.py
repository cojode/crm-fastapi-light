from src.services.tasks.base import TaskUseCase
from src.domain.tasks import Task
from src.domain.enums import TaskStatus

from uuid import UUID
import datetime


class ListTasksUseCase(TaskUseCase):

    async def execute(
        self,
        statuses: list[str] | None = None,
        author_id: UUID | None = None,
        assignee_id: UUID | None = None,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
    ) -> list[Task]:
        return await self.task_repo.list_tasks(
            [TaskStatus(status) for status in statuses] if statuses else [],
            author_id,
            assignee_id,
            start_date,
            end_date,
        )
