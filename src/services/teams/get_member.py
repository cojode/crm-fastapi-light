from src.services.teams.base import TeamUseCase
from src.domain.teams import TeamMember

from uuid import UUID

from src.exceptions import NotFoundDomainError


class TeamMemberNotFoundError(NotFoundDomainError): ...


class GetMemberUseCase(TeamUseCase):
    async def execute(self, team_id: UUID, user_id: UUID) -> TeamMember:
        if member := await self.team_repo.get_member(team_id, user_id):
            return member
        raise TeamMemberNotFoundError("Team member not found")
