from dataclasses import dataclass
from src.domain.calendar.base import CalendarView, BaseViewData, BaseSlot

import calendar
from src.settings import settings

from collections import defaultdict
import datetime


@dataclass
class HourSlot(BaseSlot):
    hour: int
    is_now: bool


@dataclass
class DailyViewData(BaseViewData):
    @property
    def day_name(self) -> str:
        return calendar.day_name[self.date.weekday()]


@dataclass
class DailyCalendarView(CalendarView):
    def view(self) -> "DailyViewData":
        return DailyViewData(
            date=self.start_date,
            slots=self._get_hourly_schedule(),
        )

    @staticmethod
    def _is_exact_up_to_hour(a: datetime.datetime, b: datetime.datetime) -> bool:
        return a.replace(minute=0, second=0, microsecond=0) == b.replace(
            minute=0, second=0, microsecond=0
        )

    def _get_hourly_schedule(self) -> list["HourSlot"]:
        events_by_hour = defaultdict(list)
        for event in self.sorted_events:
            if event.end:
                # ? event with an end can last longer than an hour
                for hour in range(event.start.hour, event.end.hour + 1):
                    events_by_hour[hour].append(event)
            else:
                # ? defined only by a start hour
                events_by_hour[event.start.hour].append(event)
        hours = []
        from src.logger import logger

        logger.debug(settings.datetime_now())
        for hour in range(24):
            hours.append(
                HourSlot(
                    hour=hour,
                    events=events_by_hour.get(hour, []),
                    is_now=self._is_exact_up_to_hour(
                        self.start_date.replace(hour=hour),
                        settings.datetime_now(),
                    ),
                )
            )
        return hours
