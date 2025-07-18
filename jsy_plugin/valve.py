from pydantic import BaseModel, field_validator, model_validator
from typing import Literal


class JSY_PLUGIN_VALVE_MODEL(BaseModel):
    prefix: Literal['JSY']
    series: Literal['1', '3', '5']
    actuation: Literal['1', '2', '3', '4', '5', 'A', 'B', 'C']
    static: Literal['00']
    coil_specs: Literal['', 'T'] = ''
    static2: Literal['5']
    manual_override: Literal['', 'D', 'E'] = ''
    light_surge: Literal['U', 'Z', 'NZ']

    @model_validator(mode='after')
    def check_conditions(self) -> 'JSY_PLUGIN_VALVE_MODEL':
        if self.light_surge == 'U' and self.series != '1':
            raise ValueError("JSY1000 not applicable with U light surge suppressor")
        if self.coil_specs == 'T' and self.light_surge not in ('Z', 'NZ'):
            raise ValueError("Only 'Z' and 'NZ' light surge available with power saving circuit, T")
        if self.series == '1' and self.coil_specs == '':
            raise ValueError("JSY1000 not available without power saving circuit, T")
        if self.series == '1' and self.manual_override == 'E':
            raise ValueError("JSY1000 not available with push-turn locking lever type")
        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}{self.actuation}{self.static}{self.coil_specs}"
            f"-{self.static2}{self.light_surge}{self.manual_override}"
        )

    def description(self) -> str:
        return (
            f"JSY{self.series}000 PLUGIN VALVE"
        )

PLUGIN_VALVE_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"JSY", "length": 3},
    {"name": "series", "pattern": r"[135]", "length": 1},
    {"name": "actuation", "pattern": r"[1-5A-C]", "length": 1},
    {"name": "static", "pattern": r"00", "length": 2},
    {"name": "coil_specs", "pattern": r"[T]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "static2", "pattern": r"5", "length": 1},
    {"name": "light_surge", "pattern": r"[U|Z|NZ]{1,2}", "length": None},
    {"name": "manual_override", "pattern": r"[DE]?", "length": 1}
]
