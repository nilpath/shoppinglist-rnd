# Development Setup

## Prerequisites

- **Python 3.11+** (managed via pyenv)
- **Redis** (message broker for Celery)
- **uv** (package manager)

## Installation

### 1. Clone and Setup Python Environment

```bash
# Clone the repository
git clone <repository-url>
cd shoppinglist-rnd

# Ensure correct Python version (via pyenv)
pyenv install 3.11
pyenv local 3.11

# Create and activate virtual environment
python -m venv ~/.virtualenvs/shoppinglist-rnd
source ~/.virtualenvs/shoppinglist-rnd/bin/activate

# Install dependencies
uv sync
```

### 2. Install Redis

**macOS (Homebrew):**

```bash
brew install redis
brew services start redis
```

**Docker:**

```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Verify Redis is running:**

```bash
redis-cli ping
# Should return: PONG
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (defaults work for local development)
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./recipes.db` | SQLite database path |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Celery result backend |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `false` | Enable debug mode |
| `OPENAI_API_KEY` | `` | OpenAI API key (for DSPy) |

## Running the Service

You need to run three components: Redis, Celery Worker, and FastAPI Server.

### Terminal 1: Redis (if not using brew services)

```bash
redis-server
```

### Terminal 2: Celery Worker

```bash
make worker
# Or directly:
uv run celery -A shoppinglist_rnd.workers.celery_app worker --loglevel=info
```

### Terminal 3: FastAPI Server

```bash
make api
# Or directly:
uv run uvicorn shoppinglist_rnd.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing the Service

### Health Check

```bash
curl http://localhost:8000/health
# {"status":"healthy"}
```

### Import a Recipe

```bash
# Start an import task
curl -X POST http://localhost:8000/api/v1/recipes/import \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/recipe"}'

# Response:
# {
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "pending",
#   "message": "Recipe import task created and queued for processing"
# }
```

### Check Task Status

```bash
# Replace {task_id} with the actual ID
curl http://localhost:8000/api/v1/recipes/import/{task_id}/status

# Response (when completed):
# {
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "completed",
#   "url": "https://www.example.com/recipe",
#   "recipe": { ... },
#   "created_at": "...",
#   "updated_at": "..."
# }
```

### Get Recipe by ID

```bash
curl http://localhost:8000/api/v1/recipes/{recipe_id}
```

### API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Redis Connection Error

```
Error: Connection refused to redis://localhost:6379
```

**Solution**: Ensure Redis is running:

```bash
# Check if Redis is running
redis-cli ping

# Start Redis (macOS)
brew services start redis

# Or with Docker
docker start redis
```

### Celery Not Processing Tasks

**Check worker is running:**

```bash
# Should see worker registered and ready
celery -A shoppinglist_rnd.workers.celery_app inspect active
```

**Check broker connection:**

```bash
celery -A shoppinglist_rnd.workers.celery_app inspect ping
```

### Database Errors

The SQLite database is created automatically on first API startup. If you need to reset:

```bash
rm recipes.db
# Restart the API server
```

### Import Errors

Check Celery worker logs for detailed error messages. Common issues:

- Network errors fetching URLs
- Invalid URL format
- DSPy/OpenAI API errors (when implemented)

## Development Workflow

1. **Make changes** to the code
2. **API server** auto-reloads with `--reload` flag
3. **Celery worker** needs manual restart after code changes
4. **Run tests** (when implemented): `uv run pytest`

## Useful Commands

```bash
# Install dependencies
make install

# Start API server
make api

# Start Celery worker
make worker

# Check Celery worker status
celery -A shoppinglist_rnd.workers.celery_app inspect active

# View Celery task queue
celery -A shoppinglist_rnd.workers.celery_app inspect reserved

# Purge all pending tasks
celery -A shoppinglist_rnd.workers.celery_app purge
```
