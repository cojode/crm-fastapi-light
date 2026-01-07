from fastapi import (
    APIRouter,
    Request,
    Depends,
)
from fastapi.responses import HTMLResponse
from src.services.users.dependency import current_active_verified_user_pages
from src.web.dependency import get_calendar_view_use_case
from src.web.pages.utils import (
    auto_templated_response,
    attempt_response_with_pages_errors,
)
from src.settings import settings

from fastapi_csrf_protect import CsrfProtect

import datetime

router = APIRouter(tags=["calendar pages"], default_response_class=HTMLResponse)

from src.domain.enums import CalendarScope


@router.get("/")
async def get_calendar(
    request: Request,
    month: str | None = None,
    day: str | None = None,
    use_case=Depends(get_calendar_view_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    today = settings.datetime_now()
    if month:
        try:
            date = datetime.datetime.strptime(month, "%Y-%m").date().replace(day=1)
        except ValueError:
            date = today.replace(day=1)
    else:
        date = today.replace(day=1)

    if day:
        date = date.replace(day=datetime.datetime.strptime(day, "%d").day)
        calendar_view = await attempt_response_with_pages_errors(
            use_case.execute(
                current_user.id,
                date,
                CalendarScope.SINGLE_DAY,
            ),
            "/profile",
            "Calendar issues",
        )
        prev_day = date - datetime.timedelta(days=1)
        next_day = date + datetime.timedelta(days=1)

        return auto_templated_response(
            request,
            "calendar/daily.html",
            csrf_protect,
            current_user,
            view=calendar_view,
            current_date=date,
            prev_day=prev_day,
            next_day=next_day,
        )

    calendar_view = await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, date, CalendarScope.SINGLE_MONTH),
        "/profile",
        "Calendar issues",
    )
    prev_month = (date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
    next_month = (date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)

    return auto_templated_response(
        request,
        "calendar/monthly.html",
        csrf_protect,
        current_user,
        view=calendar_view,
        current_date=date,
        prev_month=prev_month,
        next_month=next_month,
    )
