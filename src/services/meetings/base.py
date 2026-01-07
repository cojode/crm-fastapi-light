from src.domain.meetings import MeetingRepository
from src.services.base import BaseUseCase


class MeetingUseCase(BaseUseCase):
    def __init__(self, meeting_repo: MeetingRepository):
        self.meeting_repo = meeting_repo


from src.services.teams.get_member import GetMemberUseCase


class GetMemberDependantMeetingUseCase(MeetingUseCase):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        get_member_use_case: GetMemberUseCase,
    ):
        super().__init__(meeting_repo)
        self.get_member = get_member_use_case


from src.services.meetings.get_meeting import GetMeetingUseCase


class GetMeetingDependantMeetingUseCase(GetMemberDependantMeetingUseCase):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        get_member_use_case: GetMemberUseCase,
        get_meeting_use_case: GetMeetingUseCase,
    ):
        super().__init__(meeting_repo, get_member_use_case)
        self.get_meeting = get_meeting_use_case
