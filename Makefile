up:
	docker compose up dagster

up-d:
	docker compose up -d dagster

build-no-cache:
	docker compose build --no-cache dagster

down:
	docker compose stop
	docker compose down -v --remove-orphans

ch:
	docker compose up --build -d clickhouse

up-build: down build-no-cache up
