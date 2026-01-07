from src.services.teams.base import GetMemberDependantTeamUseCase
from src.domain.teams import TeamMember
from src.domain.enums import TeamRole

from uuid import UUID


class GrantMemberRoleUseCase(GetMemberDependantTeamUseCase):
    async def execute(
        self,
        team_id: UUID,
        invoker_id: UUID,
        team_member_id: UUID,
        role: TeamRole,
    ) -> TeamMember:
        invoker_member = await self.get_member.execute(team_id, invoker_id)
        target_member = await self.get_member.execute(team_id, team_member_id)
        invoker_member.change_role(target_member, role)
        return await self.team_repo.save_member(target_member)
