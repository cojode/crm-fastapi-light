from sqlalchemy import String, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.types import TIMESTAMP
from src.db.models import Base

from src.settings import settings

from src.domain.enums import TaskStatus, TaskScore

from uuid import uuid4


class Task(Base):
    __tablename__ = "tasks"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: uuid4(),  # pylint: disable=W0108
    )
    title = mapped_column(String(100), nullable=False)
    description = mapped_column(Text)
    deadline = mapped_column(TIMESTAMP(timezone=True))
    status = mapped_column(Enum(TaskStatus), default=TaskStatus.OPEN, nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), default=settings.datetime_now)
    score = mapped_column(Enum(TaskScore), nullable=True)
    updated_at = mapped_column(
        TIMESTAMP(timezone=True),
        default=settings.datetime_now,
        onupdate=settings.datetime_now,
    )

    author_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    assignee_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    team_id = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)

    author = relationship("User", foreign_keys=[author_id], lazy="selectin")
    assignee = relationship("User", foreign_keys=[assignee_id], lazy="selectin")
    team = relationship("Team", foreign_keys=[team_id], lazy="selectin")
    comments = relationship(
        "TaskComment",
        back_populates="task",
        uselist=True,
        lazy="selectin",
        cascade="all,delete",
    )


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    text = mapped_column(Text, nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), default=settings.datetime_now)

    author_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    author = relationship("User", foreign_keys=[author_id], lazy="selectin")
    task = relationship("Task", back_populates="comments")
