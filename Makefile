up:
	docker compose up

up-d:
	docker compose up -d

build-no-cache:
	docker compose build --no-cache

down:
	docker compose stop
	docker compose down -v --remove-orphans

up-build: down build-no-cache up
