# API contracts

Base: `http://localhost:8000/api`

Datetimes are ISO-8601 strings. `null` means the field is absent for that meeting.

---

## `GET /meetings`

Cursor-paginated meeting list. Ordered by `id` ascending.

| Query | Type | Default | Notes |
|---|---|---|---|
| `cursor` | `number \| omit` | — | Return meetings with `id > cursor` |
| `limit` | `number` | `20` | `1..100` |

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

Use `has_conflict` to decide whether to fetch conflicts.

---

## `GET /meetings/{meeting_id}/conflicts`

All conflicted fields for one meeting. Not paginated.

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

**404** — meeting does not exist
```json
{ "detail": "Meeting not found" }
```
