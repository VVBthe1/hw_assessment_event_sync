from models import Conflict


class ConflictService:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def build(field, crm_value, calendar_value, chosen, reason, meeting_id=None):
        return Conflict(
            meeting_id=meeting_id,
            field=field,
            crm_value=crm_value,
            calendar_value=calendar_value,
            chosen=chosen,
            reason=reason,
        )

    def create(self, conflict):
        self.session.add(conflict)
        return conflict

    def create_many(self, conflicts):
        self.session.add_all(conflicts)
        return conflicts
