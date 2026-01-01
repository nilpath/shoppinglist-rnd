# Configuration

## Environment Variables

All configuration is managed through environment variables. Copy `.env.example` to `.env` and customize as needed.

```bash
cp .env.example .env
```

## Available Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./recipes.db` | Database connection URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery message broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Celery result backend URL |
| `API_HOST` | `0.0.0.0` | API server bind host |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `false` | Enable debug mode (enables auto-reload) |
| `OPENAI_API_KEY` | `` | OpenAI API key for DSPy |

## Settings Class

Configuration is loaded via `pydantic-settings` in `src/shoppinglist_rnd/config.py`:

```python
from shoppinglist_rnd.config import get_settings

settings = get_settings()
print(settings.database_url)
```

## Database Configuration

### SQLite (Default)

For local development, SQLite is used by default:

```bash
DATABASE_URL=sqlite:///./recipes.db
```

The database file is created automatically on first API startup.

### PostgreSQL (Production)

For production, use PostgreSQL:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/recipes
```

## Redis Configuration

Redis is required for Celery task queue. All three URLs can point to the same Redis instance:

```bash
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Redis with Authentication

```bash
REDIS_URL=redis://:password@localhost:6379/0
```

## API Configuration

```bash
API_HOST=0.0.0.0    # Bind to all interfaces
API_PORT=8000       # Listen on port 8000
DEBUG=false         # Disable debug mode in production
```

## DSPy / OpenAI Configuration

For recipe extraction (when implemented):

```bash
OPENAI_API_KEY=sk-your-api-key-here
```
