import sys

from PySide6 import QtCore, QtWidgets

from engine.data_store import recipes
from engine.models import FactoryResult, Item, Recipe
from engine.recipe_parser import items
from engine.solver import solve_factory


class ResourceRow(QtWidgets.QWidget):
    def __init__(self, items_dict: dict[str, Item]):
        super().__init__()

        self.game_items = items_dict

        self.main_layout = QtWidgets.QHBoxLayout(self)

        self.resource_selector = QtWidgets.QComboBox()
        self.resource_selector.setEditable(True)
        for add_item in sorted(self.game_items.values(),
                                key=lambda game_item: game_item.display_name):
            self.resource_selector.addItem(add_item.display_name, add_item.item_name)
        self.resource_selector.setCurrentIndex(-1)
        self.resource_selector.setPlaceholderText("Select Item...")
        self.main_layout.addWidget(self.resource_selector)

        self.resource_quantity = QtWidgets.QDoubleSpinBox()
        self.resource_quantity.setRange(0,1e6)
        self.resource_quantity.setSuffix("/min")
        self.resource_quantity.setDecimals(5)
        self.main_layout.addWidget(self.resource_quantity)

        self.remove_row_button = QtWidgets.QPushButton("-")
        self.main_layout.addWidget(self.remove_row_button)
        self.remove_row_button.clicked.connect(self.request_removal)

    removal_requested = QtCore.Signal(QtWidgets.QWidget)

    def params(self) -> tuple[str, float] | None:
        if self.resource_selector.currentData() is None:
            return None
        else:
            return (self.resource_selector.currentData(), self.resource_quantity.value())

    @QtCore.Slot()
    def request_removal(self):
        self.removal_requested.emit(self)

class ResourceList(QtWidgets.QWidget):
    def __init__(self, items_dict: dict[str, Item]):
        super().__init__()
        self.game_items = items_dict

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.rows_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.rows_layout)

        self.rows: list[ResourceRow] = []

        self.add_row_button = QtWidgets.QPushButton("Add Available Resource")
        self.main_layout.addWidget(self.add_row_button)

        self.add_row_button.clicked.connect(self.add_row)

        self.add_row()

    @QtCore.Slot()
    def add_row(self):
        new_row = ResourceRow(items_dict=self.game_items)
        self.rows.append(new_row)
        self.rows_layout.addWidget(new_row)
        new_row.removal_requested.connect(self.remove_row)

    @QtCore.Slot(QtWidgets.QWidget)
    def remove_row(self, row: ResourceRow):
        self.rows.remove(row)
        self.rows_layout.removeWidget(row)
        row.deleteLater()

    def get_resources(self):
        resources = {}
        for row in self.rows:
            temp_params = row.params()
            if temp_params is None:
                continue
            class_name, quantity = temp_params
            resources[class_name] = quantity
        return resources

class RecipeRow(QtWidgets.QWidget):
    def __init__(self, game_recipe: Recipe, recipe_rate: float):
        super().__init__()

        self.main_layout = QtWidgets.QHBoxLayout(self)

        self.recipe_name = QtWidgets.QLabel(game_recipe.display_name)
        self.main_layout.addWidget(self.recipe_name)

        self.recipe_rate_label = QtWidgets.QLabel(str(recipe_rate))
        self.main_layout.addWidget(self.recipe_rate_label)

        self.veto_recipe_button = QtWidgets.QPushButton("X")
        self.main_layout.addWidget(self.veto_recipe_button)

class RecipeList(QtWidgets.QWidget):
    def __init__(self, recipes_dict: dict[str, Recipe]):
        super().__init__()

        self.game_recipes = recipes_dict

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.status_label = QtWidgets.QLabel("Waiting for calculation")
        self.main_layout.addWidget(self.status_label)

        self.rows: list[RecipeRow] = []

    @QtCore.Slot()
    def show_results(self, factory_result:FactoryResult, recipes_dict: dict[str, Recipe]):
        for row in self.rows:
            self.rows.remove(row)
            self.main_layout.removeWidget(row)
            row.deleteLater()

        if factory_result.status != "Optimal":
            self.status_label.setText("Calculation failed")
        else:
            if factory_result.recipe_rates is None:
                raise TypeError("Calculation returned optimal but recipe_rates is None")
            else:
                self.status_label.setText(factory_result.status)
            for recipe_name, recipe_rate in factory_result.recipe_rates.items():
                self.add_row(recipe_name, recipe_rate, recipes_dict)

    def add_row(self, recipe_name: str, recipe_rate: float, recipes_dict: dict[str, Recipe]):
        new_row = RecipeRow(recipes_dict[recipe_name], recipe_rate)
        self.rows.append(new_row)
        self.main_layout.addWidget(new_row)

class VetoedRecipe(QtWidgets.QWidget):
    def __init__(self, recipes_dict: dict[str, Recipe], recipe_name: str):
        super().__init__()

        self.game_recipes = recipes_dict

        self.main_layout = QtWidgets.QHBoxLayout(self)

        self.recipe_name_label = QtWidgets.QLabel(self.game_recipes[recipe_name].display_name)
        self.main_layout.addWidget(self.recipe_name_label)

        self.unveto_button = QtWidgets.QPushButton("✔")
        self.main_layout.addWidget(self.unveto_button)

class VetoList(QtWidgets.QWidget):
    def __init__(self, recipes_dict: dict[str, Recipe]):
        super().__init__()

        self.game_recipes = recipes_dict

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.section_title = QtWidgets.QLabel("Struck Recipes")
        self.main_layout.addWidget(self.section_title)

        self.rows: list[Recipe] = []

class AdequactoryGui(QtWidgets.QWidget):
    def __init__(self, items_dict: dict[str, Item]):
        super().__init__()

        self.game_items = items_dict

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.column_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.column_layout)

        self.column1 = QtWidgets.QGroupBox()
        self.column_layout.addWidget(self.column1)
        self.column1.setTitle("Calculation inputs")
        self.column1_layout = QtWidgets.QVBoxLayout(self.column1)

        self.target_selector = QtWidgets.QComboBox()
        self.target_selector.setEditable(True)
        for add_item in sorted(self.game_items.values(),
                                key=lambda game_item: game_item.display_name):
            self.target_selector.addItem(add_item.display_name, add_item.item_name)

        self.target_label = QtWidgets.QLabel("Select Target Product")
        self.column1_layout.addWidget(self.target_label)
        self.column1_layout.addWidget(self.target_selector)

        self.resources_label = QtWidgets.QLabel("Input Available Resources")
        self.column1_layout.addWidget(self.resources_label)

        self.resource_list = ResourceList(items_dict=self.game_items)
        self.column1_layout.addWidget(self.resource_list)

        self.column2 = QtWidgets.QGroupBox()
        self.column_layout.addWidget(self.column2)
        self.column2.setTitle("Results")
        self.column2_layout = QtWidgets.QVBoxLayout(self.column2)

        self.recipes_list = RecipeList(recipes)
        self.column2_layout.addWidget(self.recipes_list)

        self.calculate_button = QtWidgets.QPushButton("Calculate")
        self.main_layout.addWidget(self.calculate_button)
        self.calculate_button.clicked.connect(self.calculate)

    @QtCore.Slot()
    def calculate(self):
        # print(self.resource_list.get_resources())
        target_item = self.target_selector.currentData()
        input_resources = self.resource_list.get_resources()
        solver_results = solve_factory(target_item, input_resources)
        print("SOLVER FUNCTION OUTPUT BELOW")
        print(solver_results)
        self.recipes_list.show_results(solver_results, recipes)


    # @QtCore.Slot(str)
    # def veto_recipe(self, recipe_name: str):



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = AdequactoryGui(items)
    # widget.resize(800,600)
    widget.show()

    sys.exit(app.exec())
