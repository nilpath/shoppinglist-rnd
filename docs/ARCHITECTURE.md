# Architecture

## System Overview

The Recipe Import Service is an asynchronous system for importing recipes from URLs. It uses a task queue pattern to handle long-running web scraping and AI extraction operations without blocking the API.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI   │────▶│    Redis    │────▶│   Celery    │
│             │     │   Server    │     │   (Broker)  │     │   Worker    │
└─────────────┘     └──────┬──────┘     └─────────────┘     └──────┬──────┘
                           │                                       │
                           │                                       │
                           ▼                                       ▼
                    ┌─────────────┐                         ┌─────────────┐
                    │   SQLite    │◀────────────────────────│   DSPy      │
                    │  Database   │                         │   Agent     │
                    └─────────────┘                         └─────────────┘
```

## Technology Choices

### FastAPI

**Why FastAPI?**

- Modern, fast Python web framework with automatic OpenAPI documentation
- Native async support for handling concurrent requests
- Built-in request validation via Pydantic
- Excellent developer experience with type hints

### Celery + Redis

**Why Celery?**

- Mature, battle-tested distributed task queue
- Supports task retries, rate limiting, and scheduling
- Excellent monitoring tools (Flower, celery events)
- Handles long-running tasks without blocking the API

**Why Redis as broker?**

- Fast in-memory data store
- Simple setup and operation
- Supports both message broker and result backend roles
- Low latency for task dispatch

### SQLite

**Why SQLite?**

- Zero configuration database
- Perfect for development and small-to-medium workloads
- Single file storage, easy to backup
- Can be migrated to PostgreSQL later if needed

### DSPy (Future)

**Why DSPy?**

- Declarative approach to LLM programming
- Automatic prompt optimization
- Structured output extraction
- Easy to test and iterate on extraction logic

## Database Design

### Entity Relationship

```
┌─────────────────────────────┐       ┌─────────────────────────────┐
│       import_tasks          │       │          recipes            │
├─────────────────────────────┤       ├─────────────────────────────┤
│ id (PK, UUID)               │───┐   │ id (PK, UUID)               │
│ url (VARCHAR 2048)          │   │   │ name (VARCHAR 500)          │
│ status (ENUM)               │   │   │ description (TEXT)          │
│ error_message (TEXT)        │   │   │ url (VARCHAR 2048)          │
│ recipe_id (FK) ─────────────┼───┴──▶│ image (VARCHAR 2048)        │
│ created_at (DATETIME)       │       │ level_of_difficulty (VARCHAR)│
│ updated_at (DATETIME)       │       │ time (INTEGER)              │
└─────────────────────────────┘       │ portion (INTEGER)           │
                                      │ tags (JSON)                 │
                                      │ ingredients (JSON)          │
                                      │ steps (JSON)                │
                                      │ created_at (DATETIME)       │
                                      │ updated_at (DATETIME)       │
                                      └─────────────────────────────┘
```

### Design Decisions

**UUID Primary Keys**

- Allows distributed ID generation
- No sequential ID exposure (security)
- Can be generated client-side if needed

**JSON Columns for Lists**

- Simplifies schema (no junction tables needed)
- Keeps recipe data together
- SQLite has good JSON support since 3.38
- Trade-off: harder to query individual ingredients

**Separate Task Table**

- Decouples import tracking from recipe storage
- Can track failed imports without recipe records
- Supports re-importing same URL
- Maintains full import history

**Task Status Enum**

- Ensures data integrity
- Clear state machine: pending → processing → completed/failed
- Efficient status queries

## API Design

### RESTful Patterns

- `POST /api/v1/recipes/import` - Create import task (returns 202 Accepted)
- `GET /api/v1/recipes/import/{task_id}/status` - Check task status
- `GET /api/v1/recipes/{recipe_id}` - Get recipe by ID

### Async Pattern

The import endpoint returns immediately with a task ID. Clients poll the status endpoint to check completion. This pattern:

- Prevents request timeouts for slow imports
- Allows the API to handle many concurrent requests
- Provides progress visibility to clients

## Task Flow

```
1. Client POSTs URL to /api/v1/recipes/import
2. API creates ImportTask record (status: PENDING)
3. API queues Celery task with task_id and URL
4. API returns 202 with task_id

5. Celery worker picks up task
6. Worker updates status to PROCESSING
7. Worker calls RecipeExtractor.extract(url)
   - Fetches webpage content
   - Uses DSPy to extract structured data
8. Worker creates RecipeDB record
9. Worker links recipe to task, sets status COMPLETED

On failure:
- Worker sets status to FAILED
- Worker stores error_message
- Worker may retry (up to 3 times)
```

## Future Considerations

### Scaling

- **Multiple Workers**: Celery supports multiple workers for parallel processing
- **PostgreSQL**: Migrate from SQLite for production workloads
- **Redis Cluster**: For high-availability message broker

### DSPy Integration

- Implement actual recipe extraction in `RecipeExtractor`
- Add prompt optimization using DSPy's compilation
- Consider caching extracted recipes by URL hash

### Additional Features

- Webhook notifications on task completion
- Batch import endpoints
- Recipe deduplication
- Image downloading and storage
