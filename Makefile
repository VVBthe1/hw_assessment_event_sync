.PHONY: up down logs migrate ingest ps

up:
	docker compose up --build

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f

migrate:
	docker compose run --rm migrate

ingest:
	docker compose run --rm --no-deps backend python -m commands.ingest
