from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import HTMLResponse
from src.domain.teams import TeamRole
from src.services.users.dependency import (
    current_active_verified_user_pages,
    current_admin_pages,
)
from src.web.dependency import (
    get_get_teams_use_case,
    get_accept_invite_use_case,
    get_get_team_use_case,
    get_grant_member_role_use_case,
    get_remove_member_use_case,
    get_create_invite_use_case,
    get_remove_invite_use_case,
    get_create_team_use_case,
    get_rename_team_use_case,
    get_add_member_use_case,
)
from src.web.pages.utils import (
    auto_templated_response,
    auto_redirect_response,
    attempt_response_with_pages_errors,
    FragileSession,
)

from uuid import UUID

from fastapi_csrf_protect import CsrfProtect

router = APIRouter(tags=["teams pages"], default_response_class=HTMLResponse)


@router.get("/teams")
async def my_teams(
    request: Request,
    use_case=Depends(get_get_teams_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    teams_response = await attempt_response_with_pages_errors(
        use_case.execute(current_user.id),
        "/profile",
        "Teams are not available",
    )
    return auto_templated_response(
        request,
        "teams/list.html",
        csrf_protect,
        current_user=current_user,
        teams=teams_response,
    )


@router.get("/teams/create")
async def create_team_page(
    request: Request,
    current_user=Depends(current_admin_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    return auto_templated_response(
        request,
        "teams/create.html",
        csrf_protect=csrf_protect,
        current_user=current_user,
    )


@router.post("/teams/create")
async def create_team_submit(
    request: Request,
    response: Response,
    team_name: str = Form(...),
    use_case=Depends(get_create_team_use_case),
    current_user=Depends(current_admin_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    new_team = await attempt_response_with_pages_errors(
        use_case.execute(team_name, current_user.id),
        "/teams",
        "Team creation failed",
    )
    FragileSession(request).message = "Team successfully created"
    return auto_redirect_response(response, f"/teams/{new_team.id}")


@router.post("/teams/join")
async def accept_invite_code(
    request: Request,
    response: Response,
    invite_code: UUID = Form(...),
    use_case=Depends(get_accept_invite_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(code=invite_code, invoker_id=current_user.id),
        "/teams",
        "Invitations currently unavailable",
    )
    FragileSession(request).message = (
        "Invite code activated! Team would appear in a lower list."
    )
    return auto_redirect_response(response, "/teams")


@router.get("/teams/{team_id}")
async def get_team(
    request: Request,
    team_id: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_get_team_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    invoker_member_response, team_response = await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, team_id),
        "/teams",
        "Unknown team issue",
    )
    return auto_templated_response(
        request,
        "teams/view.html",
        csrf_protect,
        current_user,
        team=team_response,
        invoker_member=invoker_member_response,
    )


@router.post("/teams/{team_id}/rename")
async def rename_team(
    request: Request,
    response: Response,
    team_id: UUID,
    new_name: str = Form(...),
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_rename_team_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(team_id, current_user.id, new_name),
        f"/teams/{team_id}",
        "Can't grant role",
    )

    FragileSession(request).message = "Team succesfully renamed"
    return auto_redirect_response(response, redirect_path=f"/teams/{team_id}")


@router.post("/teams/{team_id}/members/add")
async def add_team_member(
    request: Request,
    response: Response,
    team_id: UUID,
    new_member_id: UUID = Form(...),
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_add_member_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(team_id, current_user.id, new_member_id),
        f"/teams/{team_id}",
        "Can't add a member",
    )

    FragileSession(request).message = "New member added or already in the team"
    return auto_redirect_response(response, redirect_path=f"/teams/{team_id}")


@router.post("/teams/{team_id}/members/{team_member_id}/role")
async def grant_team_member_role(
    request: Request,
    response: Response,
    team_id: UUID,
    team_member_id: UUID,
    new_role: TeamRole = Form(...),
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_grant_member_role_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(team_id, current_user.id, team_member_id, new_role),
        f"/teams/{team_id}",
        "Can't grant role",
    )

    FragileSession(request).message = (
        f"User [{team_member_id}] succesfully obtained new role"
    )
    return auto_redirect_response(response, redirect_path=f"/teams/{team_id}")


@router.post("/teams/{team_id}/members/{team_member_id}/remove")
async def remove_team_member(
    request: Request,
    response: Response,
    team_id: UUID,
    team_member_id: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_remove_member_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(team_id, current_user.id, team_member_id),
        f"/teams/{team_id}",
        "Can't grant role",
    )

    FragileSession(request).message = (
        f"User [{team_member_id}] succesfully removed from team."
    )
    return auto_redirect_response(response, redirect_path=f"/teams/{team_id}")


@router.post("/teams/{team_id}/invite")
async def generate_invite_code(
    request: Request,
    response: Response,
    team_id: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_create_invite_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(team_id, current_user.id),
        f"/teams/{team_id}",
        "Can't generate invite code",
    )

    FragileSession(request).message = "New invite code succesfully generated"
    return auto_redirect_response(response, redirect_path=f"/teams/{team_id}")


@router.post("/teams/{team_id}/invites/{invite_code}/revoke")
async def revoke_invite_code(
    request: Request,
    response: Response,
    team_id: UUID,
    invite_code: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_remove_invite_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(team_id, current_user.id, invite_code),
        f"/teams/{team_id}",
        "Could not revoke invite code",
    )
    FragileSession(request).message = "Invite code successfully revoked"
    return auto_redirect_response(response, redirect_path=f"/teams/{team_id}")
