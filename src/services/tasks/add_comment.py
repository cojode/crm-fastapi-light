from src.services.tasks.base import GetTaskDependantTaskUseCase

from src.domain.tasks import TaskComment

from uuid import UUID


class AddCommentUseCase(GetTaskDependantTaskUseCase):
    async def execute(self, invoker_id: UUID, task_id: UUID, text: str) -> TaskComment:
        invoker_member, task = await self.get_task.execute(
            invoker_id=invoker_id, task_id=task_id
        )

        comment = task.comment(
            invoker_id, text, override=invoker_member.can_override_task
        )

        return await self.task_repo.save_comment(comment)
