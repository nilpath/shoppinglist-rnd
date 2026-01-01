"""Main recipe import business logic."""

import logging
from typing import Any, Dict

from shoppinglist_rnd.services.recipe_extractor import RecipeExtractor

logger = logging.getLogger(__name__)


class RecipeImporter:
    """
    Service for importing recipes from URLs.

    Orchestrates the full import process:
    1. Fetch webpage content
    2. Extract recipe data using DSPy agent
    3. Validate and normalize data
    """

    def __init__(self):
        self.extractor = RecipeExtractor()

    def import_from_url(self, url: str) -> Dict[str, Any]:
        """
        Import a recipe from a URL.

        Args:
            url: The URL to import from

        Returns:
            Dictionary containing the extracted recipe data
        """
        logger.info(f"Importing recipe from URL: {url}")

        # Extract recipe data
        recipe_data = self.extractor.extract(url)

        # Validate and normalize
        normalized_data = self._normalize_recipe_data(recipe_data)

        logger.info(f"Successfully extracted recipe: {normalized_data.get('name', 'Unknown')}")

        return normalized_data

    def _normalize_recipe_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate extracted recipe data.

        Ensures all required fields are present and properly formatted.
        """
        # Ensure required fields
        if not data.get("name"):
            data["name"] = "Untitled Recipe"

        # Normalize level_of_difficulty
        valid_difficulties = ["easy", "medium", "hard", "unknown"]
        if data.get("level_of_difficulty") not in valid_difficulties:
            data["level_of_difficulty"] = "unknown"

        # Ensure lists are lists
        for list_field in ["tags", "ingredients", "steps"]:
            if not isinstance(data.get(list_field), list):
                data[list_field] = []

        # Normalize ingredients format
        normalized_ingredients = []
        for ing in data.get("ingredients", []):
            if isinstance(ing, dict):
                normalized_ingredients.append({
                    "name": ing.get("name", ""),
                    "quantity": float(ing.get("quantity", 0)),
                    "unit": ing.get("unit", ""),
                })
        data["ingredients"] = normalized_ingredients

        return data
