from pydantic import BaseModel, model_validator
from typing import Literal

# === Component Model for Part Numbering ===
# === Each callout will exist as a field with all possible options ===
# === prefixes and static symbols in pn can exists as fields too with one option ===
class SY_BODY_PORTED_VALVE_MODEL(BaseModel):
    prefix: Literal['SY']
    series: Literal['3', '5', '7', '9']
    actuation_type: Literal['1', '2', '3', '4', '5']
    static: Literal['20']
    coil_type: Literal['', 'T'] = ''
    rated_voltage: Literal['5', '6', 'V', 'S', 'R', '1', '2', '3', '4']
    electrical_entry: Literal['G', 'H', 'L', 'LN', 'LO', 'M', 'MN', 'MO', 'D', 'Y', 'DO', 'YO', 'WO', 'W']
    m8_connector_length: Literal['', 'A', '1', '2', '3', '4', '5', '6', '7'] # page 960 of catalog, only for 'W' type connector (M8)
    light_surge_voltage_suppressor: Literal['', 'S', 'Z', 'R', 'U'] = ''
    manual_override: Literal['', 'D', 'E'] = ''
    ab_port_size: Literal['M5', '01', '02', '03', 'C4', 'C6', 'C8', 'C10', 'C12', 'N3', 'N7', 'N9', 'N11']
    thread_type: Literal['', 'F', 'N', 'T'] = ''
    dynamic: Literal['', '-'] = '-'
    bracket: Literal['', 'F1', 'F2'] = ''
    dynamic2: Literal['', '-'] = '-'
    ce_ukca_compliant: Literal['', 'Q'] = ''

# === Model logical Statements, write conditions specified in How to Order here ===
    @model_validator(mode='after')
    def validate_conditions(self) -> 'SY_BODY_PORTED_VALVE_MODEL':
        # ----- Coil Specifications -----
        if self.electrical_entry in ('D', 'DO', 'Y', 'YO', 'W') and self.coil_type == 'T':
            raise ValueError("Selected electrical entry is not available with power saving circuit")
        
        # ----- Electrical Entry -----
        if self.electrical_entry in ('D', 'DO', 'Y', 'YO') and self.rated_voltage not in ('5', '6', '1', '2', '3', '4'):
            raise ValueError("Electrical entry and rated voltage are not compatible")
        if self.electrical_entry in ('WO', 'W') and self.rated_voltage not in ('5', '6', 'V', 'S', 'R'):
            raise ValueError("Electrical entry not compatible with AC voltage types")
        if self.electrical_entry != 'W' and self.m8_connector_length != '':
            raise ValueError('Cable length can only be specified if electrical entry is W')
        
        # ----- Light Surge Voltage Suppressor -----
        if self.rated_voltage in ('1', '2', '3', '4') and self.light_surge_voltage_suppressor == 'S':
            raise ValueError('AC voltage is not available with S type light surge voltage suppressor')
        if self.rated_voltage not in ('5', '6', 'V', 'S', 'R') and self.light_surge_voltage_suppressor in ('R', 'U'):
            raise ValueError('R and U light surge voltage suppressors are only available with DC voltage')
        if self.coil_type == 'T' and self.light_surge_voltage_suppressor != 'Z':
            raise ValueError('Power saving circuit, T, is only available with Z type light surge voltage suppressor')
        if self.electrical_entry in ('DO', 'YO') and self.light_surge_voltage_suppressor == 'Z':
            raise ValueError('DO and YO are not available with Z type light surge voltage suppressor')

        # ----- A, B Port Size -----
        if self.series == '3' and self.ab_port_size not in ('M5', 'C4', 'C6', 'N3', 'N7'):
            raise ValueError("3000 series not compatible with selected A, B port size")
        if self.series == '5' and self.ab_port_size not in ('01', 'C4', 'C6', 'C8', 'N3', 'N7', 'N9'):
            raise ValueError("5000 series not compatible with selected A, B port size")
        if self.series == '7' and self.ab_port_size not in ('02', 'C8', 'C10', 'N9', 'N11'):
            raise ValueError("7000 series not compatible with selected A, B port size")
        if self.series == '9' and self.ab_port_size not in ('02', '03', 'C8', 'C10', 'C12', 'N9', 'N11'):
            raise ValueError("9000 series not compatible with selected A, B port size")
        
        # ----- Thread Type -----
        if self.ab_port_size == 'M5' and self.thread_type != '':
            raise ValueError('Thread type cannot be selected if A, B port size is set to M5')
        
        # ----- Bracket -----
        if self.bracket == 'F1' and self.actuation_type != '2':
            raise ValueError('F1 bracket is only available for 2 position single actuation type')
        if self.bracket != '' and self.series == '9':
            raise ValueError('Bracket is not available for 9000 series')
        
        # ----- Dynamic Seperators -----
        if bool(self.bracket) != (self.dynamic == '-'): # xor logic: Flags true if conditon A and B are not the same --> in this case both must exist/no exist to work
            raise ValueError("Bracket and separator must be used together")
        
        if bool(self.ce_ukca_compliant) != (self.dynamic2 == '-'):
            raise ValueError('Extra seperator')

        return self
    
    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}{self.actuation_type}{self.static}{self.coil_type}"
            f"-{self.rated_voltage}{self.electrical_entry}{self.light_surge_voltage_suppressor}{self.manual_override}"
            f"-{self.ab_port_size}{self.thread_type}"
            f"{self.dynamic}{self.bracket}"
            f"{self.dynamic2}{self.ce_ukca_compliant}"
        )

    def description(self) -> str:
        return f"{self.prefix}{self.series}000 SERIES BODY PORTED VALVE"

# === Token Map with Regex Explanations ===
SY_BODY_PORTED_VALVE_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"SY", "length": 2},
    {"name": "series", "pattern": r"[3579]", "length": 1},
    {"name": "actuation_type", "pattern": r"[12345]", "length": 1},
    {"name": "static", "pattern": r"20", "length": 2},
    {"name": "coil_type", "pattern": r"[T]?", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "rated_voltage", "pattern": r"[123456VSR]", "length": 1},
    {"name": "electrical_entry", "pattern": r"(G|H|LO|LN|L|MO|MN|M|DO|YO|D|Y|WO|W)", "length": None},
    {"name": "m8_connector_length", "pattern": r"[1234567A]?", "length": None},
    {"name": "light_surge_voltage_suppressor", "pattern": r"[SZRU]?", "length": None},
    {"name": "manual_override", "pattern": r"[DE]?", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "ab_port_size", "pattern": r"(M5|01|02|03|C4|C6|C8|C10|C12|N3|N7|N9|N11)", "length": None},
    {"name": "thread_type", "pattern": r"[FNT]?", "length": None},
    {"name": "dynamic", "pattern": r"[-]?", "length": None},

    {"name": "bracket", "pattern": r"(F1|F2)?", "length": None},
    {"name": "dynamic2", "pattern": r"[-]?", "length": None},

    {"name": "ce_ukca_compliant", "pattern": r"[Q]?", "length": None}
]