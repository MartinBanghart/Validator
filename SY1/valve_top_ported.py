from pydantic import BaseModel, model_validator
from typing import Literal

# === Component Model for Part Numbering ===
# === Each callout will exist as a field with all possible options ===
# === prefixes and static symbols in pn can exists as fields too with one option ===
class SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL(BaseModel):
    prefix: Literal['SY']
    series: Literal['3', '5', '7']
    actuation_type: Literal['1', '2', '3', '4', '5', 'A', 'B', 'C']
    static: Literal['3']
    seal_type: Literal['0', '1']
    pilot_type: Literal['', 'R'] = ''
    back_pressure_check_valve: Literal['', 'H']
    pilot_valve: Literal['', 'B', 'K'] = ''
    coil_type: Literal['', 'T'] = ''
    rated_voltage: Literal['5', '6']
    light_surge_voltage_suppressor: Literal['', 'R', 'U', 'S', 'Z', 'NS', 'NZ']
    manual_override: Literal['', 'D', 'E', 'F']
    static2: Literal['1']
    mounting_screw: Literal['', 'B', 'K', 'H']

# === Model logical Statements, write conditions specified in How to Order here ===
    @model_validator(mode='after')
    def validate_conditions(self) -> 'SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL':
        if self.actuation_type in ('A', 'B', 'C') and self.seal_type != '0':
            raise ValueError("4 position dual 3-port valve only available with rubber seal type")
        if self.back_pressure_check_valve == 'H' and self.seal_type != '0':
            raise ValueError("Back pressure check valve only available for rubber seal type")
        if self.back_pressure_check_valve == 'H' and self.actuation_type in ('3', '4', '5'):
            raise ValueError("Back pressure valve is not availabe for 3 position type valves")
        if self.back_pressure_check_valve == 'H' and self.series == '7':
            raise ValueError('Back pressure check valve is not availabe for SY7000')
        if self.pilot_valve == 'K' and self.seal_type != '1':
            raise ValueError('The high pressure pilot valve type is only available with metal seal type')
        if self.light_surge_voltage_suppressor not in ('Z', 'NZ') and self.coil_type == 'T':
            raise ValueError('Only Z and NZ light surge voltage suppressors are available with power saving circuit')

        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}{self.actuation_type}{self.static}{self.seal_type}{self.pilot_type}{self.back_pressure_check_valve}{self.pilot_valve}{self.coil_type}"
            f"-{self.rated_voltage}{self.light_surge_voltage_suppressor}{self.manual_override}{self.static2}"
            f"-"
            f"-{self.mounting_screw}" 
        )

    def description(self) -> str:
        return f"{self.prefix}{self.series}000 SERIES BASE MOUNTED PLUG IN VALVE"

# === Token Map with Regex Explanations ===
SY1_BASE_MOUNTED_PLUGIN_VALVE_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"SY", "length": 2},
    {"name": "series", "pattern": r"[357]", "length": 1},
    {"name": "actuation_type", "pattern": r"[ABC12345]", "length": 1},
    {"name": "static", "pattern": r"[3]", "length": 1},
    {"name": "seal_type", "pattern": r"[01]", "length": 1},
    {"name": "pilot_type", "pattern": r"[R]?", "length": None},
    {"name": "back_pressure_check_valve", "pattern": r"[H]?", "length": None},
    {"name": "pilot_valve", "pattern": r"[BK]?", "length": None},
    {"name": "coil_type", "pattern": r"[T]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "rated_voltage", "pattern": r"[56]", "length": 1},
    {"name": "light_surge_voltage_suppressor", "pattern": r"(NZ|NS|Z|S|U|R)?", "length": None},
    {"name": "manual_override", "pattern": r"[DEF]?", "length": None},
    {"name": "static2", "pattern": r"1", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "mounting_screw", "pattern": r"[BKH]?", "length": None}
]