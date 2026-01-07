from src.services.teams.base import GetMemberDependantTeamUseCase
from src.domain.teams import TeamMember

from uuid import UUID

from src.exceptions import DomainError

from src.services.teams.get_member import TeamMemberNotFoundError


class TeamInviteNotFound(DomainError): ...


class AlreadyTeamMember(DomainError): ...


class AcceptInviteUseCase(GetMemberDependantTeamUseCase):
    async def execute(self, code: UUID, invoker_id: UUID) -> TeamMember:
        if not (invite := await self.team_repo.get_invite(code)):
            raise TeamInviteNotFound("Invite code not found")
        target_team = invite.team_id
        try:
            await self.get_member.execute(target_team, invoker_id)
        except TeamMemberNotFoundError:
            invite.use()
            await self.team_repo.save_invite(invite)
            return await self.team_repo.save_member(TeamMember(target_team, invoker_id))
        else:
            raise AlreadyTeamMember("User is already a member of a provided team")
