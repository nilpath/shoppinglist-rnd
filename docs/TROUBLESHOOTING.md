# Troubleshooting

## Redis Connection Error

**Symptom:**

```
Error: Connection refused to redis://localhost:6379
```

**Solution:**

Ensure Redis is running:

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Start Redis (macOS with Homebrew)
brew services start redis

# Or start with Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Or start existing Docker container
docker start redis
```

## Celery Not Processing Tasks

**Symptom:** Tasks stay in "pending" status and never complete.

**Check worker is running:**

```bash
# Should see worker registered and ready
celery -A shoppinglist_rnd.workers.celery_app inspect active
```

**Check broker connection:**

```bash
celery -A shoppinglist_rnd.workers.celery_app inspect ping
```

**Common causes:**

1. Worker not started - run `make worker`
2. Redis not running - see Redis section above
3. Worker crashed - check terminal output for errors

## Database Errors

**Symptom:** Database-related errors on startup or during requests.

**Solution:**

The SQLite database is created automatically on first API startup. To reset:

```bash
# Remove existing database
rm recipes.db

# Restart the API server
make api
```

## Import Errors

**Symptom:** Recipe import tasks fail.

**Solution:**

Check Celery worker logs for detailed error messages. Common issues:

- **Network errors** - Cannot reach the URL
- **Invalid URL format** - URL validation failed
- **DSPy/OpenAI API errors** - API key issues (when implemented)

**View worker logs:**

```bash
# Worker logs appear in the terminal where you ran:
make worker
```

## Module Not Found Errors

**Symptom:**

```
ModuleNotFoundError: No module named 'shoppinglist_rnd'
```

**Solution:**

Ensure the package is installed in development mode:

```bash
uv sync
```

## Port Already in Use

**Symptom:**

```
ERROR: [Errno 48] Address already in use
```

**Solution:**

Another process is using port 8000. Find and kill it:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

Or run the API on a different port:

```bash
uv run uvicorn shoppinglist_rnd.api.main:app --port 8001
```

## Useful Debug Commands

```bash
# Check Celery worker status
celery -A shoppinglist_rnd.workers.celery_app inspect active

# View Celery task queue
celery -A shoppinglist_rnd.workers.celery_app inspect reserved

# Purge all pending tasks
celery -A shoppinglist_rnd.workers.celery_app purge

# Check Redis connection
redis-cli ping

# List Redis keys
redis-cli keys "*"
```
