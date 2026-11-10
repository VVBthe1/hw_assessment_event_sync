from models import Conflict, Meeting


class MeetingService:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def build(
        crm_id=None,
        event_id=None,
        sources=None,
        title=None,
        client_name=None,
        client_company=None,
        relationship_owner=None,
        organizer=None,
        attendees=None,
        start_time=None,
        end_time=None,
        meeting_type=None,
        location=None,
        is_recurring=None,
        status=None,
        notes=None,
        description=None,
        created_at=None,
        has_conflict=False,
    ):
        return Meeting(
            crm_id=crm_id,
            event_id=event_id,
            sources=sources or [],
            title=title,
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
            status=status,
            notes=notes,
            description=description,
            created_at=created_at,
            has_conflict=has_conflict,
        )

    def create(self, meeting):
        self.session.add(meeting)
        self.session.flush()
        return meeting

    def create_many(self, meetings):
        self.session.add_all(meetings)
        self.session.flush()
        return meetings

    def clear(self):
        self.session.query(Conflict).delete()
        self.session.query(Meeting).delete()
        self.session.commit()
