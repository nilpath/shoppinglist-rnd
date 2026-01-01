"""Celery application configuration."""

from celery import Celery

from shoppinglist_rnd.config import get_settings

settings = get_settings()

celery_app = Celery(
    "recipe_importer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["shoppinglist_rnd.workers.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # Soft limit at 4 minutes
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_acks_late=True,  # Acknowledge after task completion
)
