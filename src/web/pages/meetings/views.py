from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    Response,
)
from fastapi.responses import HTMLResponse
from pydantic import FutureDatetime
from src.services.users.dependency import current_active_verified_user_pages
from src.web.dependency import (
    get_create_meeting_use_case,
    get_get_team_use_case,
    get_get_meeting_use_case,
    get_list_meetings_use_case,
    get_cancel_meeting_use_case,
)
from src.web.pages.utils import (
    auto_templated_response,
    auto_redirect_response,
    attempt_response_with_pages_errors,
    query_daterange_as_datetime,
    FragileSession,
)
from src.settings import settings

from uuid import UUID

from fastapi_csrf_protect import CsrfProtect

import datetime

router = APIRouter(tags=["meetings pages"], default_response_class=HTMLResponse)


@router.get("/teams/{team_id}/meetings/create")
async def create_meeting_form(
    request: Request,
    team_id: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_get_team_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    invoker_member, team = await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, team_id),
        "/teams",
        "Can not process team",
    )
    return auto_templated_response(
        request,
        "meetings/create.html",
        csrf_protect,
        current_user=current_user,
        invoker_member=invoker_member,
        team=team,
    )


@router.post("/teams/{team_id}/meetings/create")
async def create_meeting_submit(
    request: Request,
    response: Response,
    team_id: UUID,
    title: str = Form(...),
    start_time: FutureDatetime = Form(...),
    duration: int = Form(...),
    participants: list[UUID] = Form(...),
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_create_meeting_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    new_meeting = await attempt_response_with_pages_errors(
        use_case.execute(
            current_user.id,
            team_id,
            title=title,
            start_time=start_time.replace(tzinfo=settings.timezone_info),
            duration=datetime.timedelta(minutes=duration),
            participant_ids=participants,
        ),
        f"/teams/{team_id}/meetings/create",
        "Can not create a meeting",
    )

    FragileSession(request).message = "Meeting successfully created"
    return auto_redirect_response(response, redirect_path=f"/meetings/{new_meeting.id}")


@router.get("/meetings/{meeting_id}")
async def get_meeting_detail(
    request: Request,
    meeting_id: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_get_meeting_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    invoker_member, meeting = await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, meeting_id),
        "/meetings",
        "Can not display this meeting",
    )
    return auto_templated_response(
        request,
        "meetings/detail.html",
        csrf_protect,
        current_user=current_user,
        meeting=meeting,
        invoker_member=invoker_member,
    )


@router.get("/meetings")
async def list_meetings(
    request: Request,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_list_meetings_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    status = request.query_params.get("status")
    start_date, end_date = query_daterange_as_datetime(
        request.query_params.get("start_date"),
        request.query_params.get("end_date"),
    )
    if status == "awaited":
        start_date = settings.datetime_now()
    if status == "ended":
        end_date = settings.datetime_now()
    meetings = await attempt_response_with_pages_errors(
        use_case.execute(
            current_user.id,
            start_date=start_date,
            end_date=end_date,
            cancelled=status == "cancelled",
            live=status == "live",
        ),
        "/meetings",
        "Can not display this meeting",
    )
    return auto_templated_response(
        request,
        "meetings/list.html",
        csrf_protect,
        current_user=current_user,
        meetings=meetings,
    )


@router.post("/meetings/{meeting_id}/cancel")
async def cancel_meeting(
    request: Request,
    response: Response,
    meeting_id: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_cancel_meeting_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, meeting_id),
        f"/meetings/{meeting_id}",
        "Meeting could not be canceled",
    )

    return auto_redirect_response(response, redirect_path=f"/meetings/{meeting_id}")
