from dataclasses import dataclass  # , Field
from enum import Enum


class Form(Enum):
    SOLID = "RF_SOLID"
    LIQUID = "RF_LIQUID"
    GAS = "RF_GAS"


class StackSize(Enum):
    SS_ONE = 1
    SS_SMALL = 50
    SS_MEDIUM = 100
    SS_BIG = 200
    SS_HUGE = 500
    SS_FLUID = 50000


# # TODO: add buildings not found in NativeClass BuildableManufacturer
class BuildableManufacturerName(Enum):
    CONSTRUCTOR = "ConstructorMk1"
    SMELTER = "SmelterMk1"
    FOUNDRY = "FoundryMk1"
    REFINERY = "OilRefinery"
    PACKAGER = "Packager"
    MANUFACTURER = "ManufacturerMk1"
    ASSEMBLER = "AssemblerMk1"
    BLENDER = "Blender"
    ACCELERATOR = "HadronCollider"
    CONVERTER = "Converter"
    ENCODER = "QuantumEncoder"


# class TierList(Enum):
#     S = 0
#     A = 1
#     B = 2
#     C = 3
#     D = 4
#     F = 5


@dataclass
class Item:
    item_name: str
    display_name: str
    stack_size: StackSize
    can_be_discarded: bool = True
    resource_sink_points: int = 0
    energy_value: float = 0.0
    form: Form = Form.SOLID


@dataclass
class Ingredient:
    item_name: Item
    ingredient_amount: int


@dataclass
class VariablePower:
    constant: float = 0
    factor: float = 1


@dataclass
class BuildableManufacturer:
    building_name: BuildableManufacturerName
    display_name: str
    power_active: float
    input_belts: int
    output_belts: int
    max_somersloops: int
    input_pipes: int = 0
    output_pipes: int = 0
    is_unlocked: bool = True
    power_idle: float = 0.1
    variable_power: bool = False


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
