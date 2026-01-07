from src.services.tasks.base import GetMemberDependantTaskUseCase
from src.domain.tasks import Task

import datetime

from uuid import UUID


class CreateTaskUseCase(GetMemberDependantTaskUseCase):

    async def execute(
        self,
        team_id: UUID,
        invoker_id: UUID,
        title: str,
        deadline: datetime.datetime,
        description: str | None = None,
        assignee_id: UUID | None = None,
        period_offset: datetime.timedelta | None = None,
    ) -> Task:
        invoker_member = await self.get_member.execute(team_id, invoker_id)
        new_task = invoker_member.create_task(
            title, deadline, description, assignee_id, period_offset
        )
        if assignee_id:
            await self.get_member.execute(team_id, assignee_id)
            new_task.assign(invoker_id, assignee_id, invoker_member.can_override_task)

        return await self.task_repo.save_task(new_task)
