from src.schemas import GenericResponse, GenericListResponse
from src.domain.teams import Team, TeamMember, TeamInvite

from pydantic import BaseModel
from uuid import UUID


class CreateTeamRequest(BaseModel):
    name: str


class AddTeamMemberRequest(BaseModel):
    new_member_id: UUID


class AcceptInviteRequest(BaseModel):
    code: UUID


class SingleTeamResponse(GenericResponse[Team]): ...


class SingleTeamMemberResponse(GenericResponse[TeamMember]): ...


class CreateTeamResponse(SingleTeamResponse): ...


class GetTeamResponse(SingleTeamResponse): ...


class MyTeamsResponse(GenericListResponse[Team]): ...


class GetTeamsResponse(GenericListResponse[Team]): ...


class GetTeamMembersResponse(GenericListResponse[TeamMember]): ...


class GetTeamMemberResponse(SingleTeamMemberResponse): ...


class AddTeamMemberResponse(SingleTeamMemberResponse): ...


class GrantRoleResponse(SingleTeamMemberResponse): ...


class GenerateInviteCodeResponse(GenericResponse[TeamInvite]): ...


class AcceptInviteResponse(SingleTeamMemberResponse): ...
