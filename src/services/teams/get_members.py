from src.services.teams.base import TeamUseCase
from src.domain.teams import TeamMember

from uuid import UUID


class GetMembersUseCase(TeamUseCase):
    async def execute(self, team_id: UUID) -> list[TeamMember]:
        return await self.team_repo.list_members(team_id)
