from pydantic import BaseModel, model_validator
from typing import Literal

# === Component Model for Part Numbering ===
# === Each callout will exist as a field with all possible options ===
# === prefixes and static symbols in pn can exists as fields too with one option ===
class SY1_PLUGIN_BLANKING_PLATE_MODEL(BaseModel):
    series: Literal['3', '5', '7']
    mounting: Literal['', 'B']

    @model_validator(mode='after')
    def validate_conditions(self) -> 'SY1_PLUGIN_BLANKING_PLATE_MODEL':
        errors = []
        
        if errors:
            # single ValueError with newline-joined messages
            raise ValueError("\n".join(errors))
        return self

    def build_part_number(self) -> str:
        # Determine if separator is needed before mounting screw
        mounting = f"-{self.mounting}" if self.mounting else ""

        return (
            f"SY{self.series}0M-26-1A{mounting}"
        )

    def description(self) -> str:
        return f"SY-1 {self.series}000 PLUGIN BLANKING PLATE"

# === Token Map with Regex Explanations ===
SY1_BASE_MOUNTED_PLUGIN_VALVE_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"SY", "length": 2},
    {"name": "series", "pattern": r"[357]", "length": 1},
    {"name": "actuation_type", "pattern": r"0M-26-1A", "length": 8},
    {"name": "separator", "pattern": r"[-]?", "length": 1},
    {"name": "mounting", "pattern": r"[B]?", "length": None}
]