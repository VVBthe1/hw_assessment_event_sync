# Data model

Unified output after ingesting CRM + calendar. List UI reads `meetings`; conflict detail UI reads `conflicts` when `has_conflict` is true.

---

## `meetings`

Resolved row only — chosen values, not dual-source blobs.

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Auto-increment primary key. |
| `crm_id` | string \| null | From CRM when present. |
| `event_id` | string \| null | Calendar `event_id` linked to this meeting. If two calendar rows look like the same event, store only one id here (the kept row); record the discarded id in `conflicts`. |
| `sources` | string[] | `["crm"]`, `["calendar"]`, or both. |
| `title` | string | Calendar `title` when calendar is present; else CRM `subject`. |
| `client_name` | string \| null | CRM-only. Null on internal meetings is expected. |
| `client_company` | string \| null | CRM-only. Null on internal meetings is expected. |
| `relationship_owner` | string \| null | CRM-only. |
| `organizer` | string \| null | Calendar-only email. |
| `attendees` | string[] \| null | Calendar-only. |
| `start_time` | datetime \| null | Calendar `start_time` when present; else CRM `meeting_date` + `meeting_time` (`%Y-%m-%d` / `%H:%M` only). Invalid dates are skipped; CRM time may be missing. Timestamps without `Z` are naive local. Timestamps ending in `Z` are UTC → convert to `America/New_York` before compare/store. |
| `end_time` | datetime \| null | Calendar-only; null for CRM-only rows. |
| `meeting_type` | string \| null | CRM-only (`In-Person` / `Virtual` / `Internal`). |
| `location` | string \| null | If `In-Person`, CRM location; if `Virtual`, calendar location (join links). If only one side has a value, use that. |
| `is_recurring` | bool \| null | Calendar-only. |
| `status` | string | CRM `status` when present; else calendar status mapped `confirmed` → `Confirmed`, `tentative` → `Tentative`. |
| `notes` | string \| null | CRM `notes`. |
| `description` | string \| null | Calendar `description`. |
| `created_at` | datetime \| null | `min` of available source `created_at` values. |
| `has_conflict` | bool | Default `false`. True when this meeting has one or more rows in `conflicts`. |

---

## `conflicts`

Separate from the meeting row. One row per disagreed field (or duplicate-calendar case).

| Field | Type | Notes |
|---|---|---|
| `meeting_id` | integer | FK to `meetings.id`. |
| `field` | string | e.g. `location`, `start_time`, `title`, `status`, `event_id`. |
| `crm_value` | any \| null | Value from CRM for this field. |
| `calendar_value` | any \| null | Value from calendar for this field. |
| `chosen` | any | Value written onto the meeting row. |
| `reason` | string | Human-readable explanation of why this was flagged and what we kept (free text, not a fixed code enum). |

Conflict flagging rules live in `ingestion.md`.

---

## Storage

MySQL runs as the local environment via Docker. Schema is applied as a one-shot SQL script (`db/schema.sql`) under the setup/start command (create `meetings` + `conflicts`, then ingest).
