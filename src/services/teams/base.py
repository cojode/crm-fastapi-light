from src.domain.teams import TeamRepository
from src.services.base import BaseUseCase


class TeamUseCase(BaseUseCase):
    def __init__(self, team_repo: TeamRepository):
        self.team_repo = team_repo


from src.services.teams.get_member import GetMemberUseCase


class GetMemberDependantTeamUseCase(TeamUseCase):
    def __init__(
        self, team_repo: TeamRepository, get_member_use_case: GetMemberUseCase
    ):
        super().__init__(team_repo)
        self.get_member = get_member_use_case


from src.services.teams.get_team import GetTeamUseCase


class GetTeamDependantTeamUseCase(TeamUseCase):
    def __init__(self, team_repo: TeamRepository, get_team_use_case: GetTeamUseCase):
        super().__init__(team_repo)
        self.get_team = get_team_use_case
