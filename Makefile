up:
	docker compose -f compose.dagster.yml up

up-d:
	docker compose -f compose.dagster.yml up -d

up-b:
	docker compose -f compose.dagster.yml up --build

build-no-cache:
	docker compose -f compose.dagster.yml build --no-cache

down:
	docker compose -f compose.dagster.yml stop

db:
	docker compose -f compose.db.yml up --build -d

up-build: down build-no-cache up

restart: down up-d
