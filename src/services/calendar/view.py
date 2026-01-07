from src.services.tasks.list_tasks import ListTasksUseCase
from src.services.meetings.list_meetings import ListMeetingsUseCase

from uuid import UUID
import datetime
from src.domain.enums import CalendarScope
from src.domain.calendar import CalendarViewBuilder
from src.exceptions import DomainError


class CalendarViewError(DomainError): ...


class UnknownCalendarScopeError(DomainError): ...


class CalendarViewUseCase:
    def __init__(
        self,
        list_tasks_use_case: ListTasksUseCase,
        list_meetings_use_case: ListMeetingsUseCase,
    ):
        self.list_tasks = list_tasks_use_case
        self.list_meetings = list_meetings_use_case

    async def execute(
        self,
        invoker_id: UUID,
        source_datetime: datetime.datetime,
        scope: CalendarScope,
    ):
        calendar = CalendarViewBuilder.create_provided_view(source_datetime, scope)
        if not calendar:
            raise UnknownCalendarScopeError("Unknown calendar scope")

        assigned_tasks, authored_tasks, meetings = (
            await self.list_tasks.execute(
                assignee_id=invoker_id,
                start_date=calendar.start_date,
                end_date=calendar.end_date,
            ),
            await self.list_tasks.execute(
                author_id=invoker_id,
                start_date=calendar.start_date,
                end_date=calendar.end_date,
            ),
            await self.list_meetings.execute(
                invoker_id=invoker_id,
                start_date=calendar.start_date,
                end_date=calendar.end_date,
            ),
        )

        calendar.add_events(*assigned_tasks + authored_tasks + meetings)

        return calendar.view()
