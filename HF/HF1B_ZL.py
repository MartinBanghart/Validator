from pydantic import BaseModel, model_validator
from typing import Literal

# === Token Map with Regex Explanations ===
HF1B_ZL_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"HF1B-ZL", "length": 7},
    {"name": "suction_flow_rate", "pattern": r"[36]", "length": 1},
    {"name": "standard_supply_pressure", "pattern": r"[MH]", "length": 1},
    {"name": "vacuum_port_size_app_tubing", "pattern": r"(06|04|F06|F04)", "length": None},
    {"name": "exhaust_method", "pattern": r"[P]?", "length": None},
    {"name": "dynamic", "pattern": r"[-]?", "length": None},
    {"name": "vacuum_pressure_sensor", "pattern": r"(GN|G|E|F)?", "length": None},
    {"name": "vacuum_pressure_sensor_aux1", "pattern": r"[AB]?", "length": None},
    {"name": "vacuum_pressure_sensor_aux2", "pattern": r"[MP]?", "length": None},
    {"name": "vacuum_pressure_sensor_aux3", "pattern": r"[G]?", "length": None},
    {"name": "dynamic2", "pattern": r"[-]?", "length": None},
    {"name": "suction_flow_rate_aux1", "pattern": r"[P]?", "length": None},
]

# === Component Model for Part Numbering ===
class HF1B_ZL_MODEL(BaseModel):
    prefix: Literal['HF1B-ZL']
    suction_flow_rate: Literal['3', '6']
    standard_supply_pressure: Literal['M', 'H']
    vacuum_port_size_app_tubing: Literal['06', '04', 'F06', 'F04']
    exhaust_method: Literal['', 'P'] = ''
    dynamic: Literal['', '-'] = ''
    vacuum_pressure_sensor: Literal['', 'GN', 'G', 'E', 'F']
    vacuum_pressure_sensor_aux1: Literal['', 'A', 'B'] = ''
    vacuum_pressure_sensor_aux2: Literal['', 'M', 'P'] = ''
    vacuum_pressure_sensor_aux3: Literal['', 'G'] = ''
    dynamic2: Literal['', '-'] = ''
    suction_flow_rate_aux1: Literal['', 'P'] = ''

    @model_validator(mode='after')
    def validate_conditions(self) -> 'HF1B_ZL_MODEL':
        # Vacuum pressure sensor
        if self.vacuum_port_size_app_tubing in ("F06", "F04") and self.vacuum_pressure_sensor == "G":
            raise ValueError("Pressure gauge not available when F06 or F04 vacuum port size indicated")
        
        # Vacuum Pressure Sensory Auxillary options
        if self.vacuum_pressure_sensor not in ('E', 'F') and (self.vacuum_pressure_sensor_aux1 != '' or self.vacuum_pressure_sensor_aux2 != '' or self.vacuum_pressure_sensor_aux3 != ''):
            raise ValueError("Vacuum pressure auxillary options only available when vacuum pressure switch options are selected")
    
        # Suction Flow Rate Auxillary Option
        if self.suction_flow_rate_aux1 != '' and self.suction_flow_rate != '3':
            raise ValueError('Adapter assembly only available when suction flow rate option "3" is selected')
    
        # ----- Dynamic Seperators -----
        if (self.vacuum_pressure_sensor in ('E', 'F')) and (
            self.vacuum_pressure_sensor_aux1 != '' or
            self.vacuum_pressure_sensor_aux2 != '' or
            self.vacuum_pressure_sensor_aux3 != ''
        ) and self.dynamic != '-':
            raise ValueError('Dynamic separator "-" required when vacuum pressure auxillary options are present')

        if self.dynamic2 == '-' and self.suction_flow_rate_aux1 == '':
            raise ValueError('Dynamic separator "-" should not be present without adapter assembly')

        return self
    
    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.suction_flow_rate}{self.standard_supply_pressure}{self.vacuum_port_size_app_tubing}{self.exhaust_method}"
            f"{self.dynamic}{self.vacuum_pressure_sensor}{self.vacuum_pressure_sensor_aux1}{self.vacuum_pressure_sensor_aux2}{self.vacuum_pressure_sensor_aux3}"
            f"{self.dynamic2}{self.suction_flow_rate_aux1}"
        )

    def description(self) -> str:
        return f"{self.prefix}{self.suction_flow_rate} Series Multistage Ejector"
