from typing import List, Literal

from pydantic import BaseModel, Field, UUID4


class IngestionMetadata(BaseModel):
    timestamp: str
    record_count: int
    src_paths: List[str] = Field(default_factory=list)


class Recipe(BaseModel):
    id: UUID4
    name: str
    description: str
    url: str
    tags: List[str] = Field(default_factory=list)


class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str


class FullRecipe(Recipe):
    name: str
    url: str
    image: str | None = None
    level_of_difficulty: Literal["easy", "medium", "hard", "unknown"]
    time: int | None = None  # in minutes
    portion: int | None = None
    tags: List[str] = Field(default_factory=list)
    ingredients: List[Ingredient] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
