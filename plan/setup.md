# Local setup (Docker & Make)

Local stack is Compose-only. Makefile wraps the common Compose commands.

**Prerequisites:** Docker Desktop (or Engine + Compose v2).

---

## Single command

```bash
make up
```

Equivalent: `docker compose up --build`

**Startup order:** `mysql` healthy → `migrate` succeeds → `ingest` succeeds → `backend` → `frontend`.

Open **http://localhost:5173** when frontend is up.

---

## Services

| Service | Role | Host port (default) |
|---|---|---|
| `mysql` | MySQL 8.4 + named volume `mysql_data` | `3306` |
| `migrate` | One-shot: apply `db/schema.sql`, then exit | — |
| `ingest` | One-shot: load CRM + calendar JSON into MySQL | — |
| `backend` | FastAPI (`uvicorn`, reload) | `8000` |
| `frontend` | Vite React (`npm run dev`) | `5173` |

`migrate` drops and recreates `meetings` / `conflicts` every time it runs. Backend/ingest mount `./data` read-only at `/data`.

---

## Make targets

| Target | Equivalent | Notes |
|---|---|---|
| `make up` | `docker compose up --build` | Full stack + ingest; Ctrl+C stops attached processes |
| `make down` | `docker compose down` | Keeps MySQL volume |
| `make ps` | `docker compose ps` | Container status |
| `make logs` | `docker compose logs -f` | Follow all service logs |
| `make migrate` | `docker compose run --rm migrate` | Re-apply schema (destructive) |
| `make ingest` | `docker compose run --rm --no-deps backend python -m commands.ingest` | Re-load JSON without restarting the stack |

---

## Env

Copy `.env.example` → `.env` only if you need to change defaults.

| Variable | Default | Used by |
|---|---|---|
| `MYSQL_ROOT_PASSWORD` | `root` | mysql, migrate |
| `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD` | `event_sync` | mysql, backend/ingest `DATABASE_URL` |
| `MYSQL_PORT` | `3306` | host map |
| `BACKEND_PORT` | `8000` | host map |
| `FRONTEND_PORT` | `5173` | host map |
| `DATABASE_URL` | (Compose builds it) | backend/ingest; `.env.example` also shows a host-local form for non-Docker runs |

---

## Reset

```bash
make migrate   # wipe + recreate tables
make ingest    # reload JSON
# or: docker compose down -v && make up
```
