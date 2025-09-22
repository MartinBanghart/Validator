from pydantic import BaseModel, model_validator
from typing import Literal
from typing import Annotated

# INCORPORATES TERMINAL BLOCK BOX AND SPRING TYPE --- 2 models within (TYPE 10/11)
SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"SS5Y", "length": 4},
    {"name": "series", "pattern": r"[357]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "type", "pattern": r"(10|11)", "length": 2},
    {"name": "connector_type", "pattern": r"(TC|T)", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "valve_stations", "pattern": r"(0[2-9]|1[0-9]|2[0-4])", "length": 2},
    {"name": "p_e_port_entry", "pattern": r"[UDB]", "length": 1},
    {"name": "sup_exh", "pattern": r"[SR]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "a_b_port_size", "pattern": r'(?:C(?:2|3|4|6|8|10|12)|L(?:4|6|8|10|12)|B(?:4|6|8|10|12)|N(?:1|3|7|9|11)|LN(?:3|7|9|11)|BN(?:3|7|9|11))', "length": None},
    {"name": "mounting", "pattern": r"(AA|BA|D|A|B)?", "length": None},
    {"name": "din_rail_opt", "pattern": r'(0|[3-9]|1[0-9]|2[0-4])?', "length": None},
]

class SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL(BaseModel):
    # How to Order Information
    prefix: Literal['SS5Y']
    series: Literal['3', '5', '7']
    type: Literal['10', '11']
    connector_type: Literal['TC', 'T']
    valve_stations: Literal['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
                            '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    p_e_port_entry: Literal['U', 'D', 'B']
    sup_exh: Literal['', 'S', 'R'] = ''
    a_b_port_size: Literal['C2', 'C3', 'C4', 'C6', 'C8', 'C10', 'C12',
                            'L4', 'L6', 'L8', 'L10', 'L12',
                            'B4', 'B6', 'B8', 'B10', 'B12',
                            'N1', 'N3', 'N7', 'N9', 'N11',
                            'LN3', 'LN7', 'LN9', 'LN11',
                            'BN3', 'BN7', 'BN9', 'BN11']
    mounting: Literal['', 'AA', 'BA', 'D', 'A', 'B']
    din_rail_opt: Literal['', '0', '3', '4', '5', '6', '7', '8', '9', '10',
                            '11', '12', '13', '14', '15', '16', '17', '18',
                            '19', '20', '21', '22', '23', '24'] = ''

    @model_validator(mode='after')
    def check_conditions(self) -> 'SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL':
        errors = []
        
        # --- VARIABLES ---
        if self.din_rail_opt:
            din_rail_value = int(self.din_rail_opt)
        else:
            din_rail_value = 0
        valve_stations_value = int(self.valve_stations)

        # --- Valve Stations ---
        if valve_stations_value > 16 and self.connector_type == 'TC':
            errors.append("RFS required: Manifold must be single wired when there are more than 16 valve stations")
        if valve_stations_value > 10 and self.connector_type == 'T':
            errors.append("RFS required: Manifold must be single wired when there are more than 10 valve stations")
        
        # --- A, B Port Size Fittings ---
        if self.series == '3' and self.type == '10' and self.a_b_port_size not in ('C2', 'C3', 'C4', 'C6', 'L4', 'L6', 'B4', 'B6', 'N1', 'N3', 'N7', 'LN3', 'LN7', 'BN3', 'BN7'):
            errors.append("Side ported 3000 series not compatible with A,B Port Size Fittings")
        if self.series == '5' and self.type == '10' and self.a_b_port_size not in ('C4', 'C6', 'C8', 'L4', 'L6', 'L8', 'B4', 'B6', 'B8', 'N3', 'N7', 'N9', 'LN7', 'LN9', 'BN7', 'BN9'):
            errors.append("Side ported 5000 series not compatible with A,B port size fittings")
        if self.series == '7' and self.type == '10' and self.a_b_port_size not in ('C6', 'C8', 'C10', 'C12', 'L6', 'L8', 'L10', 'L12', 'B6', 'B8', 'B10', 'B12', 'N7', 'N9', 'N11', 'LN11', 'BN11'):
            errors.append("Side ported 7000 series not compatible with A,B port size fittings")
        if self.series == '3' and self.type == '11':
            errors.append("Type 11, 3000 series uses SY5000 manifold base - see 'Plug-in mixed mounting type manifold' section in catalog")
        if self.series == '5' and self.type == '11' and self.a_b_port_size not in ('C4', 'C6', 'C8', 'N3', 'N7', 'N9'):
            errors.append("Bottom ported 5000 series not compatible with A,B port size fittings")
        if self.series == '7' and self.type == '11' and self.a_b_port_size not in ('C6', 'C8', 'C10', 'C12', 'N7', 'N9', 'N11'):
            errors.append("Bottom ported 7000 series not compatible with A,B port size fittings")
        
        # --- Din Rail Mounting --
        if self.mounting not in ('D', 'A', 'B') and self.din_rail_opt != '':
            errors.append('Mounting option does not require din rail option - change mounting if din rail is necessary')
        if self.din_rail_opt != '':
            if din_rail_value != 0 and din_rail_value < valve_stations_value:
                errors.append('Din rail option must be equal to or greater than valve stations') 
        if din_rail_value > 20 and self.connector_type == "T":
            errors.append('Din rail option is too long for Terminal Block Box')       
            
        if errors:
            # single ValueError with newline-joined messages
            raise ValueError("\n".join(errors))
        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}"
            f"-{self.type}{self.connector_type}"
            f"-{self.valve_stations}{self.p_e_port_entry}{self.sup_exh}"
            f"-{self.a_b_port_size}{self.mounting}{self.din_rail_opt}"
        )

    def description(self) -> str:
        return (
            f"SY-1 {self.series}000 {self.valve_stations} STA TERMINAL BLOCK BOX (SPRING TYPE) MANIFOLD"
        )