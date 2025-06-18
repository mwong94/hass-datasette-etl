up:
	docker compose up -f compose.dagster.yml

up-d:
	docker compose up -d -f compose.dagster.yml

up-b:
	docker compose up --build -f compose.dagster.yml

build-no-cache:
	docker compose build --no-cache -f compose.dagster.yml

down:
	docker compose stop -f compose.dagster.yml

db:
	docker compose up --build -d -f compose.db.yml

up-build: down build-no-cache up

restart: down up-d
