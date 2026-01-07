from src.services.tasks.base import GetMemberDependantTaskUseCase
from src.domain.tasks import Task
from src.domain.teams import TeamMember

from uuid import UUID

from src.exceptions import NotFoundDomainError


class TaskNotFoundError(NotFoundDomainError): ...


class GetTaskUseCase(GetMemberDependantTaskUseCase):

    async def execute(
        self,
        invoker_id: UUID,
        task_id: UUID,
    ) -> tuple[TeamMember, Task]:
        """Get existing task and related invoker team member, who can access the task.
        User can access task if:
        1. Task exists.
        2. Task's team_id crosses with any user's team membership.
        3. User has "access_task_override" permission
        OR user is an author or an assignee of a task.

        """
        # ? get task from repo
        if not (task := await self.task_repo.get_task(task_id)):
            raise TaskNotFoundError("Task not found.")
        # ? verify provided invoker is a part of a team of a following task
        invoker_member = await self.get_member.execute(task.team_id, invoker_id)
        # ? verify provided team member have access to a task
        invoker_member.access_task(task)

        return invoker_member, task
