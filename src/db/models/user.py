from src.db.models import Base
from src.db.dependency import get_db_session
from fastapi import Depends
from fastapi_users.db import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, Enum
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import TIMESTAMP

from src.settings import settings

from src.domain.enums import UserRole


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model for FastAPI Users."""

    __tablename__ = "users"
    created_at = mapped_column(
        TIMESTAMP(timezone=True),
        default=settings.datetime_now,
    )
    first_name = mapped_column(String(50), nullable=True)
    last_name = mapped_column(String(50), nullable=True)
    role = mapped_column(Enum(UserRole), nullable=False, default=UserRole.DEFAULT)

    team_memberships = relationship("TeamMember", back_populates="user", uselist=True)
    meetings = relationship(
        "MeetingParticipant", back_populates="participant", uselist=True
    )
    invites = relationship("TeamInvite", back_populates="creator")

    @hybrid_property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @hybrid_property
    def is_manager(self):
        return self.role == UserRole.MANAGER


async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)
