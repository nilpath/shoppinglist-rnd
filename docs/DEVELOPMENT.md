# Deployment

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

**Verify Redis is running:**

```bash
redis-cli ping
# Should return: PONG
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (defaults work for local development)
```

See [CONFIGURATION.md](CONFIGURATION.md) for all available settings.

## Running the Service

You need to run three components: Redis, Celery Worker, and FastAPI Server.

### Terminal 1: Redis (if not using brew services)

```bash
redis-server
```

### Terminal 2: Celery Worker

```bash
make worker
```

Or directly:

```bash
uv run celery -A shoppinglist_rnd.workers.celery_app worker --loglevel=info
```

### Terminal 3: FastAPI Server

```bash
make api
```

Or directly:

```bash
uv run uvicorn shoppinglist_rnd.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Makefile Commands

```bash
make install     # Install dependencies
make api         # Start FastAPI server with auto-reload
make worker      # Start Celery worker
make redis-start # Start Redis (Homebrew)
make redis-stop  # Stop Redis (Homebrew)
```

## Development Workflow

1. **Make changes** to the code
2. **API server** auto-reloads with `--reload` flag
3. **Celery worker** needs manual restart after code changes

## Production Deployment

For production, consider:

1. **Use PostgreSQL** instead of SQLite
2. **Run with gunicorn** instead of uvicorn directly
3. **Use a process manager** (systemd, supervisor) for workers
4. **Set up Redis persistence** or use a managed Redis service
5. **Configure proper logging** and monitoring

### Example Production Commands

```bash
# API with gunicorn
gunicorn shoppinglist_rnd.api.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Celery with multiple workers
celery -A shoppinglist_rnd.workers.celery_app worker --concurrency=4 --loglevel=warning
```

## Health Checks

```bash
# API health check
curl http://localhost:8000/health

# Celery worker health
celery -A shoppinglist_rnd.workers.celery_app inspect ping
```
