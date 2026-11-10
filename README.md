# Event Sync Service

Reconciles client meetings from a CRM export and a calendar export into one list, exposes them over a REST API, and shows conflicts in a simple web UI.

**Stack:** FastAPI · MySQL 8 · React (Vite) · Docker Compose

---

## Setup

**Prerequisites:** Docker Desktop (or Engine + Compose v2).

```bash
docker compose up --build
```

Open **http://localhost:5173** when the frontend is up.

**Important links**

| Endpoint | URL |
|---|---|
| UI | http://localhost:5173 |
| API docs | http://localhost:8000/docs |
| List meetings | `GET /api/meetings` |
| Meeting conflicts | `GET /api/meetings/{id}/conflicts` |

Reload data without restarting / env / reset: [`plan/setup.md`](plan/setup.md).

---

## Approach & key decisions

Sources do not share IDs. Matching and field resolution happen in Python at ingest time; the API serves already-reconciled rows.

1. **Match in Python, not SQL** — Score CRM↔calendar pairs (same day, time closeness, company/title overlap). Keep matches above a threshold. Dataset is small (~20×22); a nested loop stays readable. Staging tables + SQL candidate filter were considered and deferred (see `plan/ingestion.md`).
2. **Resolved row + separate conflicts** — `meetings` stores chosen values only. Disagreements live in `conflicts` with `crm_value`, `calendar_value`, `chosen`, and a human-readable `reason`. List UI provides an option to view conflicts when they exist (`has_conflict=true`).
3. **Merge rules for conflicts**
   - **Title** — calendar `title` when present, else CRM `subject`
   - **Start / end** — calendar timing when present; else CRM date (+ time when available)
   - **Status** — CRM wins; calendar maps `confirmed`/`tentative` only when CRM is absent
   - **Location** — In-Person → CRM place; Virtual → calendar join link; single-sided value fills through
4. **Conflict only when both sides disagree** — Empty on one side is a fill, not a conflict. Flag location, start time, status (e.g. CRM Cancelled vs calendar confirmed), title, and duplicate calendar events.
5. **Timezone** — Timestamps ending in `Z` are treated as UTC and converted to `America/New_York` before compare/store. Naive stamps are treated as local Eastern.
6. **Single-command local stack** — `docker compose up --build` brings up MySQL, migrate, ingest, backend, and frontend in order.
7. **No list filters** — Meeting Desk stays a paginated reconciled list with conflict/calendar actions. Status/source/date filters deferred (see `plan/ui.md`).

---

## API contracts

Base: `http://localhost:8000/api`  
Datetimes are ISO-8601 strings. `null` means the field is absent for that meeting.

### `GET /meetings`

Cursor-paginated list, ordered by `id` ascending.

| Query | Type | Default | Notes |
|---|---|---|---|
| `cursor` | number \| omit | — | Return meetings with `id > cursor` |
| `limit` | number | `20` | `1..100` |

**200**
```json
{
  "items": [Meeting],
  "next_cursor": 12
}
```

`next_cursor` is the last item’s `id`, or `null` on the last page.

**Meeting**
```ts
{
  id: number
  crm_id: string | null
  event_id: string | null
  sources: ("crm" | "calendar")[]
  title: string
  client_name: string | null
  client_company: string | null
  relationship_owner: string | null
  organizer: string | null
  attendees: string[] | null
  start_time: string | null
  end_time: string | null
  meeting_type: string | null
  location: string | null
  is_recurring: boolean | null
  status: string
  notes: string | null
  description: string | null
  created_at: string | null
  has_conflict: boolean
}
```

### `GET /meetings/{meeting_id}/conflicts`

All conflicted fields for one meeting (not paginated).

**200** — `Conflict[]` (may be empty)

```ts
{
  id: number
  meeting_id: number
  field: string
  crm_value: unknown | null
  calendar_value: unknown | null
  chosen: unknown | null
  reason: string
}
```

**404** — `{ "detail": "Meeting not found" }`

Interactive docs: http://localhost:8000/docs

---

## UI

Single page **Meeting Desk** at http://localhost:5173.

- Table of reconciled meetings (title, client, representative, type, location, when, sources, status)
- Cursor pagination with page size 10 / 20 / 50
- **View conflicts** when `has_conflict` is true — side-by-side CRM vs calendar values and chosen reason
- **View calendar** when sources include calendar — organizer, attendees, times, location, recurrence, description

API base defaults to `http://localhost:8000/api` (`VITE_API_BASE` to override).

---

## Assumptions

- **No shared upstream ID** — Matching is heuristic (time + text), not deterministic keys. Ambiguous pairs can be wrong; scores favor strong time + title/company overlap.
- **Sales timezone** — Eastern (`America/New_York`) is the canonical local zone for this dataset.
- **CRM date/time shapes** — Dates only as `%Y-%m-%d` (invalid → drop start); missing time → midnight local; near-duplicate text (e.g. `Conference Room B` vs `HQ - Conference Room B`) counts as the same.
- **CRM-only client fields** — `client_name` / `client_company` null on internal or calendar-only meetings is expected.
- **Resolved values in the list** — Table cells show the merged/chosen field. Meeting-level `sources` pills show which systems contributed; per-field CRM vs calendar detail is in the conflict modal when `has_conflict` is true.
- **Duplicate calendar rows** — Keep one `event_id` on the meeting; discarded id is recorded as a conflict (not a separate meeting).

## Out of scope

- **No automated tests** — The brief does not evaluate test coverage; none included.
- **No list filters** — Paginated list only; no status/source/conflicts-only filtering.
- **Destructive migrate** — `db/schema.sql` drops and recreates `meetings` / `conflicts`. Re-ingest after migrate, or `docker compose down -v && docker compose up --build` for a full reset.

---

## Planning notes (AI-assisted)

Design notes from the build live under [`plan/`](plan/):

| File | Contents |
|---|---|
| [`plan/setup.md`](plan/setup.md) | Single-command start, Compose services, common commands, env, reset |
| [`plan/ingestion.md`](plan/ingestion.md) | Matching, conflict rules, deferred staging approach |
| [`plan/data-model.md`](plan/data-model.md) | Field meanings and winners |
| [`plan/api.md`](plan/api.md) | API contract detail |
| [`plan/ui.md`](plan/ui.md) | Frontend scope |

---

**Time spent:** 6 hours.
