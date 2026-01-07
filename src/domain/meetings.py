from datetime import datetime, timedelta
from uuid import UUID, uuid4
from src.domain.utils import FromObjectMixin
from src.domain.users import User
from src.domain.teams import Team
from src.exceptions import ForbiddenDomainError, DomainError

from abc import ABC, abstractmethod

from dataclasses import dataclass, field

from src.settings import settings


class MeetingError(DomainError): ...


class MeetingCancelError(MeetingError): ...


class MeetingNotOrganizerError(MeetingCancelError, ForbiddenDomainError): ...


class MeetingOverlapsError(MeetingError): ...


class MeetingStartTimePassedError(MeetingError): ...


class MeetingDurationTooShortError(MeetingError): ...


class MeetingAlreadyCancelledError(MeetingError): ...


class MeetingNotInitializedError(MeetingError): ...


class MeetingNotParticipantError(MeetingError, ForbiddenDomainError): ...


@dataclass(frozen=True)
class MeetingParticipant(FromObjectMixin):
    participant_id: UUID
    meeting_id: UUID
    participant: User | None = None


@dataclass
class Meeting(FromObjectMixin):
    """
    Represents a meeting with participants, organizer, and scheduling details.
    """

    team_id: UUID
    title: str
    start_time: datetime
    duration: timedelta
    organizer_id: UUID
    organizer: User | None = None
    id: UUID = field(default_factory=uuid4)
    participants: list[MeetingParticipant] = field(default_factory=list)
    participant_ids: list[UUID] = field(default_factory=list)
    team: Team | None = None
    cancelled: bool = False
    cancelled: bool = False
    is_new_meeting: bool = False

    def __post_init__(self):
        # ? Already created meeting post init

        if not self.participant_ids and self.participants:
            self.participant_ids = [
                participant.participant_id for participant in self.participants
            ]

        if not self.is_new_meeting:
            return

        # ? New meeting constraints related

        if self.start_time < settings.datetime_now():
            raise MeetingStartTimePassedError(
                "Meeting can not be initialized in the past."
            )

        if self.duration <= timedelta(0):
            raise MeetingDurationTooShortError("Meeting duration too short")

    @property
    def end_time(self):
        return self.start_time + self.duration

    @property
    def organizer_as_participant(self) -> MeetingParticipant:
        return MeetingParticipant(self.organizer_id, self.id)

    @property
    def provided_participants(self) -> list[MeetingParticipant]:
        return [MeetingParticipant(id, self.id) for id in self.participant_ids]

    @property
    def unique_participants(self) -> list[MeetingParticipant]:
        return list(set([self.organizer_as_participant] + self.provided_participants))

    @property
    def is_awaited(self):
        return self.start_time > settings.datetime_now()

    @property
    def is_ended(self):
        return self.end_time < settings.datetime_now()

    @property
    def is_live(self):
        return not self.is_awaited and not self.is_ended

    def is_participant(self, user_id: UUID) -> bool:
        return user_id in [
            participant.participant_id for participant in self.unique_participants
        ]

    def inspect(self, invoker_id: UUID, override: bool) -> "Meeting":
        if not override:
            if not self.is_participant(invoker_id):
                raise MeetingNotParticipantError("Can not inspect this meeting")
        return self

    def validate_organizer(self, user_id: UUID, exc_details: str | None = None):
        if not self.organizer_id == user_id:
            raise MeetingCancelError(exc_details)

    def cancel(self, invoker_id: UUID, override: bool):
        if not override:
            self.validate_organizer(invoker_id, "Only task organizer can cancel a task")
        if self.cancelled:
            raise MeetingAlreadyCancelledError("Meeting already cancelled")

        self.cancelled = True


class MeetingRepository(ABC):
    @abstractmethod
    async def save_meeting(self, meeting: Meeting) -> Meeting: ...

    @abstractmethod
    async def get_meeting(self, meeting_id: UUID) -> Meeting | None: ...

    @abstractmethod
    async def list_meetings(
        self,
        participant_id: UUID,
        team_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        cancelled: bool | None = None,
        live: bool = False,
    ) -> list[Meeting]: ...

    @abstractmethod
    async def list_overlaps(
        self,
        team_id: UUID,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Meeting]: ...

    @abstractmethod
    async def bulk_save_participants(
        self, participants: list[MeetingParticipant]
    ) -> list[MeetingParticipant]: ...

    @abstractmethod
    async def list_participants(self, meeting_id: UUID) -> list[MeetingParticipant]: ...
