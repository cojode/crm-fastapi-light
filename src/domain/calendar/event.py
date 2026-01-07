from dataclasses import dataclass, field
from typing import TypeAlias, Any
import datetime

from src.domain.tasks import Task
from src.domain.meetings import Meeting
from src.domain.enums import CalendarEventType
from abc import ABC, abstractmethod

from src.exceptions import DomainError

EventLikeEntity: TypeAlias = Task | Meeting


@dataclass
class BaseCalendarEvent(ABC):
    _event: Any
    type: CalendarEventType = field(init=False)

    def __post_init__(self):
        self.type = self._resolve_event_type()

    @abstractmethod
    def _resolve_event_type(self) -> CalendarEventType: ...

    @property
    @abstractmethod
    def start(self) -> datetime.datetime: ...

    @property
    @abstractmethod
    def end(self) -> datetime.datetime | None: ...

    @property
    def duration(self) -> datetime.timedelta | None:
        if not self.end:
            return None
        return self.end - self.start

    @property
    def is_interval(self) -> bool:
        return self.end is not None

    @property
    def is_single(self) -> bool:
        return not self.is_interval

    @property
    def event(self) -> Any:
        return self._event

    @property
    def is_meeting(self) -> bool:
        return self.type == CalendarEventType.MEETING

    @property
    def is_task(self) -> bool:
        return self.type == CalendarEventType.TASK


@dataclass
class TaskCalendarEvent(BaseCalendarEvent):
    _event: Task

    def _resolve_event_type(self) -> CalendarEventType:
        return CalendarEventType.TASK

    @property
    def start(self) -> datetime.datetime:
        return self._event.deadline

    @property
    def end(self) -> datetime.datetime | None:
        return None


@dataclass
class MeetingCalendarEvent(BaseCalendarEvent):
    _event: Meeting

    def _resolve_event_type(self) -> CalendarEventType:
        return CalendarEventType.MEETING

    @property
    def start(self) -> datetime.datetime:
        return self._event.start_time

    @property
    def end(self) -> datetime.datetime | None:
        return self._event.end_time


CalendarEvent: TypeAlias = TaskCalendarEvent | MeetingCalendarEvent


class CalendarEventFactoryError(DomainError): ...


class CalendarEventFactory:
    @staticmethod
    def create(event: object) -> CalendarEvent:
        if isinstance(event, Task):
            return TaskCalendarEvent(event)
        elif isinstance(event, Meeting):
            return MeetingCalendarEvent(event)
        raise CalendarEventFactoryError(f"Unsupported event type: {type(event)}")
