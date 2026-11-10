# Frontend UI

Single page (**Meeting Desk**) at `http://localhost:5173` that lists reconciled meetings from `GET /api/meetings`.

## What it shows

Table columns focused on sales usefulness: title, client, representative, type, location, when, source (CRM / Calendar), status.

## Useful bits

- **Pagination** — Prev / Next with cursor paging; pick 10 / 20 / 50 rows per page
- **Status colors** — Confirmed, Scheduled, Tentative, Completed, Cancelled
- **View conflicts** — shown when `has_conflict` is true; opens modal from `GET /api/meetings/{id}/conflicts`
- **View calendar** — shown when sources include calendar; modal with organizer, attendees, times, location, recurrence, description

API base defaults to `http://localhost:8000/api` (`VITE_API_BASE` to override).

## Out of scope

**List filters** (status, source, date, conflicts-only) — deferred. Assessment need is covered by pagination plus conflict/calendar detail; a conflicts-only filter would be the first add if the list grew.
