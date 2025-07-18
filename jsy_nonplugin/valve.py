from pydantic import BaseModel, field_validator, model_validator
from typing import Literal


class JSY_NONPLUGIN_VALVE_MODEL(BaseModel):
    prefix: Literal['JSY']
    series: Literal['1', '3', '5']
    actuation: Literal['1', '2', '3', '4', '5', 'A', 'B', 'C']
    static: Literal['40']
    coil_specs: Literal['', 'T'] = ''
    static2: Literal['5']
    elec_entry: Literal['L', 'LO', 'M', 'MO', 'D', 'Y', 'DO', 'YO', 'W', 'WO', 'WA', 'WAO', 'K', 'KO']
    light_surge: Literal['Z', 'S']
    manual_override: Literal['', 'D', 'E'] = ''

    @model_validator(mode='after')
    def check_conditions(self) -> 'JSY_NONPLUGIN_VALVE_MODEL':
        if self.series == '1' and self.coil_specs != 'T':
            raise ValueError("JSY1000 must have power saving circuit, T")
        if self.series == '1' and self.elec_entry in ('D', 'Y', 'DO', 'YO', 'W', 'WO', 'WA', 'WAO', 'K', 'KO'):
            raise ValueError("JSY1000 not compatible with selected electrical entry")
        if self.elec_entry in ('L', 'M', 'W', 'WA', 'K') and self.light_surge != 'Z':
            raise ValueError("Light/Surge Voltage Suppressor not compatible with Electrical Entry")
        if self.elec_entry in ('D', 'Y') and self.light_surge not in ('S', 'Z'):
            raise ValueError("Light/Surge Voltage Suppressor not compatible with Electrical Entry")    
        if self.elec_entry in ('DO', 'YO') and self.light_surge == 'Z':
            raise ValueError("Light/Surge Voltage Suppressor not compatible with Electrical Entry")             
        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}{self.actuation}{self.static}{self.coil_specs}"
            f"-{self.static2}{self.elec_entry}{self.light_surge}{self.manual_override}"
        )

    def description(self) -> str:
        return (
            f"JSY{self.series}000 NON PLUGIN VALVE"
        )

NONPLUGIN_VALVE_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"JSY", "length": 3},
    {"name": "series", "pattern": r"[135]", "length": 1},
    {"name": "actuation", "pattern": r"[1-5A-C]", "length": 1},
    {"name": "static", "pattern": r"40", "length": 2},
    {"name": "coil_specs", "pattern": r"[T]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "static2", "pattern": r"5", "length": 1},
    {"name": "elec_entry", "pattern": r"(LO|L|MO|M|DO|D|YO|Y|WO|W|WAO|WA|KO|K)", "length": None},
    {"name": "light_surge", "pattern": r"(Z|S){1}", "length": None},
    {"name": "manual_override", "pattern": r"[DE]?", "length": 1}
]
