from pulp.pulp import LpVariable

from engine.recipe_parser import items, recipes
import pulp

# Will eventually be replaced by user input
final_product_name = 'Desc_IronPlate_C'
final_product = items[final_product_name]

# Will eventually read a save file to determine what recipes are available
available_recipes = recipes

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
    # print(f'{consider_recipe.display_name}')
    if consider_recipe.products == []:
        # print(f'{consider_recipe.display_name}\'s products are missing')
        missing_products_count+=1
    for search_product in consider_recipe.products:
        # if "Plate" in consider_recipe.display_name:
            # print(f'{consider_recipe.display_name} has \"Plate\" in its name')
        if search_product.item_name == target_item.item_name:
            # print(f'{consider_recipe.display_name} has been found to produce {target_item.item_name}! Adding to recipe set.')
            relevant_recipes.add(consider_recipe.recipe_name)
            for add_ingredient in consider_recipe.ingredients:
                if add_ingredient.item_name not in all_ingredients:
                    all_ingredients.append(add_ingredient.item_name)
            for add_product in consider_recipe.products:
                if add_product.item_name not in all_products:
                    all_products.append(add_product.item_name)

ingredient_iterator = 0
while ingredient_iterator < len(all_ingredients):
    target_item = items[all_ingredients[ingredient_iterator]]
    # print(f'Finding how to produce {target_item.display_name}...')
    # print(f'{ingredient_iterator}/{len(all_ingredients)}')
    for consider_recipe in recipes.values():
        # print(f'{consider_recipe.display_name}')
        if consider_recipe.products == []:
            # print(f'{consider_recipe.display_name}\'s products are missing')
            missing_products_count+=1
        for search_product in consider_recipe.products:
            # if "Plate" in consider_recipe.display_name:
            #    # print(f'{consider_recipe.display_name} has \"Plate\" in its name')
            #    # print(f'{search_product.item_name}')
            if search_product.item_name == target_item.item_name:
                # print(f'{consider_recipe.display_name} has been found to produce {target_item.item_name}! Adding to recipe set.')
                relevant_recipes.add(consider_recipe.recipe_name)
                for add_ingredient in consider_recipe.ingredients:
                    if add_ingredient.item_name not in all_ingredients:
                        all_ingredients.append(add_ingredient.item_name)
                        # print(f'{consider_recipe.recipe_name} added {add_ingredient.item_object.item_name}')
                        # print(len(all_ingredients))
                for add_product in consider_recipe.products:
                    if add_product.item_name not in all_products:
                        all_products.append(add_product.item_name)
    ingredient_iterator+=1

relevant_items = list(set(all_ingredients).union(set(all_products)))
raw_inputs = list(set(all_ingredients) - set(all_products))
byproducts = list(set(all_products) - set(all_ingredients) - set(final_product_name))

recipe_vars = {
    recipe_name: LpVariable(recipe_name, lowBound=0)
    for recipe_name in relevant_recipes
}

# def production_coefficient(item_name: str, recipe_name: str) -> float:
#     coeff = 0


#     return coeff
