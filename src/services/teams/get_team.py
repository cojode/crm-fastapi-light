from src.services.teams.base import GetMemberDependantTeamUseCase
from src.domain.teams import Team, TeamMember

from uuid import UUID

from src.exceptions import NotFoundDomainError


class TeamNotFoundError(NotFoundDomainError): ...


class GetTeamUseCase(GetMemberDependantTeamUseCase):

    async def execute(self, invoker_id: UUID, team_id: UUID) -> tuple[TeamMember, Team]:
        invoker_member = await self.get_member.execute(team_id, invoker_id)

        if team := await self.team_repo.get_team(team_id):
            return invoker_member, team
        raise TeamNotFoundError("Team not found")
