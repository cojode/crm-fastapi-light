from src.domain.calendar.event import CalendarEvent
from dataclasses import dataclass
import datetime
import calendar

from collections import defaultdict

from src.settings import settings

from src.domain.calendar.base import CalendarView, BaseViewData, BaseSlot

from typing import Sequence


@dataclass
class DaySlot(BaseSlot):
    day: int | None
    date: datetime.date | None
    is_current_month: bool
    is_today: bool
    events: list[CalendarEvent]

    @property
    def is_weekend(self) -> bool:
        return self.date is not None and self.date.weekday() in [5, 6]


@dataclass
class MonthlyViewData(BaseViewData):
    slots: list[list[DaySlot]]
    weekdays: Sequence[str] = calendar.day_name

    @property
    def month(self):
        return self.date.month

    @property
    def year(self):
        return self.date.year

    @property
    def month_name(self) -> str:
        return calendar.month_name[self.month]


@dataclass
class MonthlyCalendarView(CalendarView):
    def view(self) -> "MonthlyViewData":
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.start_date.year, self.start_date.month)
        today = settings.datetime_now()

        events_by_day = defaultdict(list)

        for event in self.sorted_events:
            day = event.start.date()
            events_by_day[day].append(event)

        weeks = []
        for week in month_days:
            week_days = []
            for day in week:
                date = (
                    datetime.date(self.start_date.year, self.start_date.month, day)
                    if day != 0
                    else None
                )

                new_slot = DaySlot(
                    day=day if day != 0 else None,
                    date=date,
                    is_current_month=day != 0,
                    is_today=date == today if date else False,
                    events=events_by_day.get(date, []),
                )

                week_days.append(new_slot)
            weeks.append(week_days)

        return MonthlyViewData(slots=weeks, date=self.start_date)
