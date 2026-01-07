from src.services.tasks.base import GetTaskDependantTaskUseCase

from src.domain.tasks import Task
from src.domain.enums import TaskScore

from uuid import UUID


class RateTaskUseCase(GetTaskDependantTaskUseCase):
    async def execute(self, invoker_id: UUID, task_id: UUID, score: TaskScore) -> Task:
        invoker_member, task = await self.get_task.execute(
            invoker_id=invoker_id, task_id=task_id
        )
        task.rate(invoker_id, score, override=invoker_member.can_override_task)
        return await self.task_repo.save_task(task)
