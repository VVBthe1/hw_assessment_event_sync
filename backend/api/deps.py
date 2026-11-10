from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db
from services.conflicts import ConflictService
from services.meetings import MeetingService

DbSession = Annotated[Session, Depends(get_db)]


def get_meeting_service(session: DbSession):
    return MeetingService(session)


def get_conflict_service(session: DbSession):
    return ConflictService(session)


MeetingSvc = Annotated[MeetingService, Depends(get_meeting_service)]
ConflictSvc = Annotated[ConflictService, Depends(get_conflict_service)]
