.PHONY: dev test lint migrate seed types clean docker-up docker-down

dev:
	@echo "Starting backend and frontend..."
	python -m uvicorn verifyd.main:app --app-dir apps/api/src --reload --port 8000 &
	cd apps/web && npm run dev

test:
	pytest apps/api/tests -v

lint:
	cd apps/web && npm run build

migrate:
	cd apps/api && alembic upgrade head

seed:
	python scripts/seed.py

types:
	python scripts/generate_types.py

docker-up:
	docker compose up -d

docker-down:
	docker compose down
