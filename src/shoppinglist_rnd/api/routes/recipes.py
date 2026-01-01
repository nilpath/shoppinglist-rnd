"""Recipe import API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shoppinglist_rnd.api.schemas import (
    IngredientResponse,
    RecipeImportRequest,
    RecipeResponse,
    TaskResponse,
    TaskStatusEnum,
    TaskStatusResponse,
)
from shoppinglist_rnd.database import get_db
from shoppinglist_rnd.db_models import ImportTask, RecipeDB, TaskStatus
from shoppinglist_rnd.workers.tasks import import_recipe_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/import", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_recipe(
    request: RecipeImportRequest,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Start an asynchronous recipe import from a URL.

    Returns a task ID that can be used to check the import status.
    """
    # Create task record in database
    task = ImportTask(
        url=str(request.url),
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(f"Created import task {task.id} for URL: {request.url}")

    # Queue Celery task
    import_recipe_task.delay(task.id, str(request.url))

    return TaskResponse(
        task_id=task.id,
        status=TaskStatusEnum.PENDING,
        message="Recipe import task created and queued for processing",
    )


@router.get("/import/{task_id}/status", response_model=TaskStatusResponse)
async def get_import_status(
    task_id: str,
    db: Session = Depends(get_db),
) -> TaskStatusResponse:
    """
    Check the status of a recipe import task.

    Returns the task status and, if completed, the imported recipe.
    """
    task = db.query(ImportTask).filter(ImportTask.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    # Build recipe response if available
    recipe_response = None
    if task.recipe:
        recipe_response = RecipeResponse(
            id=task.recipe.id,
            name=task.recipe.name,
            description=task.recipe.description,
            url=task.recipe.url,
            image=task.recipe.image,
            level_of_difficulty=task.recipe.level_of_difficulty,
            time=task.recipe.time,
            portion=task.recipe.portion,
            tags=task.recipe.tags or [],
            ingredients=[IngredientResponse(**ing) for ing in (task.recipe.ingredients or [])],
            steps=task.recipe.steps or [],
            created_at=task.recipe.created_at,
        )

    return TaskStatusResponse(
        task_id=task.id,
        status=TaskStatusEnum(task.status.value),
        url=task.url,
        error_message=task.error_message,
        recipe=recipe_response,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    db: Session = Depends(get_db),
) -> RecipeResponse:
    """Get a recipe by ID."""
    recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found",
        )

    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        url=recipe.url,
        image=recipe.image,
        level_of_difficulty=recipe.level_of_difficulty,
        time=recipe.time,
        portion=recipe.portion,
        tags=recipe.tags or [],
        ingredients=[IngredientResponse(**ing) for ing in (recipe.ingredients or [])],
        steps=recipe.steps or [],
        created_at=recipe.created_at,
    )
