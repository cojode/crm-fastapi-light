from src.services.tasks.base import GetTaskMemberDependantTaskUseCase

from src.domain.tasks import Task

from uuid import UUID


class AssignToTaskUseCase(GetTaskMemberDependantTaskUseCase):
    async def execute(self, invoker_id: UUID, task_id: UUID, assignee_id: UUID) -> Task:
        invoker_member, task = await self.get_task.execute(
            invoker_id=invoker_id, task_id=task_id
        )

        await self.get_member.execute(task.team_id, assignee_id)

        task.assign(invoker_id, assignee_id, override=invoker_member.can_override_task)

        return await self.task_repo.save_task(task)
