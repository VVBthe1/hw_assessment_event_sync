from datetime import datetime

from sqlalchemy.orm import Session

from models import Meeting


class MeetingService:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def build(
        title: str,
        sources: list[str],
        status: str,
        crm_id: str | None = None,
        event_id: str | None = None,
        client_name: str | None = None,
        client_company: str | None = None,
        relationship_owner: str | None = None,
        organizer: str | None = None,
        attendees: list[str] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        meeting_type: str | None = None,
        location: str | None = None,
        is_recurring: bool | None = None,
        notes: str | None = None,
        description: str | None = None,
        created_at: datetime | None = None,
        has_conflict: bool = False,
    ) -> Meeting:
        return Meeting(
            title=title,
            sources=sources,
            status=status,
            crm_id=crm_id,
            event_id=event_id,
            client_name=client_name,
            client_company=client_company,
            relationship_owner=relationship_owner,
            organizer=organizer,
            attendees=attendees,
            start_time=start_time,
            end_time=end_time,
            meeting_type=meeting_type,
            location=location,
            is_recurring=is_recurring,
            notes=notes,
            description=description,
            created_at=created_at,
            has_conflict=has_conflict,
        )

    def create(self, meeting: Meeting) -> Meeting:
        self.session.add(meeting)
        self.session.flush()
        return meeting

    def get(self, meeting_id: int) -> Meeting | None:
        return self.session.query(Meeting).filter(Meeting.id == meeting_id).one_or_none()

    def list(
        self, cursor: int | None = None, limit: int = 20
    ) -> tuple[list[Meeting], int | None]:
        query = self.session.query(Meeting).order_by(Meeting.id.asc())
        if cursor is not None:
            query = query.filter(Meeting.id > cursor)

        rows = query.limit(limit + 1).all()
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = items[-1].id if has_more else None
        return items, next_cursor
