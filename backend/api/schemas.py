from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class MeetingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crm_id: str | None
    event_id: str | None
    sources: list[str]
    title: str
    client_name: str | None
    client_company: str | None
    relationship_owner: str | None
    organizer: str | None
    attendees: list[str] | None
    start_time: datetime | None
    end_time: datetime | None
    meeting_type: str | None
    location: str | None
    is_recurring: bool | None
    status: str
    notes: str | None
    description: str | None
    created_at: datetime | None
    has_conflict: bool


class MeetingListOut(BaseModel):
    items: list[MeetingOut]
    next_cursor: int | None = None


class ConflictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    field: str
    crm_value: Any | None
    calendar_value: Any | None
    chosen: Any | None
    reason: str
