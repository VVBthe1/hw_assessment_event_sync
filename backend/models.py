from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from db import Base


class MeetingStatus(str, Enum):
    CONFIRMED = "Confirmed"
    SCHEDULED = "Scheduled"
    TENTATIVE = "Tentative"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

    @classmethod
    def from_crm(cls, value):
        if not value:
            return cls.SCHEDULED
        return cls(value)

    @classmethod
    def from_calendar(cls, value):
        mapping = {
            "confirmed": cls.CONFIRMED,
            "tentative": cls.TENTATIVE,
            "cancelled": cls.CANCELLED,
        }
        if not value:
            return cls.CONFIRMED
        return mapping.get(value.lower(), cls.CONFIRMED)


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crm_id = Column(String(64), unique=True, nullable=True)
    event_id = Column(String(64), unique=True, nullable=True)
    sources = Column(JSON, nullable=False)
    title = Column(String(512), nullable=False)
    client_name = Column(String(255), nullable=True)
    client_company = Column(String(255), nullable=True)
    relationship_owner = Column(String(255), nullable=True)
    organizer = Column(String(255), nullable=True)
    attendees = Column(JSON, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    meeting_type = Column(String(64), nullable=True)
    location = Column(String(512), nullable=True)
    is_recurring = Column(Boolean, nullable=True)
    status = Column(String(64), nullable=False)
    notes = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    has_conflict = Column(Boolean, nullable=False, default=False)

    conflicts = relationship("Conflict", back_populates="meeting", cascade="all, delete-orphan")


class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    field = Column(String(64), nullable=False)
    crm_value = Column(JSON, nullable=True)
    calendar_value = Column(JSON, nullable=True)
    chosen = Column(JSON, nullable=True)
    reason = Column(Text, nullable=False)

    meeting = relationship("Meeting", back_populates="conflicts")
