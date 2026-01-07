from src.services.tasks.base import GetTaskDependantTaskUseCase

from src.domain.tasks import Task

from uuid import UUID

import datetime

from src.logger import logger


class UpdateTaskUseCase(GetTaskDependantTaskUseCase):

    async def execute(
        self,
        invoker_id: UUID,
        task_id: UUID,
        title: str | None = None,
        description: str | None = None,
        deadline: datetime.datetime | None = None,
        assignee_id: UUID | None = None,
    ) -> Task:
        invoker_member, task = await self.get_task.execute(
            invoker_id=invoker_id, task_id=task_id
        )
        with_assignee_reset = (
            task.assignee_id != assignee_id and assignee_id is not None
        )

        task.update(
            invoker_id,
            title,
            description,
            deadline,
            override=invoker_member.can_override_task,
            reset_task=with_assignee_reset,
        )
        if with_assignee_reset:
            logger.debug("reset")
            task.assign(
                invoker_id,
                assignee_id,
                invoker_member.has_permission("can_task_override"),
            )

        return await self.task_repo.save_task(task)
