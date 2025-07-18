from pydantic import BaseModel, PrivateAttr, model_validator, Field
from typing import Literal
from typing import Annotated

# Input for Parser
JJ5SY_PLUGIN_MFLD_DSUB_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"JJ5SY", "length": 5},
    {"name": "series", "pattern": r"[135]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "type", "pattern": r"10", "length": 2},
    {"name": "connector_type", "pattern": r"(PHC|PGC|PG|PH|PC|P|FW|FC|F)", "length": None}, # order matters here due to greedy nature, putting longer patterns is essential as patterns are checked left to right and terminate if match is made
    {"name": "connector_entry_direction", "pattern": r"(1|2)", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "valve_stations", "pattern": r"(02|03|04|05|06|07|08|09|10|11|12)", "length": 2},
    {"name": "p_e_port_entry", "pattern": r"[UDB]", "length": 1},
    {"name": "sup_exh", "pattern": r"[S]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},

    {"name": "a_b_port_size", "pattern": r'(?:C(?:2|3|4|6|8|10|12))', "length": None},
    {"name": "mounting", "pattern": r"D?", "length": None, "optional": True},
    {"name": "din_rail_opt", "pattern": r'(0|[3-9]|1[0-9]|2[0-4])?', "length": None, "optional": True},
]


class JJ5SY_PLUGIN_MFLD_DSUB_MODEL(BaseModel):
    # How to Order Information
    prefix: Literal['JJ5SY']
    series: Literal['1', '3', '5']
    type: Literal['10']
    connector_type: Literal['F', 'FW', 'FC', 'P', 'PG', 'PH', 'PC', 'PGC', 'PHC']
    connector_entry_direction: Literal['1', '2']
    valve_stations: Literal['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    p_e_port_entry: Literal['U', 'D', 'B']
    sup_exh: Literal['', 'S'] = ''
    a_b_port_size: Literal['C2', 'C3', 'C4', 'C6', 'C8', 'C10', 'C12']
    mounting: Literal['', 'D'] = ''
    din_rail_opt: Literal['', '0', '3', '4', '5', '6', '7', '8', '9', '10',
                            '11', '12', '13', '14', '15', '16', '17', '18',
                            '19', '20', '21', '22', '23', '24'] = ''

    @model_validator(mode='after')
    def check_conditions(self) -> 'JJ5SY_PLUGIN_MFLD_DSUB_MODEL':
        if self.connector_type in ('FW', 'FC', 'PGC', 'PHC') and self.connector_entry_direction == '2':
            raise ValueError('Selected connector type cannout be rotated laterally')
        if self.series == '1' and self.type == '10' and self.a_b_port_size not in ('C2', 'C4', 'C6'):
            raise ValueError("Side ported 1000 series not compatible with A,B Port Size Fittings")
        if self.series == '3' and self.type == '10' and self.a_b_port_size not in ('C4', 'C6', 'C8'):
            raise ValueError("Side ported 3000 series not compatible with A,B port size fittings")
        if self.series == '5' and self.type == '10' and self.a_b_port_size not in ('C6', 'C8', 'C10', 'C12'):
            raise ValueError("Side ported 5000 series not compatible with A,B port size fittings")
        if self.connector_type in ('PG', 'PGC') and self.valve_stations in ('10', '11', '12'):
            raise ValueError('Connector type has too many valve stations selected')
        if self.connector_type in ('PH', 'PHC') and self.valve_stations not in ('02', '03', '04'):
            raise ValueError('Connector type has too many valve stations selected')
        if self.mounting in ('') and self.din_rail_opt not in (''):
            raise ValueError('Direct mounting selected, no din rail option necessary')
        return self

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}"
            f"-{self.type}{self.connector_type}{self.connector_entry_direction}"
            f"-{self.valve_stations}{self.p_e_port_entry}{self.sup_exh}"
            f"-{self.a_b_port_size}{self.mounting}{self.din_rail_opt}"
        )
    
    def description(self) -> str:
        return (
            f"JSY{self.series}000 {self.valve_stations} STA DSUB MANIFOLD"
        )

#     # ------------- BOM ----- BOM ----- BOM ----- BOM ----- BOM ----- BOM ----- BOM  ----- BOM ------------- 

#     # --- model_post_init is an option for actions taken after validation and cleaning by the base pydantic model (think "right after __init__ and validation but before return")
#     # -- this call all function designed to create and validate child components such as the manifold block and sup/exh blocks
#     def model_post_init(self, __context) -> None:
#         self._init_manifold_block()
#         self._init_sup_exh_block_d_side()
#         self._init_sup_exh_block_u_side()
    
#     # ------------------------------------------- MANIFOLD BLOCK -------------------------------------------    
#     _manifold_block: 'JJ5SY_PLUGIN_MFLD_DSUB_MODEL.Manifold_Block' = PrivateAttr()
    
#     # Creates instance of fields inherited from top model into manifold block --> this will then be checked by pydantic model for the subcomponent
#     def _init_manifold_block(self) -> None:
#         # Logical Conditions
#         if self.a_b_port_size == 'C6':
#             block_pitch = '2'
#         else:
#             block_pitch = '1'
        
#         self._manifold_block = self.Manifold_Block(
#             prefix = 'JSY',
#             series = self.series,
#             static = '1M',
#             static2 = '2P',
#             block_pitch = block_pitch,
#             wiring_type = 'S', # hard encoded but has option 'D' for double wire which would requrire RFS
#             static3 = 'A',
#             a_b_port_size = self.a_b_port_size,

#             # --- Non part number related values ---
#             quantity = int(self.valve_stations)
#         )

#     @property
#     def manifold_block(self) -> 'JJ5SY_PLUGIN_MFLD_DSUB_MODEL.Manifold_Block':
#         return self._manifold_block    
    
#     class Manifold_Block(BaseModel):
#         # JSY[#]1M-2P-[#][#]A-[#]
#         prefix: Literal['JSY']
#         series: Literal['1', '3', '5'] 
#         static: Literal['1M']
#         static2: Literal['2P']
#         block_pitch: Literal['1', '2']
#         wiring_type: Literal['S', 'D']
#         static3: Literal['A']
#         a_b_port_size: Literal['C2', 'C3', 'C4', 'C6', 'C8', 'C10', 'C12']

#         # --- Non part number related values ---
#         quantity: int = Field(..., ge=2, le=24)
        
#         def build_part_number(self) -> str:
#             return(
#                 f"{self.prefix}{self.series}{self.static}"
#                 f"-{self.static2}"
#                 f"-{self.block_pitch}{self.wiring_type}{self.static3}"
#                 f"-{self.a_b_port_size}"
#             )
            
# # ------------------------------------------- SUP/EXH BLOCK (D-Side) -------------------------------------------    
#     _sup_exh_block_d_side: 'JJ5SY_PLUGIN_MFLD_DSUB_MODEL.Sup_Exh_Block_D_Side' = PrivateAttr()
    
#     # Creates instance of fields inherited from top model into sup exh block d-side --> this will then be checked by pydantic model for the subcomponent
#     def _init_sup_exh_block_d_side(self) -> None:
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
        
#         self._sup_exh_block_d_side = self.Sup_Exh_Block_D_Side(
#             prefix = 'JSY',
#             series = self.series,
#             static = '1M',
#             static2 = '1P',
#             static3 = '1A',
#             pilot_silencer_type = self.sup_exh,
#             a_b_port_size = a_b_port_size,
#             mounting = mounting,

#             # --- Non part number related values ---
#             quantity = int(1)
#         )

#     @property
#     def sup_exh_block_d_side(self) -> 'JJ5SY_PLUGIN_MFLD_DSUB_MODEL.Sup_Exh_Block_D_Side':
#         return self._sup_exh_block_d_side    
    
#     class Sup_Exh_Block_D_Side(BaseModel):
#         # D-Sub Connector (IP67) --- JSY[#]1M-1P-1A[#]-[#][#]
#         prefix: Literal['JSY']
#         series: Literal['1', '3', '5'] 
#         static: Literal['1M']
#         static2: Literal['1P']
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
#                 f"-{self.a_b_port_size}{self.mounting}"
#             )  
# # ------------------------------------------- SUP/EXH BLOCK (U-Side) -------------------------------------------    
#     _sup_exh_block_u_side: 'JJ5SY_PLUGIN_MFLD_DSUB_MODEL.Sup_Exh_Block_U_Side' = PrivateAttr()
    
#     # Creates instance of fields inherited from top model into sup exh block d-side --> this will then be checked by pydantic model for the subcomponent
#     def _init_sup_exh_block_u_side(self) -> None:
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
        
#         self._sup_exh_block_u_side = self.Sup_Exh_Block_U_Side(
#             prefix = 'JSY',
#             series = self.series,
#             static = '1M',
#             static2 = '3P',
#             static3 = '1A',
#             pilot_silencer_type = self.sup_exh,
#             a_b_port_size = a_b_port_size,
#             mounting = mounting,

#             # --- Non part number related values ---
#             quantity = int(1)
#         )

#     @property
#     def sup_exh_block_u_side(self) -> 'JJ5SY_PLUGIN_MFLD_DSUB_MODEL.Sup_Exh_Block_U_Side':
#         return self._sup_exh_block_u_side    
    
#     class Sup_Exh_Block_U_Side(BaseModel):
#         # D-Sub Connector (IP67) --- JSY[#]1M-1P-1A[#]-[#][#]
#         prefix: Literal['JSY']
#         series: Literal['1', '3', '5'] 
#         static: Literal['1M']
#         static2: Literal['3P']
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
#                 f"-{self.a_b_port_size}{self.mounting}"
#             )