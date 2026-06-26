from dataclasses import dataclass  # , Field
from enum import Enum


class Form(Enum):
    RF_SOLID = "RF_SOLID"
    RF_LIQUID = "RF_LIQUID"
    RF_GAS = "RF_GAS"


class StackSize(Enum):
    SS_ONE = 1
    SS_SMALL = 50
    SS_MEDIUM = 100
    SS_BIG = 200
    SS_HUGE = 500
    SS_FLUID = 50000


# # TODO: add buildings not found in NativeClass BuildableManufacturer
class BuildableManufacturer(Enum):
    BM_CONSTRUCTOR = "ConstructorMk1"
    BM_SMELTER = "SmelterMk1"
    BM_FOUNDRY = "FoundryMk1"
    BM_REFINERY = "OilRefinery"
    BM_PACKAGER = "Packager"
    BM_MANUFACTURER = "ManufacturerMk1"
    BM_ASSEMBLER = "AssemblerMk1"
    BM_BLENDER = "Blender"


class TierList(Enum):
    TL_S = 0
    TL_A = 1
    TL_B = 2
    TL_C = 3
    TL_D = 4
    TL_F = 5


@dataclass
class Item:
    item_name: str
    display_name: str
    stack_size: StackSize
    can_be_discarded: bool = True
    resource_sink_points: int = 0
    energy_value: float = 0.0
    form: Form = Form.RF_SOLID


@dataclass
class Ingredient:
    item_name: Item
    ingredient_amount: int


@dataclass
class VariablePower:
    constant: float = 0
    factor: float = 1


@dataclass
class Recipe:
    recipe_name: str
    display_name: str
    ingredients: list[Ingredient]
    products: list[Ingredient]
    produced_in: BuildableManufacturer
    recipe_time: float
    variable_power: VariablePower
    alternate: bool
    is_unlocked: bool = True
