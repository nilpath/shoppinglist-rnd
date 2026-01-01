"""Celery task definitions."""

import logging

from shoppinglist_rnd.database import get_db_session
from shoppinglist_rnd.db_models import ImportTask, RecipeDB, TaskStatus
from shoppinglist_rnd.services.recipe_importer import RecipeImporter
from shoppinglist_rnd.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def import_recipe_task(self, task_id: str, url: str):
    """
    Celery task to import a recipe from a URL.

    Args:
        task_id: The database ID of the ImportTask record
        url: The URL to import the recipe from
    """
    logger.info(f"Starting recipe import task {task_id} for URL: {url}")

    with get_db_session() as db:
        # Update task status to processing
        task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found in database")
            return

        task.status = TaskStatus.PROCESSING
        db.commit()

        try:
            # Import the recipe
            importer = RecipeImporter()
            recipe_data = importer.import_from_url(url)

            # Create recipe record
            recipe = RecipeDB(
                name=recipe_data["name"],
                description=recipe_data.get("description"),
                url=url,
                image=recipe_data.get("image"),
                level_of_difficulty=recipe_data.get("level_of_difficulty", "unknown"),
                time=recipe_data.get("time"),
                portion=recipe_data.get("portion"),
                tags=recipe_data.get("tags", []),
                ingredients=recipe_data.get("ingredients", []),
                steps=recipe_data.get("steps", []),
            )
            db.add(recipe)
            db.flush()  # Get the recipe ID

            # Update task with success
            task.status = TaskStatus.COMPLETED
            task.recipe_id = recipe.id
            db.commit()

            logger.info(f"Successfully imported recipe {recipe.id} for task {task_id}")

        except Exception as e:
            logger.exception(f"Failed to import recipe for task {task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            db.commit()

            # Retry on transient failures
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e)
