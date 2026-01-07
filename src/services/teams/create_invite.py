from src.services.teams.base import GetMemberDependantTeamUseCase
from src.domain.teams import TeamInvite

from uuid import UUID


class CreateInviteUseCase(GetMemberDependantTeamUseCase):
    async def execute(
        self,
        team_id: UUID,
        invoker_id: UUID,
    ) -> TeamInvite:
        invoker_member = await self.get_member.execute(team_id, invoker_id)
        invite = invoker_member.generate_invite_code()
        return await self.team_repo.save_invite(invite)
