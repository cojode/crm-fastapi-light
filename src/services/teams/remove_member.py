from src.services.teams.base import GetMemberDependantTeamUseCase

from uuid import UUID


class RemoveMemberUseCase(GetMemberDependantTeamUseCase):
    async def execute(
        self,
        team_id: UUID,
        invoker_id: UUID,
        team_member_id: UUID,
    ):
        invoker_member = await self.get_member.execute(team_id, invoker_id)
        target_member = await self.get_member.execute(team_id, team_member_id)
        invoker_member.remove_member(target_member)
        await self.team_repo.delete_member(target_member)
