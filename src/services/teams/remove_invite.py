from src.services.teams.base import GetMemberDependantTeamUseCase

from uuid import UUID


class RemoveInviteUseCase(GetMemberDependantTeamUseCase):
    async def execute(self, team_id: UUID, invoker_id: UUID, code: UUID):
        invoker_member = await self.get_member.execute(team_id, invoker_id)
        invoker_member.remove_invite_code()
        await self.team_repo.delete_invite(code)
