import streamlit as st
import random
import pandas as pd
from pydantic import ValidationError
from typing import get_args, get_origin, Literal
from io import BytesIO, StringIO

# -------- To resolve moving up into different directory and importing files in separate folder --------
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# --------------------- Part Validation Models -------------------------
# -------------------------- JSY --------------------------
# ---- PLUG IN -----
from jsy_plugin.valve import JSY_PLUGIN_VALVE_MODEL
from jsy_plugin.manifold_dsub_flatribbon import JJ5SY_PLUGIN_MFLD_DSUB_MODEL 
from jsy_plugin.manifold_terminalbox import JJ5SY_PLUGIN_MFLD_TERMBOX_MODEL 
from jsy_plugin.manifold_leadwire import JJ5SY_PLUGIN_MFLD_LEADWIRE_MODEL 
from jsy_plugin.manifold_ex600 import JJ5SY_PLUGIN_MFLD_EX600_MODEL 
from jsy_plugin.manifold_ex260 import JJ5SY_PLUGIN_MFLD_EX260_MODEL 
from jsy_plugin.manifold_ex260_profisafe import JJ5SY_PLUGIN_MFLD_EX260_PROFISAFE_MODEL 
from jsy_plugin.manifold_ex120 import JJ5SY_PLUG_IN_MFLD_EX120_MODEL 
from jsy_plugin.manifold_jsy_e import JJ5SY_PLUGIN_EJECTOR_MANIFOLD_MODEL

# ----- NON PLUG IN -----
from jsy_nonplugin.valve import JSY_NONPLUGIN_VALVE_MODEL 
from jsy_nonplugin.manifold_metalbase import JJ5SY_NONPLUGIN_MFLD_METALBASE_MODEL 

# -------------------------- SY-1 --------------------------
from SY1.manifold_type_10_11_dsub_flatribbon import SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL 
from SY1.manifold_type_10_11_terminal_block_spring_type import SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL
from SY1.valve_base_mounted import SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL

# -------------------------- SY ----------------------------
from SY.valve_body_ported import SY_BODY_PORTED_VALVE_MODEL

# ----------------------------- Model Map (for user selection of models) -----------------------------

MODEL_SERIES_MAP = {
    "JSY": {
        "JSY Plugin Valve" : JSY_PLUGIN_VALVE_MODEL,
        "JSY DSUB Manifold" : JJ5SY_PLUGIN_MFLD_DSUB_MODEL,
        "JSY Terminal Manifold" : JJ5SY_PLUGIN_MFLD_TERMBOX_MODEL,
        "JSY Leadwire Manifold" : JJ5SY_PLUGIN_MFLD_LEADWIRE_MODEL,
        "JSY EX600 Manifold" : JJ5SY_PLUGIN_MFLD_EX600_MODEL,
        "JSY EX260 Manifold" : JJ5SY_PLUGIN_MFLD_EX260_MODEL,
        "JSY EX260 (PROFISAFE) Manifold" : JJ5SY_PLUGIN_MFLD_EX260_PROFISAFE_MODEL,
        "JSY EX120 Manifold" : JJ5SY_PLUG_IN_MFLD_EX120_MODEL,

        "JSY Non Plugin Valve" : JSY_NONPLUGIN_VALVE_MODEL,
        "JSY Metalbase Manifold" : JJ5SY_NONPLUGIN_MFLD_METALBASE_MODEL,
        "JSY Ejector Manifold" : JJ5SY_PLUGIN_EJECTOR_MANIFOLD_MODEL
    },

    "SY-1": {
        "SY-1 Type 10/11 DSUB Manifold" : SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL,
        "SY-1 Type 10/11 Terminal Block Manifold" : SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL,
        "SY-1 Base Mounted Valve" : SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL
    },

    "SY": {
        "SY Body Ported Valve" : SY_BODY_PORTED_VALVE_MODEL
    }
}

# ------------------------- Functions -----------------------------

def get_literal_choices(type_):
    # extract choices from a Literal[...] type --> if choices are not defined as a literal type it will not work
    if get_origin(type_) == Literal:
        return get_args(type_)
    return None

def generate_random_instance(model_class, defaults=None):
    defaults = defaults or {}

    for _ in range(100):
        field_values = {}
        for name, field in model_class.model_fields.items():
            if name in defaults:
                field_values[name] = defaults[name]
            else:
                choices = get_literal_choices(field.annotation)
                if choices:
                    field_values[name] = random.choice(choices)
                else:
                    field_values[name] = field.default if field.default is not None else ""
        try:
            return model_class(**field_values)
        except ValidationError:
            continue
    return None


def generate_valid_parts(model_class, count: int, defaults=None):
    valid_parts = set()
    attempts = 0
    max_attempts = count * 20

    while len(valid_parts) < count and attempts < max_attempts:
        part = generate_random_instance(model_class, defaults)
        if part:
            valid_parts.add(part.build_part_number())
        attempts += 1

    return list(valid_parts)

# Extract valid default options based on Literal[...] fields
def get_literal_fields(model_class):
    literal_fields = {}
    for name, field in model_class.model_fields.items():
        choices = get_literal_choices(field.annotation)
        if choices:
            literal_fields[name] = choices
    return literal_fields

def validate_defaults_by_sampling(model_class, defaults, tries=100):
    for _ in range(tries):
        instance = generate_random_instance(model_class, defaults)
        if instance is not None:
            return True  # at least one valid combo found
    return False  # no valid instances after multiple attempts

def get_validation_error_if_all_fail(model_class, defaults, tries=100):
    valid = validate_defaults_by_sampling(model_class, defaults, tries)
    return None if valid else "No valid combinations could be found after sampling. Double check default option combinations are valid."


# -------------------------------------------------------------
st.set_page_config(page_title="Part Generator", layout="wide")
st.title("Part Number Generator")

col1, col2 = st.columns(2)

# -------------------- Column 1 -------------------------

with col1:
    msubcol1, msubcol2 = st.columns([1, 2])
    with msubcol1:
        product_series = st.selectbox("Product Series", list(MODEL_SERIES_MAP.keys()))
        
    with msubcol2:
        available_models = list(MODEL_SERIES_MAP[product_series].keys())
        model_choice = st.selectbox("Select Model", available_models)
        model_class = MODEL_SERIES_MAP[product_series][model_choice]

    # user help info and dropdowns for user-selectable defaults
    with st.expander("🛠️ Help"):
        st.markdown("""
        - Select a part number model from the dropdown above
        - Optionally, choose default values for categories of the model to keep constant
        - Click **Generate** to create random valid part numbers
        - Download results as Excel or Text
        """)

    st.subheader("Configure Defaults")
    user_defaults = {}
    literal_fields = get_literal_fields(model_class)

    for field_name, choices in literal_fields.items():
        if len(choices) == 1:
            # Auto-apply the only available choice
            user_defaults[field_name] = choices[0]
        else:
            selection = st.selectbox(
                f"{field_name}:",
                ["random"] + list(choices),
                key=field_name
            )
            if selection != "random":
                user_defaults[field_name] = selection

# -------------------- Column 2 -------------------------

with col2:
    count = st.selectbox("How many parts to generate?", [1, 10, 20, 100])
    if st.button("Generate", use_container_width=True):
        subcol1, subcol2 = st.columns([1, 1])
        if not validate_defaults_by_sampling(model_class, user_defaults):
            error_msg = get_validation_error_if_all_fail(model_class, user_defaults)
            st.error(error_msg)
        else:
            result = generate_valid_parts(model_class, count, defaults=user_defaults)

            if result:
                df = pd.DataFrame(result, columns=["Part Number"])
                st.success(f"Generated {len(df)} valid part numbers:")

                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False, sheet_name="Parts")
                excel_buffer.seek(0)
                with subcol1:
                    st.download_button("Download as Excel", data=excel_buffer, file_name="part_numbers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                txt_buffer = StringIO()
                txt_buffer.write("\n".join(df["Part Number"]))
                with subcol2:
                    st.download_button("Download as Text", data=txt_buffer.getvalue(), file_name="part_numbers.txt", mime="text/plain")

                row_height = 35
                if len(df) > 20:
                    st.dataframe(df, use_container_width=True, height=row_height * (20 + 1))
                else:
                    st.dataframe(df, use_container_width=True, height=row_height * (len(df) + 1))
            else:
                st.error("Could not generate valid part numbers. Try fewer or review model constraints.")
