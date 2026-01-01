"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class TaskStatusEnum(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request schemas
class RecipeImportRequest(BaseModel):
    """Request body for importing a recipe."""

    url: HttpUrl = Field(..., description="URL of the recipe to import")


# Response schemas
class TaskResponse(BaseModel):
    """Response for task creation."""

    task_id: str = Field(..., description="Unique identifier for the import task")
    status: TaskStatusEnum
    message: str

    class Config:
        from_attributes = True


class IngredientResponse(BaseModel):
    """Ingredient in a recipe."""

    name: str
    quantity: float
    unit: str


class RecipeResponse(BaseModel):
    """Full recipe response."""

    id: str
    name: str
    description: Optional[str] = None
    url: str
    image: Optional[str] = None
    level_of_difficulty: str
    time: Optional[int] = None
    portion: Optional[int] = None
    tags: List[str] = []
    ingredients: List[IngredientResponse] = []
    steps: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    """Response for task status check."""

    task_id: str
    status: TaskStatusEnum
    url: str
    error_message: Optional[str] = None
    recipe: Optional[RecipeResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
