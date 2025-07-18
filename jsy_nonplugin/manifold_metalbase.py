from pydantic import BaseModel, PrivateAttr, model_validator, Field
from typing import Literal
from typing import Annotated

# Input for Parser
JJ5SY_NONPLUGIN_MFLD_METALBASE_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"JJ5SY", "length": 5},
    {"name": "series", "pattern": r"[135]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "type", "pattern": r"(40|41)", "length": 2},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "valve_stations", "pattern": r"(02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20)", "length": 2},
    {"name": "p_e_port_entry", "pattern": r"[UDB]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "a_b_port_size", "pattern": r'(?:C(?:2|4|6|8|10|12)|KC(?:2|4|6|8|10|12)|M3|M5|01|02)', "length": None},
    {"name": "thread_type", "pattern": r"[FN]?", "length": None, "optional": True},
    {"name": "din_rail_opt", "pattern": r'(?:D(?:0|[3-9]|1[0-9]|2[0-4])?|D)?', "length": None, "optional": True},
]


class JJ5SY_NONPLUGIN_MFLD_METALBASE_MODEL(BaseModel):
    # How to Order Information
    prefix: Literal['JJ5SY']
    series: Literal['1', '3', '5']
    type: Literal['40', '41']
    valve_stations: Literal['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
    p_e_port_entry: Literal['U', 'D', 'B']
    a_b_port_size: Literal['M3', 'M5', '01', '02', 'C2', 'C4', 'C6', 'C8', 'C10', 'C12', 'KC2', 'KC4', 'KC6', 'KC8', 'KC10', 'KC12']
    thread_type: Literal['', 'F', 'N'] = ''
    din_rail_opt: Literal['', 'D', 'D0', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10',
                            'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18',
                            'D19', 'D20', 'D21', 'D22', 'D23', 'D24'] = ''

    @model_validator(mode='after')
    def check_conditions(self) -> 'JJ5SY_NONPLUGIN_MFLD_METALBASE_MODEL':
        if self.a_b_port_size not in ('M3', 'M5', 'C2', 'C4', 'KC2', 'KC4', 'KC6') and self.series == '1':
            raise ValueError('JSY1000 not compatible with selected A, B port size')
        if self.a_b_port_size not in ('M5', '01', 'C6', 'KC4', 'KC6', 'KC8') and self.series == '3':
            raise ValueError('JSY1000 not compatible with selected A, B port size')
        if self.a_b_port_size not in ('C8', 'KC6', 'KC8', 'KC10', 'KC12') and self.series == '5':
            raise ValueError('JSY1000 not compatible with selected A, B port size')
        if self.type == '41' and self.din_rail_opt != '':
            raise ValueError('Type 41 base can only have direct mounting option selected')
        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}"
            f"-{self.type}"
            f"-{self.valve_stations}{self.p_e_port_entry}"
            f"-{self.a_b_port_size}{self.thread_type}{self.din_rail_opt}"
        )
    
    def description(self) -> str:
        return (
            f"JSY{self.series}000 {self.valve_stations} STA METAL BASE MANIFOLD"
        )