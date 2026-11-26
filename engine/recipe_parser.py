import json
import re
from dataclasses import asdict, is_dataclass
from enum import Enum

from engine.data_store import items, recipes
from engine.models import (
    # BuildableManufacturer,
    # BuildableManufacturerName,
    Form,
    Item,
    Recipe,
    StackSize,
    VariablePower,
)


def parse_game_data(docs_path) -> tuple[dict[str, Item], dict[str, Recipe]]:
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

    expected_item_categories = [
        "FGItemDescriptor",
        "FGItemDescriptorBiomass",
        "FGItemDescriptorNuclearFuel",
        "FGItemDescriptorPowerBoosterFuel",
        "FGResourceDescriptor",
        "FGEquipmentDescriptor",
        "FGAmmoTypeProjectile",
        "FGPowerShardDescriptor",
        "FGAmmoTypeInstantHit",
        "FGAmmoTypeSpreadshot",
        "FGConsumableDescriptor",
    ]


    def find_item(item_name: str, expected_categories: list[str]) -> Item | None:
        # The check for already being documented will happen outside this function
        # Find the data for the item with this name, starting with the "Expected categories"
        for category in expected_categories:
            if item_name in docs_unwrap[category]:
                item_data = docs_unwrap[category][item_name]
                return Item(
                    item_name=item_data["ClassName"],
                    display_name=item_data["mDisplayName"],
                    stack_size=StackSize(int(item_data["mCachedStackSize"])),
                    can_be_discarded=item_data["mCanBeDiscarded"] == "True",
                    resource_sink_points=int(item_data["mResourceSinkPoints"]),
                    energy_value=float(item_data["mEnergyValue"]),
                    form=Form(item_data["mForm"]),
                )

        print(f"{item_name} not found in any of the expected categories")
        for category in docs_unwrap.values():
            if item_name in category:
                # print(f"{item_name} found in {category_name}!")
                item_data = category[item_name]
                return Item(
                    item_name=item_data["ClassName"],
                    display_name=item_data["mDisplayName"],
                    stack_size=StackSize(int(item_data["mCachedStackSize"])),
                    can_be_discarded=item_data["mCanBeDiscarded"] == "True",
                    resource_sink_points=int(item_data["mResourceSinkPoints"]),
                    energy_value=float(item_data["mEnergyValue"]),
                    form=Form(item_data["mForm"]),
                )


    for target_recipe in docs_unwrap["FGRecipe"].values():
        buildings_list = target_recipe["mProducedIn"]
        buildings_list_parsed = re.findall(r".+?Factory/(\w+)/Build", buildings_list)
        if "AutomatedWorkBench" in buildings_list_parsed:
            buildings_list_parsed.remove("AutomatedWorkBench")
        if len(buildings_list_parsed) == 1:
            target_ingredients_raw = target_recipe["mIngredients"]
            target_ingredients_cleaned = re.findall(
                r".+?\.(Desc_\w+_C)\'\",Amount=(\d+).*?", target_ingredients_raw
            )
            target_products_raw = target_recipe["mProduct"]
            target_products_cleaned = re.findall(
                r".+?\.(Desc_\w+_C)\'\",Amount=(\d+).*?", target_products_raw
            )
            target_ingredients_cooked = {}
            target_products_cooked = {}
            for ingredient_tuple in target_ingredients_cleaned:
                ingredient_name = ingredient_tuple[0]
                if ingredient_name not in items:
                    item_data = find_item(ingredient_name, expected_item_categories)
                    if item_data is None:
                        raise ValueError(f"Could not find data for {ingredient_name}")
                    else:
                        items[ingredient_name] = item_data
                target_ingredients_cooked[ingredient_name] = int(ingredient_tuple[1])

            for product_tuple in target_products_cleaned:
                product_name = product_tuple[0]
                if product_name not in items:
                    item_data = find_item(product_name, expected_item_categories)
                    if item_data is None:
                        raise ValueError(f"Could not find data for {product_name}")
                    else:
                        items[product_name] = item_data
                target_products_cooked[product_name] = int(product_tuple[1])

            buildings_list = target_recipe["mProducedIn"]
            buildings_list_parsed = re.findall(r".+?Factory/(\w+)/Build", buildings_list)
            if "AutomatedWorkBench" in buildings_list_parsed:
                buildings_list_parsed.remove("AutomatedWorkBench")
            if len(buildings_list_parsed) > 1:
                raise ValueError(
                    f"Unexpected production building data for {target_recipe['ClassName']}:\n{buildings_list}\n{buildings_list_parsed}"
                )
            if len(buildings_list_parsed) == 0:
                continue

            recipes[target_recipe["ClassName"]] = Recipe(
                recipe_name=target_recipe["ClassName"],
                display_name=target_recipe["mDisplayName"],
                ingredients=target_ingredients_cooked,
                products=target_products_cooked,
                produced_in=buildings_list_parsed[0],
                recipe_time=float(target_recipe["mManufactoringDuration"])/60, # convert seconds to minutes

                variable_power=VariablePower(
                    constant=float(target_recipe["mVariablePowerConsumptionConstant"]),
                    factor=float(target_recipe["mVariablePowerConsumptionFactor"]),
                ),
                alternate="AlternateRecipes" in target_recipe["FullName"],
            )

    with open(file='data/items.json', mode='w', encoding='utf-8') as items_file:
        json.dump(items, items_file, ensure_ascii=False, default=serializablize, indent=4, sort_keys=True)

    with open(file='data/recipes.json', mode='w', encoding='utf-8') as recipes_file:
        json.dump(recipes, recipes_file, ensure_ascii=False, default=serializablize, indent=4, sort_keys=True)

    # with open(file='data/buildings.json', mode='w', encoding='utf-8') as buildings_file:
    #     json.dump(production_buildings, buildings_file, ensure_ascii=False, default=serializablize)

    return (items, recipes)

def serializablize(dump_target):
    if is_dataclass(dump_target) and not isinstance(dump_target, type):
        return asdict(dump_target)
    if isinstance(dump_target, Enum):
        return dump_target.value
    raise TypeError(f"{type(dump_target)} is not serializable nor handled by serializablize()")

if __name__ == "__main__":

    # If building from source, point this filepath at
    # CommunityResources/Docs/en-us.JSON, or
    # move that file to the (gitignored) location indicated here.
    docs_path_hard = "data/raw/en-US.json"
    parse_game_data(docs_path=docs_path_hard)
