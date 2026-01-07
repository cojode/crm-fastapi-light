from src.services.meetings.base import MeetingUseCase

from uuid import UUID


import datetime


class ListMeetingsUseCase(MeetingUseCase):

    async def execute(
        self,
        invoker_id: UUID,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
        cancelled: bool | None = None,
        live: bool = False,
    ):
        return await self.meeting_repo.list_meetings(
            participant_id=invoker_id,
            start_date=start_date,
            end_date=end_date,
            cancelled=cancelled,
            live=live,
        )
