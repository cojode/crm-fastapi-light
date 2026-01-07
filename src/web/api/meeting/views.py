from fastapi import APIRouter, Depends, status

from src.services.users.dependency import (
    current_staff_api,
    current_active_verified_user_api,
)

from src.web.dependency import (
    get_create_meeting_use_case,
    get_get_meeting_use_case,
    get_cancel_meeting_use_case,
    get_list_meetings_use_case,
)

from src.web.api.meeting.schema import CreateMeetingRequest

from uuid import UUID

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    payload: CreateMeetingRequest,
    invoker=Depends(current_staff_api),
    use_case=Depends(get_create_meeting_use_case),
):
    return await use_case.execute(
        invoker_id=invoker.id,
        team_id=payload.team_id,
        title=payload.title,
        start_time=payload.start_time,
        duration=payload.duration,
        participant_ids=payload.participant_ids,
    )


@router.get("/me")
async def my_meetings(
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_list_meetings_use_case),
):
    return await use_case.execute(invoker_id=invoker.id)


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_get_meeting_use_case),
):
    _, meeting = await use_case.execute(invoker_id=invoker.id, meeting_id=meeting_id)
    return meeting


@router.patch("/{meeting_id}/cancel")
async def cancel_meeting(
    meeting_id: UUID,
    invoker=Depends(current_active_verified_user_api),
    use_case=Depends(get_cancel_meeting_use_case),
):
    return await use_case.execute(invoker_id=invoker.id, meeting_id=meeting_id)
