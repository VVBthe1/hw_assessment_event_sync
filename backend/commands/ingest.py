import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from db import SessionLocal
from models import Conflict, Meeting, MeetingStatus
from services.conflicts import ConflictService
from services.meetings import MeetingService

ROOT = Path(__file__).resolve().parents[2]
CRM_PATH = ROOT / "data" / "crm_events.json"
CAL_PATH = ROOT / "data" / "calendar_events.json"
EASTERN = ZoneInfo("America/New_York")

STOP_WORDS = {"the", "a", "an", "and", "of", "to", "for", "with", "on", "in", "at"}
VIRTUAL_MARKERS = ("zoom", "teams", "microsoft teams", "meet.google", "http://", "https://")


def load_json(path):
    with path.open() as f:
        return json.load(f)


def parse_crm_start(row):
    date_raw = row.get("meeting_date")
    time_raw = row.get("meeting_time")
    if not date_raw:
        return None

    try:
        date_value = datetime.strptime(date_raw, "%Y-%m-%d").date()
    except ValueError:
        return None

    if not time_raw:
        return datetime.combine(date_value, datetime.min.time())

    try:
        time_value = datetime.strptime(time_raw, "%H:%M").time()
    except ValueError:
        return None

    return datetime.combine(date_value, time_value)


def parse_cal_datetime(value):
    if not value:
        return None
    if value.endswith("Z"):
        utc = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return utc.astimezone(EASTERN).replace(tzinfo=None)
    return datetime.fromisoformat(value)


def normalize_text(value):
    return " ".join((value or "").strip().lower().split())


def significant_words(value):
    # replacing common special chars
    cleaned = normalize_text(value).replace("+", " ").replace("-", " ").replace("/", " ")
    
    # ignoring stop words
    return {word for word in cleaned.split() if word and word not in STOP_WORDS}


def title_word_overlap(left, right):
    return len(significant_words(left) & significant_words(right))


def texts_equivalent(left, right):
    a = normalize_text(left)
    b = normalize_text(right)
    if not a or not b:
        return False
    if a == b or a in b or b in a:
        return True

    left_virtual = any(marker in a for marker in VIRTUAL_MARKERS)
    right_virtual = any(marker in b for marker in VIRTUAL_MARKERS)
    if left_virtual != right_virtual:
        return False

    left_words = significant_words(left)
    right_words = significant_words(right)
    if not left_words or not right_words:
        return False
    return len(left_words & right_words) >= 1


def match_score(crm, cal):
    crm_start = parse_crm_start(crm)
    cal_start = parse_cal_datetime(cal.get("start_time"))
    if crm_start is None or cal_start is None:
        return 0
    if crm_start.date() != cal_start.date():
        return 0

    score = 10
    company = normalize_text(crm.get("client_company"))
    title = normalize_text(cal.get("title"))
    if company and company in title:
        score += 50

    overlap = title_word_overlap(crm.get("subject"), cal.get("title"))
    if overlap >= 2:
        score += 50
    elif overlap == 1:
        score += 15

    if not crm.get("meeting_time"):
        return score

    # identifying minutes diff between CRM and Calendar dates in minutes.
    delta = abs(int((crm_start - cal_start).total_seconds() // 60))
    if delta == 0:
        score += 100
    elif delta <= 15:
        score += 80
    elif delta <= 60:
        score += 40
    return score


def pick_calendar_match(crm, calendar_rows, used_ids):
    candidates = []
    for cal in calendar_rows:
        if cal["event_id"] in used_ids:
            continue
        score = match_score(crm, cal)
        if score >= 60:
            candidates.append((score, cal))

    if not candidates:
        return None, []

    # sort by score descending and calendar item event id ascending
    candidates.sort(key=lambda item: (-item[0], item[1]["event_id"]))
    primary = candidates[0][1] # highest score or latest event as primary
    duplicates = []

    primary_start = parse_cal_datetime(primary.get("start_time"))
    primary_end = parse_cal_datetime(primary.get("end_time")) or (
        primary_start + timedelta(hours=1) if primary_start else None
    )

    for _, cal in candidates[1:]:
        cal_start = parse_cal_datetime(cal.get("start_time"))
        cal_end = parse_cal_datetime(cal.get("end_time")) or (
            cal_start + timedelta(hours=1) if cal_start else None
        )
        if not primary_start or not cal_start or not primary_end or not cal_end:
            continue

        overlaps = primary_start < cal_end and cal_start < primary_end
        same_organizer = cal.get("organizer") == primary.get("organizer")
        shared_attendees = set(cal.get("attendees") or []) & set(primary.get("attendees") or [])
        similar_title = title_word_overlap(primary.get("title"), cal.get("title")) >= 2
        if overlaps and (same_organizer or shared_attendees or similar_title):
            duplicates.append(cal)

    return primary, duplicates


def choose_location(crm, cal):
    crm_location = (crm or {}).get("location")
    cal_location = (cal or {}).get("location")
    meeting_type = (crm or {}).get("meeting_type")

    if crm is None:
        return {"location": cal_location}
    if cal is None:
        return {"location": crm_location}

    if meeting_type == "In-Person":
        chosen = crm_location if crm_location is not None else cal_location
        reason = (
            f"CRM is In-Person and calendar location differs "
            f"(crm={crm_location!r}, calendar={cal_location!r}); kept CRM location."
        )
    elif meeting_type == "Virtual":
        chosen = cal_location if cal_location is not None else crm_location
        reason = (
            f"Virtual meeting locations differ "
            f"(crm={crm_location!r}, calendar={cal_location!r}); kept calendar location."
        )
    elif crm_location is not None and cal_location is None:
        return {"location": crm_location}
    elif cal_location is not None and crm_location is None:
        return {"location": cal_location}
    else:
        chosen = crm_location or cal_location
        reason = (
            f"Locations differ "
            f"(crm={crm_location!r}, calendar={cal_location!r}); kept CRM location."
        )

    decision = {"location": chosen}
    if crm_location and cal_location and not texts_equivalent(crm_location, cal_location):
        decision["crm_value"] = crm_location
        decision["calendar_value"] = cal_location
        decision["reason"] = reason
    return decision


def build_meeting(crm, cal, duplicate_cals=None):
    duplicate_cals = duplicate_cals or []
    conflicts = []

    sources = []
    if crm is not None:
        sources.append("crm")
    if cal is not None:
        sources.append("calendar")

    crm_subject = (crm or {}).get("subject")
    cal_title = (cal or {}).get("title")
    if cal_title:
        title = cal_title
        if (
            crm_subject
            and title_word_overlap(crm_subject, cal_title) == 0
            and not texts_equivalent(crm_subject, cal_title)
        ):
            conflicts.append(
                ConflictService.build(
                    "title",
                    crm_subject,
                    cal_title,
                    title,
                    "CRM subject and calendar title both present and look unrelated; "
                    f"kept calendar title ({cal_title!r}).",
                )
            )
    else:
        title = crm_subject or "Untitled meeting"

    crm_start = parse_crm_start(crm) if crm else None
    crm_start_for_compare = None if (crm and not crm.get("meeting_time")) else crm_start
    cal_start = parse_cal_datetime((cal or {}).get("start_time"))
    cal_end = parse_cal_datetime((cal or {}).get("end_time"))

    if cal_start is not None:
        start_time = cal_start
        if crm_start_for_compare is not None and crm_start_for_compare != cal_start:
            conflicts.append(
                ConflictService.build(
                    "start_time",
                    crm_start_for_compare.isoformat(sep=" "),
                    cal_start.isoformat(sep=" "),
                    cal_start.isoformat(sep=" "),
                    "Start times differ after parsing "
                    f"(crm={crm_start_for_compare}, calendar={cal_start}); "
                    "kept calendar start_time.",
                )
            )
    else:
        start_time = crm_start_for_compare or crm_start

    if crm is not None:
        status = MeetingStatus.from_crm(crm.get("status"))
        cal_status = (cal or {}).get("status")
        if (
            cal_status
            and status == MeetingStatus.CANCELLED
            and cal_status.lower() == "confirmed"
        ):
            conflicts.append(
                ConflictService.build(
                    "status",
                    status.value,
                    cal_status,
                    status.value,
                    "CRM status is Cancelled but calendar is still confirmed; kept CRM status.",
                )
            )
    else:
        status = MeetingStatus.from_calendar((cal or {}).get("status"))

    location_decision = choose_location(crm, cal)
    if "reason" in location_decision:
        conflicts.append(
            ConflictService.build(
                "location",
                location_decision["crm_value"],
                location_decision["calendar_value"],
                location_decision["location"],
                location_decision["reason"],
            )
        )

    crm_created = parse_cal_datetime(crm.get("created_at")) if crm else None
    cal_created = parse_cal_datetime(cal.get("created_at")) if cal else None

    if crm_created and cal_created:
        created_at = min(crm_created, cal_created)
    else:
        created_at = crm_created or cal_created

    event_id = (cal or {}).get("event_id")
    for dup in duplicate_cals:
        conflicts.append(
            ConflictService.build(
                "event_id",
                (crm or {}).get("crm_id"),
                [event_id, dup.get("event_id")],
                event_id,
                f"Calendar event {dup.get('event_id')} looks like a duplicate of "
                f"{event_id}; kept {event_id}.",
            )
        )

    meeting = MeetingService.build(
        title=title,
        sources=sources,
        status=status.value,
        crm_id=(crm or {}).get("crm_id"),
        event_id=event_id,
        client_name=(crm or {}).get("client_name"),
        client_company=(crm or {}).get("client_company"),
        relationship_owner=(crm or {}).get("relationship_owner"),
        organizer=(cal or {}).get("organizer"),
        attendees=(cal or {}).get("attendees"),
        start_time=start_time,
        end_time=cal_end,
        meeting_type=(crm or {}).get("meeting_type"),
        location=location_decision["location"],
        is_recurring=(cal or {}).get("is_recurring") if cal else None,
        notes=(crm or {}).get("notes"),
        description=(cal or {}).get("description"),
        created_at=created_at,
        has_conflict=bool(conflicts),
    )
    return meeting, conflicts


def reconcile(crm_rows, cal_rows):
    used_cal_ids = set()
    results = []

    for crm in crm_rows:
        cal, duplicates = pick_calendar_match(crm, cal_rows, used_cal_ids)
        if cal is not None:
            used_cal_ids.add(cal["event_id"])
            for dup in duplicates:
                used_cal_ids.add(dup["event_id"])
        results.append(build_meeting(crm, cal, duplicates))

    for cal in cal_rows:
        if cal["event_id"] not in used_cal_ids:
            results.append(build_meeting(None, cal, []))

    return results


def main():
    reconciled = reconcile(load_json(CRM_PATH), load_json(CAL_PATH))
    session = SessionLocal()
    meetings = MeetingService(session)
    conflicts = ConflictService(session)

    try:
        session.query(Conflict).delete()
        session.query(Meeting).delete()

        meeting_count = 0
        conflict_count = 0

        for meeting, conflict_rows in reconciled:
            meetings.create(meeting)
            meeting_count += 1
            for conflict in conflict_rows:
                conflict.meeting_id = meeting.id
            conflict_count += conflicts.create_many(conflict_rows)

        session.commit()
    except Exception as exc:
        session.rollback()
        print(f"Ingest failed: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()

    print(f"Ingested {meeting_count} meetings with {conflict_count} conflicts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
