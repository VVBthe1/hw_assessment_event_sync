# Event Sync — local Docker environment

## Start

```bash
docker compose up --build
```

Starts MySQL, applies `db/schema.sql`, then backend and frontend.

| Service | Port |
|---|---|
| MySQL | 3306 |
| Backend (FastAPI) | 8000 |
| Frontend (React) | 5173 |

## Ingest

```bash
docker compose run --rm --no-deps backend python -m commands.ingest
```

## Stop

```bash
docker compose down
```
