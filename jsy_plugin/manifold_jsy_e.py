from pydantic import BaseModel, PrivateAttr, model_validator, ValidationError, Field
from typing import Literal
from typing import Annotated

# Input for Parser
JJ5SY_PLUGIN_EJECTOR_MANIFOLD_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"JJ5SY", "length": 5},
    {"name": "series", "pattern": r"[1]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "type", "pattern": r"E10", "length": 3},
    {"name": "ex", "pattern": r"S", "length": 1},
    {"name": "si_unit", "pattern": r"(EN|DN|FN|KN|0)", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "valve_stations", "pattern": r"(02|03|04|05|06|07|08|09|10|11|12)", "length": 2},
    {"name": "p_e_port_entry", "pattern": r"[UDB]", "length": 1},
    {"name": "sup_exh_block_assy", "pattern": r"[S]?", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "pressure_sensors", "pattern": r'[12345]', "length": 1},
    {"name": "pilot_air_control", "pattern": r'(AX|A|BX|B|X)', "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    
    {"name": "a_b_port_size", "pattern": r'(C2|C4|C6)', "length": None},
    {"name": "mounting", "pattern": r"[D]?", "length": None, "optional": True},
    {"name": "din_rail_opt", "pattern": r'(0|[3-9]|1[0-9]|2[0-4])?', "length": None, "optional": True},
]

class JJ5SY_PLUGIN_EJECTOR_MANIFOLD_MODEL(BaseModel):
    # How to Order Information
    prefix: Literal['JJ5SY']
    series: Literal['1']
    
    type: Literal['E10']
    ex: Literal['S']
    si_unit: Literal['0', 'EN', 'DN', 'FN', 'KN']
    
    valve_stations: Literal['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    p_e_port_entry: Literal['U', 'D', 'B']
    sup_exh_block_assy: Literal['', 'S'] = ''
    
    pressure_sensors: Literal['1', '2', '3', '4', '5']
    pilot_air_control: Literal['AX', 'A', 'BX', 'B', 'X']
    
    a_b_port_size: Literal['C2', 'C4', 'C6']
    mounting: Literal['', 'D'] = ''
    din_rail_opt: Literal['', '0', '3', '4', '5', '6', '7', '8', '9', '10',
                            '11', '12', '13', '14', '15', '16', '17', '18',
                            '19', '20', '21', '22', '23', '24'] = ''

    @model_validator(mode='after')
    def check_conditions(self) -> 'JJ5SY_PLUGIN_EJECTOR_MANIFOLD_MODEL':
        # --- VARIABLES ---
        pressure_sensors_val = int(self.pressure_sensors)
        valve_stations_val = int(self.valve_stations)
        
        if pressure_sensors_val > valve_stations_val:
            raise ValueError('Too many pressure sensors for number of valve stations')
        
        if self.mounting in ('') and self.din_rail_opt not in (''):
            raise ValueError('Direct mounting selected, no din rail option necessary')
        if self.p_e_port_entry in ('U', 'D', 'C', 'E') and self.valve_stations in ('11', '12', '13', '14', '15', '16'):
            raise ValueError('P,E Port entry cannot support this many valve stations')
        if self.si_unit == '0' and self.mounting == 'D' and self.din_rail_opt != '0':
            raise ValueError('If no SI unit is selected and din rail is to be mounted, D0 must be selected option')
        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}"
            f"-{self.type}{self.ex}{self.si_unit}"
            f"-{self.valve_stations}{self.p_e_port_entry}{self.sup_exh_block_assy}"
            f"-{self.pressure_sensors}{self.pilot_air_control}"
            f"-{self.a_b_port_size}{self.mounting}{self.din_rail_opt}"
        )

    def description(self) -> str:
        return (
            f"JSY{self.series}000 {self.valve_stations} STA EJECTOR MANIFOLD"
        )