from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    Response,
    Query,
)
from fastapi.responses import HTMLResponse
from src.domain.tasks import TaskScore
from pydantic import FutureDatetime
from src.services.users.dependency import current_active_verified_user_pages
from src.web.dependency import (
    get_create_task_use_case,
    get_get_team_use_case,
    get_get_task_use_case,
    get_add_comment_use_case,
    get_delete_task_use_case,
    get_list_tasks_use_case,
    get_complete_task_use_case,
    get_update_task_use_case,
    get_rate_task_use_case,
)
from src.web.pages.utils import (
    auto_templated_response,
    auto_redirect_response,
    attempt_response_with_pages_errors,
    FragileSession,
    query_daterange_as_datetime,
)

from uuid import UUID

from fastapi_csrf_protect import CsrfProtect

router = APIRouter(tags=["tasks pages"], default_response_class=HTMLResponse)


@router.get("/teams/{team_id}/tasks/create")
async def create_task_form(
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
        "tasks/create.html",
        csrf_protect,
        current_user=current_user,
        invoker_member=invoker_member,
        team=team,
    )


@router.post("/teams/{team_id}/tasks/create")
async def create_task_submit(
    request: Request,
    response: Response,
    team_id: UUID,
    title: str = Form(...),
    description: str = Form(...),
    deadline: FutureDatetime = Form(...),
    assignee_id: UUID | str = Form(default=""),
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_create_task_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    new_task = await attempt_response_with_pages_errors(
        use_case.execute(
            team_id,
            current_user.id,
            title,
            deadline,
            description,
            None if assignee_id == "" else assignee_id,
        ),
        "/teams/{team_id}",
        "Task could not be created",
    )
    FragileSession(request).message = "Task successfully created"

    return auto_redirect_response(response, f"/tasks/{new_task.id}")


@router.get("/tasks")
async def list_tasks(
    request: Request,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_list_tasks_use_case),
    csrf_protect: CsrfProtect = Depends(),
    task_type: str = Query("assigned", description="Тип задач: assigned или authored"),
):
    statuses = request.query_params.getlist("status")
    start_date, end_date = query_daterange_as_datetime(
        request.query_params.get("start_date"),
        request.query_params.get("end_date"),
    )
    params = {
        "statuses": statuses,
        "start_date": start_date,
        "end_date": end_date,
        "author_id": None,
    }

    if task_type == "authored":
        params["author_id"] = current_user.id
    else:
        params["assignee_id"] = current_user.id

    tasks = await attempt_response_with_pages_errors(
        use_case.execute(**params),
        "/profile",
        "Tasks could not be displayed",
    )

    total_tasks_count = len(tasks)
    rated_tasks = [task for task in tasks if task.score is not None]
    rated_tasks_count = len(rated_tasks)
    avg_rating = (
        sum([task.score.value for task in rated_tasks]) / rated_tasks_count
        if rated_tasks_count != 0
        else 0
    )

    return auto_templated_response(
        request,
        "tasks/list.html",
        csrf_protect,
        current_user,
        tasks=tasks,
        total_tasks=total_tasks_count,
        rated_tasks=rated_tasks_count,
        avg_rating=avg_rating,
        task_type=task_type,
    )


@router.get("/tasks/{task_id}")
async def view_task(
    request: Request,
    task_id: UUID,
    current_user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_get_task_use_case),
    team_use_case=Depends(get_get_team_use_case),
    csrf_protect: CsrfProtect = Depends(),
):
    invoker_member, task = await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, task_id),
        "/tasks/assignee",
        "Task could not be displayed",
    )
    edit_mode = request.query_params.get("edit", None)
    rate_mode = request.query_params.get("rate", None)

    if edit_mode:
        _, team = await attempt_response_with_pages_errors(
            team_use_case.execute(invoker_member.user_id, invoker_member.team_id),
            "/tasks/assignee",
            "Team could not be loaded",
        )
    else:
        team = None

    return auto_templated_response(
        request,
        "tasks/detail.html",
        csrf_protect,
        current_user,
        task=task,
        invoker_member=invoker_member,
        edit_mode=edit_mode,
        rate_mode=rate_mode,
        team=team,
    )


@router.post("/tasks/{task_id}/update")
async def update_task(
    request: Request,
    response: Response,
    task_id: UUID,
    title: str = Form(...),
    description: str = Form(...),
    deadline: FutureDatetime = Form(...),
    assignee_id: UUID | None = Form(default=None),
    use_case=Depends(get_update_task_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(
            invoker_id=current_user.id,
            task_id=task_id,
            title=title,
            deadline=deadline,
            description=description,
            assignee_id=assignee_id,
        ),
        "/teams/{team_id}",
        "Task could not be updated",
    )
    FragileSession(request).message = "Task updated succesfully"
    return auto_redirect_response(response, f"/tasks/{task_id}")


@router.post("/tasks/{task_id}/comment")
async def leave_comment(
    request: Request,
    response: Response,
    task_id: UUID,
    comment_text: str = Form(...),
    use_case=Depends(get_add_comment_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, task_id, text=comment_text),
        f"/tasks/{task_id}",
        "Comment could not be added",
    )
    return auto_redirect_response(response, f"/tasks/{task_id}")


@router.post("/tasks/{task_id}/rate")
async def rate_task(
    request: Request,
    response: Response,
    task_id: UUID,
    score: TaskScore = Form(...),
    use_case=Depends(get_rate_task_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, task_id, score),
        f"/tasks/{task_id}",
        "Rate could not be added",
    )
    return auto_redirect_response(response, f"/tasks/{task_id}")


@router.post("/tasks/{task_id}/delete")
async def delete_task(
    request: Request,
    response: Response,
    task_id: UUID,
    use_case=Depends(get_delete_task_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(task_id, current_user.id),
        f"/tasks/{task_id}",
        "Task could not be removed",
    )

    return auto_redirect_response(response, "/tasks/")


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    request: Request,
    response: Response,
    task_id: UUID,
    use_case=Depends(get_complete_task_use_case),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        use_case.execute(current_user.id, task_id),
        f"/tasks/{task_id}",
        "Task could not be completed",
    )

    return auto_redirect_response(response, f"/tasks/{task_id}")
