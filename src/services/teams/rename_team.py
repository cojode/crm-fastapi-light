from src.services.teams.base import GetTeamDependantTeamUseCase

from uuid import UUID


class RenameTeamUseCase(GetTeamDependantTeamUseCase):
    async def execute(
        self,
        team_id: UUID,
        invoker_id: UUID,
        new_name: str,
    ):
        invoker_member, team = await self.get_team.execute(invoker_id, team_id)
        return await self.team_repo.save_team(
            invoker_member.rename_team(team, new_name)
        )
