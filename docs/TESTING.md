# Testing

## Overview

This document describes testing strategies and how to run tests for the recipe import service.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=shoppinglist_rnd

# Run specific test file
uv run pytest tests/test_api.py

# Run with verbose output
uv run pytest -v
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_api.py          # API endpoint tests
├── test_workers.py      # Celery task tests
└── test_services.py     # Service layer tests
```

## Manual Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Import a Recipe

```bash
curl -X POST http://localhost:8000/api/v1/recipes/import \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/recipe"}'
```

### Check Task Status

```bash
curl http://localhost:8000/api/v1/recipes/import/{task_id}/status
```

### Get Recipe

```bash
curl http://localhost:8000/api/v1/recipes/{recipe_id}
```

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## TODO

- [ ] Add pytest fixtures for database and Redis
- [ ] Add unit tests for services
- [ ] Add integration tests for API endpoints
- [ ] Add Celery task tests with mocked broker
