from src.services.teams.base import TeamUseCase
from src.domain.teams import Team


from uuid import UUID


class ListTeamsUseCase(TeamUseCase):
    async def execute(self, user_id: UUID | None = None) -> list[Team]:
        return await self.team_repo.list_teams(user_id)
