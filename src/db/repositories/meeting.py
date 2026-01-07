from uuid import UUID
from src.domain.meetings import MeetingRepository, Meeting, MeetingParticipant
from src.domain.users import User
from src.domain.teams import Team

from src.db.models.meeting import (
    Meeting as MeetingDB,
    MeetingParticipant as MeetingParticipantDB,
)
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from src.settings import settings
from sqlalchemy import cast, Interval, TIMESTAMP


class SQLAMeetingRepository(MeetingRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_meeting(self, meeting: Meeting) -> Meeting:
        return Meeting.from_object(
            await self.session.merge(
                MeetingDB.from_dataclass(
                    meeting,
                    ignore_fields=["participants", "organizer", "team"],
                )
            ),
        )

    async def get_meeting(self, meeting_id: UUID) -> Meeting | None:
        db_meeting = await self.session.get(MeetingDB, meeting_id)
        return (
            Meeting.from_object(
                db_meeting,
                convert_relation_fields=[
                    ("participants", MeetingParticipant),
                    ("organizer", User),
                    ("team", Team),
                ],
                participants=[("participant", User)],
            )
            if db_meeting
            else None
        )

    async def list_meetings(
        self,
        participant_id: UUID,
        team_id: UUID | None = None,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
        cancelled: bool | None = None,
        live: bool = False,
    ) -> list[Meeting]:
        query = (
            select(MeetingDB)
            .join(
                MeetingParticipantDB,
                MeetingDB.id == MeetingParticipantDB.meeting_id,
            )
            .where(MeetingParticipantDB.participant_id == participant_id)
        )

        if live:
            now = settings.datetime_now()
            query = query.where(
                MeetingDB.cancelled.is_(False),
                MeetingDB.start_time <= now,
                cast(
                    MeetingDB.start_time + MeetingDB.duration,
                    TIMESTAMP(timezone=True),
                )
                >= now,
            )
        else:
            if start_date:
                query = query.where(MeetingDB.start_time >= start_date)
            if end_date:
                query = query.where(
                    cast(
                        MeetingDB.start_time + cast(MeetingDB.duration, Interval),
                        TIMESTAMP(timezone=True),
                    )
                    <= end_date
                )
            if cancelled is not None:
                query = query.where(MeetingDB.cancelled.is_(cancelled))

        if team_id:
            query = query.where(MeetingDB.team_id == team_id)

        result = await self.session.execute(query)

        return [
            Meeting.from_object(
                meeting,
                convert_relation_fields=[
                    ("participants", MeetingParticipant),
                    ("team", Team),
                ],
            )
            for meeting in result.scalars().unique().all()
        ]

    async def list_overlaps(
        self,
        team_id: UUID,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> list[Meeting]:
        query = (
            select(MeetingDB)
            .where(MeetingDB.team_id == team_id)
            .where(MeetingDB.cancelled.is_(False))
            .where(
                (MeetingDB.start_time < end_time)
                & (
                    cast(
                        MeetingDB.start_time + cast(MeetingDB.duration, Interval),
                        TIMESTAMP(timezone=True),
                    )
                    > start_time
                )
            )
        )

        result = await self.session.execute(query)

        return [
            Meeting.from_object(meeting) for meeting in result.scalars().unique().all()
        ]

    async def bulk_save_participants(
        self, participants: list[MeetingParticipant]
    ) -> list[MeetingParticipant]:
        if not participants:
            return []
        meeting_id = participants[0].meeting_id

        # ? Prepare a list of a participants as a db models
        db_participants = [
            MeetingParticipantDB.from_dataclass(p, ignore_fields=["participant"])
            for p in participants
        ]

        # ? Add all of them to the session
        self.session.add_all(db_participants)

        # ? Make newly created paticipants appear in list_participants() before session is closed
        await self.session.flush()

        return await self.list_participants(meeting_id)

    async def list_participants(self, meeting_id: UUID) -> list[MeetingParticipant]:
        result = await self.session.execute(
            select(MeetingParticipantDB).where(
                MeetingParticipantDB.meeting_id == meeting_id
            )
        )
        # ? If there are no participant with given meeting_id,
        # ? list comprehension would return an empty list
        return [
            MeetingParticipant.from_object(db_participant)
            for db_participant in result.scalars().all()
        ]
