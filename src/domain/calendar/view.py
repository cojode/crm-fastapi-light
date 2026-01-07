import datetime
from src.domain.calendar.day import DailyCalendarView
from src.domain.calendar.month import MonthlyCalendarView
from src.domain.calendar.base import CalendarView
from src.domain.enums import CalendarScope
import calendar


class CalendarViewBuilder:
    @staticmethod
    def create_daily_view(date: datetime.date) -> DailyCalendarView:
        dt = datetime.datetime.combine(date, datetime.time.min)
        return DailyCalendarView(
            scope=CalendarScope.SINGLE_DAY,
            start_date=dt,
            end_date=dt + datetime.timedelta(days=1),
        )

    @staticmethod
    def create_monthly_view(date: datetime.date) -> MonthlyCalendarView:
        dt = datetime.datetime.combine(date, datetime.time.min)
        last_day = calendar.monthrange(date.year, date.month)[1]
        end_date = datetime.date(date.year, date.month, last_day)
        end_dt = datetime.datetime.combine(end_date, datetime.time.max)

        return MonthlyCalendarView(
            scope=CalendarScope.SINGLE_MONTH,
            start_date=dt,
            end_date=end_dt,
        )

    @staticmethod
    def create_provided_view(
        date: datetime.date, scope: CalendarScope
    ) -> CalendarView | None:
        scoped_views = {
            CalendarScope.SINGLE_DAY: CalendarViewBuilder.create_daily_view,
            CalendarScope.SINGLE_MONTH: CalendarViewBuilder.create_monthly_view,
        }
        view_creator = scoped_views.get(scope)
        return view_creator(date) if view_creator else None
