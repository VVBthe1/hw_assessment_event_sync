# Ingestion

Match CRM and calendar rows in Python (same day + time closeness; company/title as backup). Merge into `meetings` with field rules from the data model. CRM wins status; calendar wins timing when present; location depends on meeting type.

Current matching is an `O(n·m)` nested loop with a score threshold. Fine for this dataset (~20×22).

## Conflict flagging

Flag a conflict only when both CRM and calendar have a value for the field and they disagree after applying the meeting field rules. If one side is empty, fill from the other — no conflict.

Flag in these cases:

1. **Location** — CRM says in-person place, calendar says Zoom/Teams/Meet (or the two locations clearly name different places). Meeting keeps the location from the `location` field rule; `reason` explains the mismatch.
2. **Start time** — after parsing (and converting any `Z` time to `America/New_York`), starts are not the same. Meeting keeps calendar `start_time` when calendar is present.
3. **Status** — CRM is `Cancelled` but calendar is still `confirmed` (CRM status stays on the meeting).
4. **Title** — calendar `title` and CRM `subject` both present and clearly different. Meeting keeps calendar `title`.
5. **Duplicate calendar** — two calendar events look like the same meeting (overlapping time, same organizer / shared attendees / similar title). Keep one `event_id` on the meeting; conflict row notes the other id.

Same-looking values should not flag (e.g. `Conference Room B` vs `HQ - Conference Room B`). After writing any conflict rows, set `has_conflict = true` on the meeting.

## Why not staging tables (deferred)

A more “ingest-shaped” pipeline would be:

1. Load raw CRM + calendar JSON into staging/temp tables with normalized `start_time` (incl. `Z` → `America/New_York`).
2. SQL-filter candidates (same day and/or start within ±60 min; optional company/title filters).
3. Run score / merge / conflict rules in Python only on that shortlist.
4. Write resolved `meetings` + `conflicts`; drop or truncate staging.

That fits a real ETL path (DB does the cheap filter; app keeps the judgment calls). **Not worth implementing here** — assessment time, explainability, and data size. Revisit if volume grows or matching rules get heavier.
