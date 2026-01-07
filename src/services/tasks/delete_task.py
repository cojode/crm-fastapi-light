from src.services.tasks.base import GetTaskDependantTaskUseCase

from uuid import UUID


class DeleteTaskUseCase(GetTaskDependantTaskUseCase):
    async def execute(
        self,
        task_id: UUID,
        invoker_id: UUID,
    ) -> None:
        invoker_member, task = await self.get_task.execute(
            invoker_id=invoker_id, task_id=task_id
        )

        task.delete(invoker_id, override=invoker_member.can_override_task)

        await self.task_repo.delete_task(task)
