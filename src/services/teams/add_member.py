from src.services.teams.base import GetMemberDependantTeamUseCase
from src.domain.teams import TeamMember

from uuid import UUID


class AddMemberUseCase(GetMemberDependantTeamUseCase):
    async def execute(
        self, team_id: UUID, invoker_id: UUID, new_member_id: UUID
    ) -> TeamMember:
        invoker_member = await self.get_member.execute(team_id, invoker_id)
        new_member = invoker_member.add_member(new_member_id)
        return await self.team_repo.save_member(new_member)
