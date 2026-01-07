from src.services.meetings.base import GetMemberDependantMeetingUseCase

from src.domain.meetings import Meeting
from src.domain.teams import TeamMember

from uuid import UUID

from src.exceptions import NotFoundDomainError


class MeeetingNotFoundError(NotFoundDomainError): ...


class GetMeetingUseCase(GetMemberDependantMeetingUseCase):

    async def execute(
        self, invoker_id: UUID, meeting_id: UUID
    ) -> tuple[TeamMember, Meeting]:
        if not (meeting := await self.meeting_repo.get_meeting(meeting_id=meeting_id)):
            raise MeeetingNotFoundError("Meeting not found")
        invoker_member = await self.get_member.execute(meeting.team_id, invoker_id)
        invoker_member.access_meeting(meeting)
        return invoker_member, meeting
