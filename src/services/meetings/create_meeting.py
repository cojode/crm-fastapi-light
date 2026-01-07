from src.services.meetings.base import GetMemberDependantMeetingUseCase

from src.domain.meetings import Meeting, MeetingOverlapsError

from uuid import UUID

from datetime import datetime, timedelta

from src.logger import logger


class CreateMeetingUseCase(GetMemberDependantMeetingUseCase):
    async def execute(
        self,
        invoker_id: UUID,
        team_id: UUID,
        title: str,
        start_time: datetime,
        duration: timedelta,
        participant_ids: list[UUID],
    ) -> Meeting:
        # * 1. Get invoker as a member of a provided team
        invoker_member = await self.get_member.execute(team_id, invoker_id)
        # * 2. Make team member create meeting
        new_meeting = invoker_member.create_meeting(
            title=title,
            start_time=start_time,
            duration=duration,
            participant_ids=participant_ids,
        )
        end_time = start_time + duration
        # * 3. Verify new meeting not overlaps with other ones
        # * Meetings to check with: same team, in the same range
        overlaps = await self.meeting_repo.list_overlaps(
            team_id=team_id, start_time=start_time, end_time=end_time
        )

        logger.debug(overlaps)

        if overlaps:
            raise MeetingOverlapsError(
                "Can not create meeting - it overlaps with another"
            )
        # * 4. Validate every participant is a part of a provided team :(
        for participant_id in participant_ids:
            await self.get_member.execute(team_id, participant_id)
        # * 5. Proceed with meeting creation
        created_meeting = await self.meeting_repo.save_meeting(new_meeting)
        # * 6. Add all meeting participant to the newly created meeting domain
        created_meeting.participant_ids = participant_ids

        # * 7. Add all unique participants to the DB
        await self.meeting_repo.bulk_save_participants(
            created_meeting.unique_participants
        )
        return created_meeting
