from sqlalchemy import String, Integer, ForeignKey, UUID, Enum
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from src.db.models import Base

from src.settings import settings
from uuid import uuid4

from src.domain.enums import TeamRole


class Team(Base):
    __tablename__ = "teams"

    id = mapped_column(UUID, primary_key=True, default=uuid4)
    name = mapped_column(String(100), nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), default=settings.datetime_now)

    members = relationship(
        "TeamMember", back_populates="team", uselist=True, lazy="joined"
    )
    invites = relationship(
        "TeamInvite", back_populates="team", uselist=True, lazy="joined"
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = mapped_column(UUID, ForeignKey("teams.id"), primary_key=True)
    user_id = mapped_column(UUID, ForeignKey("users.id"), primary_key=True)
    role = mapped_column(Enum(TeamRole), default=TeamRole.EMPLOYEE, nullable=False)
    joined_at = mapped_column(TIMESTAMP(timezone=True), default=settings.datetime_now)

    user = relationship("User", back_populates="team_memberships", lazy="joined")
    team = relationship("Team", back_populates="members")


class TeamInvite(Base):
    __tablename__ = "team_invites"

    code = mapped_column(UUID, default=str(uuid4()), primary_key=True)
    creator_id = mapped_column(UUID, ForeignKey("users.id"))
    team_id = mapped_column(UUID, ForeignKey("teams.id"))
    expires_at = mapped_column(TIMESTAMP(timezone=True))
    max_uses = mapped_column(Integer, default=1)
    used_count = mapped_column(Integer, default=0)

    creator = relationship("User", back_populates="invites", lazy="joined")
    team = relationship("Team", back_populates="invites")
