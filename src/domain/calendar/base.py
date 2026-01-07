from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.domain.calendar.event import (
    EventLikeEntity,
    CalendarEvent,
    CalendarEventFactory,
)
from src.domain.enums import CalendarScope
import datetime
from typing import Any
from src.settings import settings


@dataclass
class BaseSlot:
    events: list[CalendarEvent]

    @property
    def is_empty(self) -> bool:
        return len(self.events) == 0


@dataclass
class BaseViewData:
    date: datetime.datetime
    slots: list[Any]


@dataclass
class CalendarView(ABC):
    scope: CalendarScope
    start_date: datetime.datetime
    end_date: datetime.datetime
    events: list[CalendarEvent] = field(default_factory=list)

    def __post_init__(self):
        self.start_date = self.start_date.replace(tzinfo=settings.timezone_info)
        self.end_date = self.end_date.replace(tzinfo=settings.timezone_info)

    @property
    def duration(self) -> datetime.timedelta:
        return self.end_date - self.start_date

    @property
    def sorted_events(self) -> list[CalendarEvent]:
        return sorted(self.events, key=lambda e: e.start)

    def add_event(self, item: EventLikeEntity):
        calendar_event = CalendarEventFactory.create(item)
        if calendar_event not in self.events:
            self.events.append(calendar_event)

    def add_events(self, *items: EventLikeEntity):
        for item in items:
            self.add_event(item)

    @abstractmethod
    def view(self) -> BaseViewData: ...
