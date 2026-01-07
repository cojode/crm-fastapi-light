from src.services.meetings.base import GetMeetingDependantMeetingUseCase

from src.domain.meetings import Meeting

from uuid import UUID


class CancelMeetingUseCase(GetMeetingDependantMeetingUseCase):
    async def execute(self, invoker_id: UUID, meeting_id: UUID) -> Meeting:
        invoker, meeting = await self.get_meeting.execute(invoker_id, meeting_id)
        meeting.cancel(invoker_id, invoker.can_override_meeting)
        saved_meeting = await self.meeting_repo.save_meeting(meeting)
        return saved_meeting
