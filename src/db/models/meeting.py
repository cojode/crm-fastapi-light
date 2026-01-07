from src.db.models import Base

from sqlalchemy import (
    String,
    ForeignKey,
    Interval,
    TIMESTAMP,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column

from uuid import uuid4

from src.settings import settings


class Meeting(Base):

    __tablename__ = "meetings"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: uuid4(),  # pylint: disable=W0108
    )
    title = mapped_column(String(100), nullable=False)

    start_time = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), default=settings.datetime_now)
    duration = mapped_column(Interval, nullable=False)

    cancelled = mapped_column(Boolean, nullable=False, default=False)

    team_id = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    organizer_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    organizer = relationship("User", foreign_keys=[organizer_id], lazy="selectin")

    team = relationship("Team", foreign_keys=[team_id], lazy="selectin")

    participants = relationship(
        "MeetingParticipant",
        back_populates="meeting",
        uselist=True,
        lazy="selectin",
        cascade="all,delete",
    )


class MeetingParticipant(Base):

    __tablename__ = "meeting_participants"

    __table_args__ = (
        UniqueConstraint(
            "participant_id",
            "meeting_id",
            name="meeting_paticipants_composite",
        ),
    )

    participant_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    meeting_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("meetings.id"), primary_key=True
    )

    meeting = relationship("Meeting", back_populates="participants")

    participant = relationship("User", back_populates="meetings", lazy="selectin")
