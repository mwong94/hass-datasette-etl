up:
	docker compose -f compose.dagster.yml up

up-d:
	docker compose up -f compose.dagster.yml -d

up-b:
	docker compose up -f compose.dagster.yml --build

build-no-cache:
	docker compose build -f compose.dagster.yml --no-cache

down:
	docker compose -f compose.dagster.yml stop

db:
	docker compose -f compose.db.yml up --build -d

up-build: down build-no-cache up

restart: down up-d
