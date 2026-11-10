from typing import Any

from sqlalchemy.orm import Session

from models import Conflict


class ConflictService:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def build(
        field: str,
        crm_value: Any,
        calendar_value: Any,
        chosen: Any,
        reason: str,
        meeting_id: int | None = None,
    ) -> Conflict:
        return Conflict(
            meeting_id=meeting_id,
            field=field,
            crm_value=crm_value,
            calendar_value=calendar_value,
            chosen=chosen,
            reason=reason,
        )

    def create(self, conflict: Conflict) -> Conflict:
        self.session.add(conflict)
        return conflict

    def create_many(self, conflicts: list[Conflict]) -> int:
        self.session.add_all(conflicts)
        return len(conflicts)

    def list_for_meeting(self, meeting_id: int) -> list[Conflict]:
        return (
            self.session.query(Conflict)
            .filter(Conflict.meeting_id == meeting_id)
            .order_by(Conflict.id.asc())
            .all()
        )
