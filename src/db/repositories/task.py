from src.db.models.task import Task as TaskDB, TaskComment as TaskCommentDB
from src.domain.users import User
from src.domain.teams import Team

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from src.domain.tasks import TaskRepository, Task, TaskComment
from src.domain.enums import TaskStatus

from uuid import UUID

import datetime


class SQLATaskRepository(TaskRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_task(self, task: Task) -> Task:
        return Task.from_object(
            await self.session.merge(
                TaskDB.from_dataclass(
                    task,
                    ignore_fields=[
                        "comments",
                        "assignee",
                        "author",
                        "created_at",
                        "team",
                    ],
                )
            )
        )

    async def get_task(self, task_id: UUID) -> Task | None:
        db_task = await self.session.get(TaskDB, task_id)
        return (
            Task.from_object(
                db_task,
                [
                    ("comments", TaskComment),
                    ("assignee", User),
                    ("author", User),
                    ("team", Team),
                ],
                comments=[("author", User)],
            )
            if db_task
            else None
        )

    async def list_tasks(
        self,
        statuses: list[TaskStatus],
        author_id: UUID | None,
        assignee_id: UUID | None,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
    ) -> list[Task]:
        stmt = select(TaskDB)
        if author_id is not None:
            stmt = stmt.where(TaskDB.author_id == author_id)
        if assignee_id is not None:
            stmt = stmt.where(TaskDB.assignee_id == assignee_id)
        if start_date is not None:
            stmt = stmt.where(TaskDB.deadline >= start_date)
        if end_date is not None:
            stmt = stmt.where(TaskDB.deadline <= end_date)
        if statuses:
            stmt = stmt.where(TaskDB.status.in_(statuses))
        result = await self.session.execute(stmt)
        return [
            Task.from_object(
                db_task,
                [("assignee", User), ("author", User), ("team", Team)],
            )
            for db_task in result.scalars().unique().all()
        ]

    async def delete_task(self, task: Task) -> None:
        await self.session.execute(delete(TaskDB).where(TaskDB.id == task.id))

    async def save_comment(self, comment: TaskComment) -> TaskComment:
        return TaskComment.from_object(
            await self.session.merge(
                TaskCommentDB.from_dataclass(comment, ignore_fields=["author"])
            )
        )

    async def list_comments(self, task_id: UUID) -> list[TaskComment]:
        result = await self.session.execute(
            select(TaskCommentDB).where(TaskCommentDB.task_id == task_id)
        )
        return [
            TaskComment.from_object(db_comment) for db_comment in result.scalars().all()
        ]
