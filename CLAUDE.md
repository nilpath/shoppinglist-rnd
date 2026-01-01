# shoppinglist-rnd

Recipe import service using FastAPI, Celery, and DSPy.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, components, and technical decisions |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Environment variables and application settings |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Running the API, Celery worker, and Redis |
| [docs/TESTING.md](docs/TESTING.md) | Testing strategies and running tests |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |

## Quick Start

```bash
# 1. Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# 2. Start Celery worker
make worker

# 3. Start API server
make api
```

## Project Structure

```
src/shoppinglist_rnd/
├── api/           # FastAPI endpoints
├── workers/       # Celery tasks
├── services/      # Business logic (recipe extraction)
├── db_models.py   # SQLAlchemy database models
├── config.py      # Application settings
└── database.py    # Database connection
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/recipes/import` | Start recipe import from URL |
| GET | `/api/v1/recipes/import/{task_id}/status` | Check import task status |
| GET | `/api/v1/recipes/{recipe_id}` | Get recipe by ID |
| GET | `/health` | Health check |

## Tech Stack

- **FastAPI** - REST API framework
- **Celery** - Async task queue
- **Redis** - Message broker
- **SQLite** - Database (SQLAlchemy ORM)
- **DSPy** - LLM-based recipe extraction (placeholder)
