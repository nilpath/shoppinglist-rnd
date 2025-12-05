import dspy
from typing import Literal

from shoppinglist_rnd.models import Ingredient
from shoppinglist_rnd.browser import Browser


SYSTEM_PROMPT_SHOPPER = """
Pick a product based on:
- Ingredient name
- Ingredient notes (e.g., "1.5%, läng hållbarhet")
- Ingredient category (e.g., "Dairy", "Fruit and vegetables")
- Best unit price (e.g., "25 kr/kg")
- Closest match  to ingredient quantity and unit (e.g., "1 liter", "500 grams")
"""

SYSTEM_PROMPT_QUANTITY_UNIT_CONVERTER = """
Convert ingredient quantities and units based on context.

name, quantity, unit -> converted quantity,converted unit
soja, 1, msk -> 15, ml
vetemjöl, 1, dl -> 90, gram
creme fraiche, 200, gram -> 2, dl
socker, 1, dl -> 85, gram

"""


class Categorize(dspy.Signature):
    ingredient_name: str = dspy.InputField(description="The name of the ingredient to categorize.")
    category: Literal["Fruit and vegetables", "Dairy", "Meats", "Frozen Goods", "Canned Foods", "Dried Goods"] = dspy.OutputField(description="The category of the ingredient.")

class QuantityUnitConverter(dspy.Signature):
    context: str = dspy.InputField(description="Additional context for conversion.")
    ingredient_name: str = dspy.InputField(description="The name of the ingredient.")
    quantity: float = dspy.InputField(description="The quantity of the ingredient.")
    unit: str = dspy.InputField(description="The unit of the ingredient (e.g., grams, liters).")
    converted_quantity: float = dspy.OutputField(description="The converted quantity.")
    converted_unit: str = dspy.OutputField(description="The converted unit.")


class Shopper(dspy.Signature):
    """Shop for ingredients on Willys.se."""

    context: str = dspy.InputField(
        description="Additional context or instructions for shopping."
    )
    ingredients: list[Ingredient] = dspy.InputField(
        description="List of ingredients with name, quantity, unit, and category."
    )
    shopping_result: str = dspy.OutputField(
        description="Summary of shopping actions taken and their results."
    )


class ShoppingListAgent(dspy.Module):

    def __init__(self, headless: bool = False):
        super().__init__()

        self._browser = Browser(headless=headless)

        self.categorizer = dspy.Predict(signature=Categorize)
        self.quantity_unit_converter = dspy.Predict(signature=QuantityUnitConverter)
        self.shopper = dspy.ReAct(
            signature=Shopper,
            tools=self._browser.get_tools(),
            max_iters=15,
        )

    def forward(self, ingredients: list[Ingredient]) -> dspy.Prediction:
        
        for ingredient in ingredients:
            cat_result = self.categorizer(ingredient_name=ingredient.name)
            conv_result = self.quantity_unit_converter(
                context=SYSTEM_PROMPT_QUANTITY_UNIT_CONVERTER,
                ingredient_name=ingredient.name,
                quantity=ingredient.quantity,
                unit=ingredient.unit,
            )

            ingredient.category = cat_result.category
            ingredient.quantity = conv_result.converted_quantity
            ingredient.unit = conv_result.converted_unit

        shopping_result = self.shopper(
            context=SYSTEM_PROMPT_SHOPPER,
            ingredients=ingredients
        )

        return dspy.Prediction(
            ingredients=ingredients,
            shopping_result=shopping_result.shopping_result,
            trajectory=shopping_result.trajectory,
        )

    def close(self) -> None:
        """Clean up browser resources."""
        self._browser.close()

    def wait_for_close(self) -> None:
        """Wait for user to close the browser."""
        self._browser.wait_for_close()
