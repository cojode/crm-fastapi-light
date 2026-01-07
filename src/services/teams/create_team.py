from src.services.teams.base import TeamUseCase
from src.domain.teams import Team, TeamMember
from src.domain.enums import TeamRole

from uuid import uuid4, UUID


class CreateTeamUseCase(TeamUseCase):
    async def execute(self, name: str, owner_id: UUID) -> Team:
        team = Team(id=uuid4(), name=name)
        saved_team = await self.team_repo.save_team(team)

        owner = TeamMember(team_id=team.id, user_id=owner_id, role=TeamRole.OWNER)
        await self.team_repo.save_member(owner)

        return saved_team
