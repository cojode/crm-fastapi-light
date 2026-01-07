from pydantic import BaseModel, FutureDatetime
from uuid import UUID

from datetime import timedelta


class CreateMeetingRequest(BaseModel):
    team_id: UUID
    title: str
    start_time: FutureDatetime
    duration: timedelta
    participant_ids: list[UUID]
