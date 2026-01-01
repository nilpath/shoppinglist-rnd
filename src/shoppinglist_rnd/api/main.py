"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shoppinglist_rnd.api.routes import recipes
from shoppinglist_rnd.config import get_settings
from shoppinglist_rnd.database import engine
from shoppinglist_rnd.db_models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Application shutting down...")


app = FastAPI(
    title="Recipe Import Service",
    description="Asynchronous recipe import service using DSPy for web scraping",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(recipes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "shoppinglist_rnd.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
