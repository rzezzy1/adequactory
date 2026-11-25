import pulp

from engine.models import FactoryResult, Form
from engine.recipe_parser import items, recipes

###############################################################################################
# Will eventually be replaced by user input
# if __name__ == "__main__":
#     final_product_name = 'Desc_ModularFrameHeavy_C'
###############################################################################################

def solve_factory(final_product_name: str, input_resources: dict[str, float], veto_list: list[str]) -> FactoryResult:
    final_product = items[final_product_name]

    # Will eventually read a save file to determine what recipes are available
    # available_recipes = recipes

    # Pre-loop:
    # # take target item,
    # # loop through all recipes,
    # # make a set of all recipes that list it as a product,
    # # add those recipes' ingredients and products to lists,
    # # de-duplicate those lists
    relevant_recipes = set()
    all_ingredients = []
    all_products = []
    missing_products_count = 0

    target_item = final_product
    for consider_recipe in recipes.values():
        if consider_recipe.products == []:
            missing_products_count+=1
        for search_product in consider_recipe.products:
            if search_product == target_item.item_name:
                relevant_recipes.add(consider_recipe.recipe_name)
                for add_ingredient in consider_recipe.ingredients:
                    if add_ingredient not in all_ingredients:
                        all_ingredients.append(add_ingredient)
                for add_product in consider_recipe.products:
                    if add_product not in all_products:
                        all_products.append(add_product)

    ingredient_iterator = 0
    while ingredient_iterator < len(all_ingredients):
        target_item = items[all_ingredients[ingredient_iterator]]
        # print(f'Looking for recipes for {target_item}')
        for consider_recipe in recipes.values():
            if consider_recipe.products == []:
                missing_products_count+=1
            for search_product in consider_recipe.products:
                if search_product == target_item.item_name:
                    # print(f'{target_item.item_name} found in {consider_recipe.display_name}')
                    relevant_recipes.add(consider_recipe.recipe_name)
                    for add_ingredient in consider_recipe.ingredients:
                        if add_ingredient not in all_ingredients:
                            all_ingredients.append(add_ingredient)
                    for add_product in consider_recipe.products:
                        if add_product not in all_products:
                            all_products.append(add_product)
        ingredient_iterator+=1

    # print(relevant_recipes)
    # print(all_ingredients)

    relevant_items = list(set(all_ingredients).union(set(all_products)))
    # raw_inputs = list(set(all_ingredients) - set(all_products))
    # byproducts = list(set(all_products) - set(all_ingredients) - set(final_product_name))

    ###############################################################################################
    # MANUAL RECIPE REMOVAL
    # TODO: REMOVE THIS
    # relevant_recipes.discard("Recipe_Alternate_IngotIron_C")
    # relevant_recipes.discard("Recipe_Diamond_C")
    ###############################################################################################
    for recipe_name in veto_list:
        relevant_recipes.discard(recipe_name)

    recipe_vars = {
        recipe_name: pulp.LpVariable(recipe_name, lowBound=0)
        for recipe_name in relevant_recipes
    }

    def production_coefficient(item_name: str, recipe_name: str) -> float:
        coeff = (
        recipes[recipe_name].products.get(item_name, 0)/recipes[recipe_name].recipe_time
        - recipes[recipe_name].ingredients.get(item_name, 0)/recipes[recipe_name].recipe_time
        )
        return coeff

    resource_availability = dict.fromkeys(relevant_items, 0.0)

    ###############################################################################################
    # TODO: REPLACE WITH USER INPUT IN ITEMS PER MINUTE
    # WHILE ENTERING MANUALLY, MULTIPLY LIQUIDS BY 1000
    # if __name__ == "__main__":
    #     resource_availability["Desc_OreIron_C"] = -480*6
    #     resource_availability["Desc_Stone_C"] = -480*4
    #     resource_availability["Desc_Water_C"] = -300*6*1000
    #     resource_availability["Desc_OreCopper_C"] = -480
    #     resource_availability["Desc_OreGold_C"] = -480
    #     resource_availability["Desc_Coal_C"] = -480*4
    ###############################################################################################
    for class_name, quantity in input_resources.items():
        if items[class_name].form != Form.SOLID:
            volume_multiplier = 1000
        else:
            volume_multiplier = 1
        resource_availability[class_name] = -volume_multiplier*quantity
    factory_model = pulp.LpProblem("Maximize target item production", pulp.LpMaximize)

    for item in relevant_items:
        lhs = pulp.lpSum([production_coefficient(item_name=item, recipe_name=recipe) * recipe_vars[recipe] for recipe in relevant_recipes])
        factory_model += pulp.LpConstraint(
            e = lhs,
            sense = pulp.LpConstraintGE,
            name = item,
            rhs = resource_availability[item]
        )

        is_not_sinkable = not items[item].can_be_discarded
        is_fluid = items[item].form != Form.SOLID
        is_not_burnable = items[item].energy_value == 0

        if ((is_not_sinkable or is_fluid) and is_not_burnable):
            factory_model += pulp.LpConstraint(
                e = lhs,
                sense = pulp.LpConstraintLE,
                name = item + "_byproduct",
                rhs = 0
            )

        if item == final_product_name:
            factory_model += lhs

    factory_model.solve()
    # print(pulp.LpStatus[factory_model.status])

    return_status = pulp.LpStatus[factory_model.status]
    if return_status != "Optimal":
        return FactoryResult(return_status, None, None)

    return_recipe_rates: dict[str, float] | None = {}

    for recipe in relevant_recipes:
        solution = recipe_vars[recipe].varValue
        if solution is None:
            raise ValueError("Found None recipe rate even though optimal solution was found")
        elif solution > 10**-6:
            print(f'{recipes[recipe].display_name}: {solution}')
            return_recipe_rates[recipe] = solution


    return_output_rate = pulp.value(factory_model.objective)
    if not isinstance(return_output_rate, float):
        raise TypeError("Found None product rate even though optimal solution was found")


    return FactoryResult(status=return_status, output_rate=float(return_output_rate), recipe_rates=return_recipe_rates)

if __name__ == "__main__":
    final_product_name_hard = 'Desc_ModularFrameHeavy_C'
    input_resources_hard = {"Desc_OreIron_C": 480.0*6,
                            "Desc_Stone_C": 480.0*4,
                            "Desc_Water_C": 300.0*6,
                            "Desc_OreCopper_C": 480.0,
                            "Desc_OreGold_C": 480.0,
                            "Desc_Coal_C": 480.0*4}
    veto_list_hard = ["Recipe_Alternate_IngotIron_C", "Recipe_Diamond_C"]
    solve_factory(final_product_name_hard, input_resources_hard, veto_list_hard)
