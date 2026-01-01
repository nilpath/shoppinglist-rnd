.PHONY: install api worker redis-start redis-stop

install:
	uv sync
	uvx playwright install chromium

# Start FastAPI server with auto-reload
api:
	uv run uvicorn shoppinglist_rnd.api.main:app --host 0.0.0.0 --port 8000 --reload

# Start Celery worker
worker:
	uv run celery -A shoppinglist_rnd.workers.celery_app worker --loglevel=info

# Redis management (if installed via homebrew)
redis-start:
	brew services start redis

redis-stop:
	brew services stop redis
