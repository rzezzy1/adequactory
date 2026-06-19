from dataclasses import Field, dataclass
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


@dataclass
class Item:
    item_name: str
    display_name: str
    stack_size: StackSize
    can_be_discarded: bool = True
    resource_sink_points: int = 0
    energy_value: float = 0.0
    form: Form = Form.RF_SOLID
