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
    notes: str | None = None
    category: str | None = None


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


class Product(BaseModel):
    """Represents a product from Willys search results."""

    name: str = Field(description="Product name/title")
    price: float = Field(description="Current price in SEK")
    unit_price: str | None = Field(default=None, description="Price per unit (e.g., '25 kr/kg')")
    image_url: str | None = Field(default=None, description="URL to product image")
    product_id: str | None = Field(default=None, description="Unique product identifier")
    brand: str | None = Field(default=None, description="Product brand")
    quantity_in_cart: int = Field(default=0, description="Current quantity in cart")


class SearchResult(BaseModel):
    """Represents search results from Willys."""

    query: str = Field(description="The search query used")
    products: List[Product] = Field(default_factory=list, description="List of products found")
    total_count: int = Field(default=0, description="Total number of results")


class AddToCartResult(BaseModel):
    """Result of adding a product to cart."""

    success: bool
    product_name: str
    quantity: int
    message: str = Field(default="")
