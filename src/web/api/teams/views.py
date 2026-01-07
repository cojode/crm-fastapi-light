from fastapi import APIRouter, Depends, status
from src.services.users.dependency import (
    current_admin_api,
    current_active_verified_user_api,
)
from uuid import UUID

from src.domain.enums import TeamRole

from src.web.dependency import (
    get_create_team_use_case,
    get_get_team_use_case,
    get_get_teams_use_case,
    get_get_members_use_case,
    get_get_member_use_case,
    get_add_member_use_case,
    get_grant_member_role_use_case,
    get_remove_member_use_case,
    get_create_invite_use_case,
    get_accept_invite_use_case,
)

from src.web.api.teams.schemas import (
    CreateTeamRequest,
    AddTeamMemberRequest,
    AcceptInviteRequest,
    CreateTeamResponse,
    GetTeamResponse,
    GetTeamsResponse,
    GetTeamMembersResponse,
    GetTeamMemberResponse,
    AddTeamMemberResponse,
    GrantRoleResponse,
    GenerateInviteCodeResponse,
    AcceptInviteResponse,
    MyTeamsResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=CreateTeamResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    payload: CreateTeamRequest,
    invoker=Depends(current_admin_api),
    use_case=Depends(get_create_team_use_case),
):
    return CreateTeamResponse(data=await use_case.execute(payload.name, invoker.id))


@router.get("", response_model=GetTeamsResponse)
async def list_teams(
    _=Depends(current_active_verified_user_api),
    use_case=Depends(get_get_teams_use_case),
):
    return GetTeamsResponse(values=await use_case.execute())


@router.get("/me", response_model=MyTeamsResponse)
async def my_teams(
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_get_teams_use_case),
):
    return MyTeamsResponse(values=await use_case.execute(invoker.id))


@router.get("/{team_id}", response_model=GetTeamResponse)
async def get_team(
    team_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_get_team_use_case),
):
    _, team = await use_case.execute(invoker.id, team_id)
    return GetTeamResponse(data=team)


@router.get("/{team_id}/members", response_model=GetTeamMembersResponse)
async def get_team_members(
    team_id: UUID,
    _=Depends(current_active_verified_user_api),
    use_case=Depends(get_get_members_use_case),
):
    return GetTeamMembersResponse(values=await use_case.execute(team_id))


@router.get("/{team_id}/members/{user_id}", response_model=GetTeamMemberResponse)
async def get_team_member(
    team_id: UUID,
    user_id: UUID,
    _=Depends(current_active_verified_user_api),
    use_case=Depends(get_get_member_use_case),
):
    return GetTeamMemberResponse(data=await use_case.execute(team_id, user_id))


@router.post(
    "/{team_id}/members",
    response_model=AddTeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_team_member(
    payload: AddTeamMemberRequest,
    team_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_add_member_use_case),
):
    return AddTeamMemberResponse(
        data=await use_case.execute(team_id, invoker.id, payload.new_member_id)
    )


@router.patch("/{team_id}/members/{user_id}/role", response_model=GrantRoleResponse)
async def grant_role(
    team_id: UUID,
    user_id: UUID,
    role: TeamRole,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_grant_member_role_use_case),
):
    return GrantRoleResponse(
        data=await use_case.execute(team_id, invoker.id, user_id, role)
    )


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: UUID,
    user_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_remove_member_use_case),
):
    return await use_case.execute(team_id, invoker.id, user_id)


@router.post("/{team_id}/invite")
async def generate_invite_code(
    team_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_create_invite_use_case),
):
    return GenerateInviteCodeResponse(data=await use_case.execute(team_id, invoker.id))


@router.post("/accept-invite", response_model=AcceptInviteResponse)
async def accept_invite(
    payload: AcceptInviteRequest,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_accept_invite_use_case),
):
    return AcceptInviteResponse(data=await use_case.execute(payload.code, invoker.id))
