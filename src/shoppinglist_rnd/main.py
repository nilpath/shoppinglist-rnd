import os

import dspy
import dotenv
import mlflow

from shoppinglist_rnd.agent import ShoppingListAgent
from shoppinglist_rnd.models import Ingredient

dotenv.load_dotenv('.env')

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME"))

mlflow.dspy.autolog()


if __name__ == "__main__":

    lm = dspy.LM("openai/gpt-4o-mini")
    dspy.configure(lm=lm)

    ingredients = [
        Ingredient(name="Äpplen (Royal Gala)", quantity=2, unit="pcs"),
        Ingredient(name="Mjölk", quantity=1, unit="liter", notes="1.5%, lång hållbarhet"),
        Ingredient(name="Fryst Kycklingbröstfilé", quantity=500, unit="grams"),
        Ingredient(name="Frysta ärtor", quantity=300, unit="grams"),
    ]

    agent = ShoppingListAgent()
    try:
        result = agent(ingredients=ingredients)
        print(result)

        print("\nShopping complete! Browse the cart or continue shopping.")
        print("Close the browser window when you're done.")

        agent.wait_for_close()
    finally:
        agent.close()
