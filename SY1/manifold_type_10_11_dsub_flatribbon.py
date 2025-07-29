from pydantic import BaseModel, field_validator, PrivateAttr, model_validator, ValidationError, Field
from typing import Literal
from typing import Annotated

SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"SS5Y", "length": 4},
    {"name": "series", "pattern": r"[357]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "type", "pattern": r"(10|11)", "length": 2},
    {"name": "connector_type", "pattern": r"(FW|F|PG|PH|P)", "length": None},
    {"name": "connector_entry_direction", "pattern": r"(1|2)", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "valve_stations", "pattern": r"(02|03|04|05|06|07|08|09|10|11|12|13|14|15|16)", "length": 2},
    {"name": "p_e_port_entry", "pattern": r"[UDB]", "length": 1},
    {"name": "sup_exh", "pattern": r"[SR]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "a_b_port_size", "pattern": r'(?:C(?:2|3|4|6|8|10|12)|L(?:4|6|8|10|12)|B(?:4|6|8|10|12)|N(?:1|3|7|9|11)|LN(?:3|7|9|11)|BN(?:3|7|9|11))', "length": None},
    {"name": "mounting", "pattern": r"(AA|BA|D|A|B)?", "length": None},
    {"name": "din_rail_opt", "pattern": r'(0|[3-9]|1[0-9]|2[0-4])?', "length": None},
]

class SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL(BaseModel):
    # How to Order Information
    prefix: Literal['SS5Y']
    series: Literal['3', '5', '7']
    type: Literal['10', '11']
    connector_type: Literal['F', 'FW', 'P', 'PG', 'PH']
    connector_entry_direction: Literal['1', '2']
    valve_stations: Literal['02', '03', '04', '05', '06', '07', '08', '09', 
                            '10', '11', '12', '13', '14', '15', '16']
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
    def check_conditions(self) -> 'SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL':
        # --- VARIABLES ---
        if self.din_rail_opt:
            din_rail_value = int(self.din_rail_opt)
        else:
            din_rail_value = 0
        valve_stations_value = int(self.valve_stations)

        # --- Connector Entry Direction ---
        if self.connector_entry_direction == '2' and self.connector_type == 'FW':
            raise ValueError('FW Connector type cannot be rotated')
        
        # --- Valve Stations ---
        if self.connector_type in ('F', 'FW', 'P') and valve_stations_value > 12:
            raise ValueError('Too many valve stations selected for connector type')
        if self.connector_type in ('PG') and valve_stations_value > 9:
            raise ValueError('Too many valve stations selected for connector type') 
        if self.connector_type in ('PH') and valve_stations_value > 4:
            raise ValueError('Too many valve stations selected for connector type')
        
        # --- A, B Port Size Fittings ---
        if self.series == '3' and self.type == '10' and self.a_b_port_size not in ('C2', 'C3', 'C4', 'C6', 'L4', 'L6', 'B4', 'B6', 'N1', 'N3', 'N7', 'LN3', 'LN7', 'BN3', 'BN7'):
            raise ValueError("Side ported 3000 series not compatible with A,B Port Size Fittings")
        if self.series == '5' and self.type == '10' and self.a_b_port_size not in ('C4', 'C6', 'C8', 'L4', 'L6', 'L8', 'B4', 'B6', 'B8', 'N3', 'N7', 'N9', 'LN7', 'LN9', 'BN7', 'BN9'):
            raise ValueError("Side ported 5000 series not compatible with A,B port size fittings")
        if self.series == '7' and self.type == '10' and self.a_b_port_size not in ('C6', 'C8', 'C10', 'C12', 'L6', 'L8', 'L10', 'L12', 'B6', 'B8', 'B10', 'B12', 'N7', 'N9', 'N11', 'LN11', 'BN11'):
            raise ValueError("Side ported 7000 series not compatible with A,B port size fittings")
        if self.series == '3' and self.type == '11':
            raise ValueError("Type 11, 3000 series uses SY5000 manifold base - see 'Plug-in mixed mounting type manifold' section in catalog")
        if self.series == '5' and self.type == '11' and self.a_b_port_size not in ('C4', 'C6', 'C8', 'N3', 'N7', 'N9'):
            raise ValueError("Bottom ported 5000 series not compatible with A,B port size fittings")
        if self.series == '7' and self.type == '11' and self.a_b_port_size not in ('C6', 'C8', 'C10', 'C12', 'N7', 'N9', 'N11'):
            raise ValueError("Bottom ported 7000 series not compatible with A,B port size fittings")
        
        # --- Din Rail Mounting --
        if self.mounting not in ('D', 'A', 'B') and self.din_rail_opt != '':
            raise ValueError('Mounting option does not require din rail option')
        if self.din_rail_opt != '':
            if din_rail_value != 0 and din_rail_value < valve_stations_value:
                raise ValueError('Din rail option must be equal to or greater than valve stations')

        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}"
            f"-{self.type}{self.connector_type}{self.connector_entry_direction}"
            f"-{self.valve_stations}{self.p_e_port_entry}{self.sup_exh}"
            f"-{self.a_b_port_size}{self.mounting}{self.din_rail_opt}"
        )

    def description(self) -> str:
        if self.connector_type in ('F', 'FW'):
            connector = 'D-Sub Connector'
        else:
            connector = 'Flat Ribbon Cable'

        return (
            f"SY-1 {self.series}000 {self.valve_stations} STA {connector} MANIFOLD"
        )
    
#     # ------------- BOM ----- BOM ----- BOM ----- BOM ----- BOM ----- BOM ----- BOM  ----- BOM ------------- 

#     # --- model_post_init is an option for actions taken after validation and cleaning by the base pydantic model (think "right after __init__ and validation but before return")
#     # -- this call all function designed to create and validate child components such as the manifold block and sup/exh blocks
#     def model_post_init(self, __context) -> None:
#         self._init_manifold_block()
#         self._init_sup_exh_block_d_side_dsub()
#         # self._init_sup_exh_block_d_side_flatribbon()
#         # self._init_sup_exh_block_u_side()
    
#     # ------------------------------------------- MANIFOLD BLOCK -------------------------------------------    
#     _manifold_block: 'SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL.Manifold_Block' = PrivateAttr()

#     @property
#     def manifold_block(self) -> 'SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL.Manifold_Block':
#         return self._manifold_block 
    
#     class Manifold_Block(BaseModel):
#         # SY[#]0M-2-[#][#]A-[#]
#         prefix: Literal['SY']
#         series: Literal['3', '5', '7'] 
#         static: Literal['0M']
#         static2: Literal['2']
#         block_pitch: Literal['1', '2']
#         wiring_type: Literal['S', 'D']
#         static3: Literal['A']
#         a_b_port_size: Literal['C2', 'C3', 'C4', 'C6', 'C8', 'C10', 'C12',
#                             'L4', 'L6', 'L8', 'L10', 'L12',
#                             'B4', 'B6', 'B8', 'B10', 'B12',
#                             'N1', 'N3', 'N7', 'N9', 'N11',
#                             'LN3', 'LN7', 'LN9', 'LN11',
#                             'BN3', 'BN7', 'BN9', 'BN11']

#         # --- Non part number related values ---
#         quantity: int = Field(..., ge=2, le=12)

#         def build_part_number(self) -> str:
#             return(
#                 f"{self.prefix}{self.series}{self.static}"
#                 f"-{self.static2}"
#                 f"-{self.block_pitch}{self.wiring_type}{self.static3}"
#                 f"-{self.a_b_port_size}"
#             )  

#     # Creates instance of fields inherited from top model into manifold block --> this will then be checked by pydantic model for the subcomponent
#     def _init_manifold_block(self) -> None:
#         # Logical Conditions
#         if self.type == '10':
#             block_pitch = '1'
#         elif self.type == '11':
#             block_pitch = '2'
        
#         self._manifold_block = self.Manifold_Block(
#             prefix = 'SY',
#             series = self.series,
#             static = '0M',
#             static2 = '2',
#             block_pitch = block_pitch,
#             wiring_type = 'D', # hard encoded but has option 'S' for double wire which would requrire RFS
#             static3 = 'A',
#             a_b_port_size = self.a_b_port_size,

#             # --- Non part number related values ---
#             quantity = int(self.valve_stations)
#         ) 

# # ------------------------------------------- SUP/EXH BLOCK (D-Side) DSUB -------------------------------------------    
#     _sup_exh_block_d_side_dsub: 'SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL.Sup_Exh_Block_D_Side_Dsub' = PrivateAttr()
    
#     @property
#     def sup_exh_block_d_side_dsub(self) -> 'SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL.Sup_Exh_Block_D_Side_Dsub':
#         return self._sup_exh_block_d_side_dsub    
    
#     class Sup_Exh_Block_D_Side_Dsub(BaseModel):
#         # D-Sub Connector (IP67) --- SY[#]0M-1-1A[#]-[#]-[#]
#         prefix: Literal['SY']
#         series: Literal['3', '5', '7'] 
#         static: Literal['0M']
#         static2: Literal['1']
#         static3: Literal['1A']
#         pilot_silencer_type: Literal['', 'S', 'R'] = '' # R is external pilot, this is made to order (Page 152)
#         a_b_port_size: Literal['C2', 'C3', 'C4', 'C6', 'C8', 'C10', 'C12']
#         mounting: Literal['', 'D0'] = '' # if any din_rail_opt is selected on manifold (ex. D0, D3, D17), this should be D0, else nil

#         # --- Non part number related values ---
#         quantity: int = 1
        
#         def build_part_number(self) -> str:
#             return(
#                 f"{self.prefix}{self.series}{self.static}"
#                 f"-{self.static2}"
#                 f"-{self.static3}{self.pilot_silencer_type}"
#                 f"-{self.a_b_port_size}"
#                 f"-{self.mounting}"
#             )


#     # Creates instance of fields inherited from top model into sup exh block d-side --> this will then be checked by pydantic model for the subcomponent
#     def _init_sup_exh_block_d_side_dsub(self) -> None:
#         # Logical Conditions
#         if self.din_rail_opt == '':
#             mounting = ''
#         else:
#             mounting = 'D0'
        
#         if self.series == '1':
#             a_b_port_size = 'C8'
#         elif self.series == '3':
#             a_b_port_size = 'C10'
#         elif self.series == '5':
#             a_b_port_size = 'C12'
        
#         self._sup_exh_block_d_side_dsub = self.Sup_Exh_Block_D_Side_Dsub(
#             prefix = 'SY',
#             series = self.series,
#             static = '0M',
#             static2 = '1',
#             static3 = '1A',
#             pilot_silencer_type = self.sup_exh,
#             a_b_port_size = a_b_port_size,
#             mounting = mounting,

#             # --- Non part number related values ---
#             quantity = int(1)
#         ) 