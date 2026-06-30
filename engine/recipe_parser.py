import json
import re

from engine.data_store import items, production_buildings, recipes
from engine.models import Form, Item, Recipe, StackSize

# # TODO: figure out a way to have this find the user's game data
docs_path = "scripts/en-US.json"

with open(docs_path, mode="r", encoding="utf-16") as read_file:
    docs_raw = json.load(read_file)

docs_unwrap_intermediate: dict[str, dict] = {}
docs_unwrap: dict[str, dict] = {}

for category in docs_raw:
    category_name = category["NativeClass"].split(".")[2].rstrip("'")
    docs_unwrap_intermediate[category_name] = category["Classes"]
    docs_unwrap[category_name] = {}
    for class_dict in category["Classes"]:
        docs_unwrap[category_name][class_dict["ClassName"]] = class_dict

# print(type(recipes.keys()))


def find_item(item_name: str, expected_categories: list[str]) -> Item | None:
    # The check for already being documented will happen outside this function
    # Find the data for the item with this name, starting with the "Expected categories"
    for category in expected_categories:
        if item_name in docs_unwrap[category].keys():
            item_data = docs_unwrap[category][item_name]
            return Item(
                item_name=item_data["FullName"],
                display_name=item_data["mDisplayName"],
                stack_size=StackSize(item_data["mCachedStackSize"]),
                can_be_discarded=item_data["mCanBeDiscarded"],
                resource_sink_points=item_data["mResourceSinkPoints"],
                energy_value=item_data["mEnergyValue"],
                form=Form(item_data["mForm"]),
            )

    print(f"{item_name} not found in any of the expected categories")
    for category in docs_unwrap:
        if item_name in docs_unwrap[category]:
            print(f"{item_name} found in {category}!")
            item_data = docs_unwrap[category][item_name]
            return Item(
                item_name=item_data["FullName"],
                display_name=item_data["mDisplayName"],
                stack_size=StackSize(item_data["mCachedStackSize"]),
                can_be_discarded=item_data["mCanBeDiscarded"],
                resource_sink_points=item_data["mResourceSinkPoints"],
                energy_value=item_data["mEnergyValue"],
                form=Form(item_data["mForm"]),
            )

    print(f"ERROR: {item_name} not found in any category.")


for target_recipe in docs_unwrap["FGRecipe"].values():
    if "Recipe.Part" in target_recipe["mGameplayTags"]:
        target_ingredients_raw = target_recipe["mIngredients"]
        target_ingredients_cleaned = re.findall(
            r".+?\.Desc_(\w+)_C\'\",Amount=(\d+).*?", target_ingredients_raw
        )
        target_products_raw = target_recipe["mProduct"]
        target_products_cleaned = re.findall(
            r".+?\.Desc_(\w+)_C\'\",Amount=(\d+).*?", target_products_raw
        )

    # recipes[target_recipe["ClassName"]] = Recipe(
    #     recipe_name = target_recipe["ClassName"],
    #     display_name = target_recipe["mDisplayName"],
    #     ingredients =
    # )
