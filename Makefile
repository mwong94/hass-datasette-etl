up:
	docker compose up dagster

up-d:
	docker compose up -d dagster

up-b:
	docker compose up --build dagster

build-no-cache:
	docker compose build --no-cache dagster

down:
	docker compose stop

db:
	docker compose up --build -d clickhouse

up-build: down build-no-cache up
