from fastapi import APIRouter, Depends, status
from uuid import UUID
from src.web.api.tasks.schema import (
    CreateTaskRequest,
    CreateTaskResponse,
    GetTaskResponse,
    ListAssignedTasksResponse,
    ListOwnedTasksResponse,
    UpdateTaskRequest,
    UpdateTaskResponse,
    AssignToTaskResponse,
    AssignToTaskRequest,
    CompleteTaskResponse,
    RateTaskRequest,
    RateTaskResponse,
    TaskCommentRequest,
    TaskCommentResponse,
)

from src.web.dependency import (
    get_create_task_use_case,
    get_get_task_use_case,
    get_list_tasks_use_case,
    get_rate_task_use_case,
    get_delete_task_use_case,
    get_update_task_use_case,
    get_complete_task_use_case,
    get_assign_to_task_use_case,
    get_add_comment_use_case,
)

from src.services.users.dependency import (
    current_active_verified_user_api,
)


router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateTaskResponse,
    summary="Create a new task",
)
async def create_task(
    payload: CreateTaskRequest,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_create_task_use_case),
):
    """Create a new task in the system."""
    return CreateTaskResponse(
        data=await use_case.execute(
            team_id=payload.team_id,
            invoker_id=invoker.id,
            title=payload.title,
            deadline=payload.deadline,
            description=payload.description,
        )
    )


@router.get(
    "/authored",
    response_model=ListOwnedTasksResponse,
    summary="List tasks created by the current user",
)
async def list_owned_tasks(
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_list_tasks_use_case),
):
    """Get all tasks created by the current user."""
    return ListOwnedTasksResponse(values=await use_case.execute(author_id=invoker.id))


@router.get(
    "/assigned",
    response_model=ListAssignedTasksResponse,
    summary="List tasks assigned to the current user",
)
async def list_assigned_tasks(
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_list_tasks_use_case),
):
    """Get all tasks assigned to the current user."""
    return ListAssignedTasksResponse(
        values=await use_case.execute(author_id=None, assignee_id=invoker.id)
    )


@router.get(
    "/{task_id}",
    response_model=GetTaskResponse,
    summary="Get a task by ID",
)
async def get_task(
    task_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_get_task_use_case),
):
    """Retrieve a specific task by its unique ID."""
    _, task = await use_case.execute(invoker_id=invoker.id, task_id=task_id)
    return GetTaskResponse(data=task)


@router.patch(
    "/{task_id}",
    response_model=UpdateTaskResponse,
    summary="Update a task",
)
async def update_task(
    payload: UpdateTaskRequest,
    task_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_update_task_use_case),
):
    """Update task details (partial update)."""
    return UpdateTaskResponse(
        data=await use_case.execute(
            invoker_id=invoker.id,
            task_id=task_id,
            title=payload.title,
            description=payload.description,
            deadline=payload.deadline,
        )
    )


@router.post(
    "/{task_id}/assign",
    response_model=AssignToTaskResponse,
    summary="Assign a task to a user",
)
async def assign_to_task(
    task_id: UUID,
    payload: AssignToTaskRequest,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_assign_to_task_use_case),
):
    """Assign a task to another user."""
    return AssignToTaskResponse(
        data=await use_case.execute(
            invoker_id=invoker.id,
            task_id=task_id,
            assignee_id=payload.assignee_id,
        )
    )


@router.post(
    "/{task_id}/complete",
    response_model=CompleteTaskResponse,
    summary="Mark a task as completed",
)
async def complete_task(
    task_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_complete_task_use_case),
):
    """Mark a task as completed."""
    return CompleteTaskResponse(
        data=await use_case.execute(invoker_id=invoker.id, task_id=task_id)
    )


@router.post(
    "/{task_id}/rate",
    response_model=RateTaskResponse,
    summary="Rate a completed task",
)
async def rate_task(
    task_id: UUID,
    payload: RateTaskRequest,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_rate_task_use_case),
):
    """Submit a rating for a completed task."""
    return RateTaskResponse(
        data=await use_case.execute(
            invoker_id=invoker.id, task_id=task_id, score=payload.score
        )
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_delete_task_use_case),
):
    """Permanently delete a task."""
    await use_case.execute(invoker_id=invoker.id, task_id=task_id)


@router.post(
    "/{task_id}/comment",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskCommentResponse,
    summary="Add a comment to a task",
)
async def add_task_comment(
    task_id: UUID,
    payload: TaskCommentRequest,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_add_comment_use_case),
):
    """Add a comment to a task."""
    return TaskCommentResponse(
        data=await use_case.execute(
            invoker_id=invoker.id, task_id=task_id, text=payload.text
        )
    )
