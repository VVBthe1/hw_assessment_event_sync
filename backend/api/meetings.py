from fastapi import APIRouter, HTTPException, Query

from api.deps import ConflictSvc, MeetingSvc
from api.schemas import ConflictOut, MeetingListOut

router = APIRouter()


@router.get("/meetings", response_model=MeetingListOut)
def list_meetings(
    meetings: MeetingSvc,
    cursor: int | None = None,
    limit: int = Query(default=20, ge=1, le=100),
):
    items, next_cursor = meetings.list(cursor=cursor, limit=limit)
    return MeetingListOut(items=items, next_cursor=next_cursor)


@router.get("/meetings/{meeting_id}/conflicts", response_model=list[ConflictOut])
def list_meeting_conflicts(
    meeting_id: int,
    meetings: MeetingSvc,
    conflicts: ConflictSvc,
):
    if meetings.get(meeting_id) is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return conflicts.list_for_meeting(meeting_id)
