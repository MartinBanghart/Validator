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
from jsy_plugin.valve import JSY_PLUGIN_VALVE_MODEL # type: ignore
from jsy_plugin.manifold_dsub_flatribbon import JJ5SY_PLUGIN_MFLD_DSUB_MODEL # type: ignore
from jsy_plugin.manifold_terminalbox import JJ5SY_PLUGIN_MFLD_TERMBOX_MODEL # type: ignore
from jsy_plugin.manifold_leadwire import JJ5SY_PLUGIN_MFLD_LEADWIRE_MODEL # type: ignore
from jsy_plugin.manifold_ex600 import JJ5SY_PLUGIN_MFLD_EX600_MODEL # type: ignore
from jsy_plugin.manifold_ex260 import JJ5SY_PLUGIN_MFLD_EX260_MODEL # type: ignore
from jsy_plugin.manifold_ex260_profisafe import JJ5SY_PLUGIN_MFLD_EX260_PROFISAFE_MODEL # type: ignore
from jsy_plugin.manifold_ex120 import JJ5SY_PLUG_IN_MFLD_EX120_MODEL # type: ignore

# ----- NON PLUG IN -----
from jsy_nonplugin.valve import JSY_NONPLUGIN_VALVE_MODEL # type: ignore
from jsy_nonplugin.manifold_metalbase import JJ5SY_NONPLUGIN_MFLD_METALBASE_MODEL # type: ignore

# -------------------------- SY-1 --------------------------
from SY1.manifold_type_10_11_dsub_flatribbon import SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL # type: ignore

# -------------------------------------------------------------
st.set_page_config(page_title="Random Part Generator", layout="centered")
st.title("Random Part Number Generator")

def get_literal_choices(type_):
    # extract choices from a Literal[...] type --> if choices are not defined as a literal type it will not work
    if get_origin(type_) == Literal:
        return get_args(type_)
    return None

def generate_random_instance(model_class):
    # try generating a valid instance from random field selections
    for _ in range(100):
        field_values = {}
        for name, field in model_class.model_fields.items():
            choices = get_literal_choices(field.annotation)
            if choices:
                field_values[name] = random.choice(choices)
            else:
                # fallback for optional/nullable fields
                field_values[name] = field.default if field.default is not None else ""
        try:
            return model_class(**field_values)
        except ValidationError:
            continue
    return None

def generate_valid_parts(model_class, count: int):
    # generate a given number of valid part numbers
    # by creating a set, all part numbers returned will be unique
    valid_parts = set()
    attempts = 0
    max_attempts = count * 20  # prevent infinite loops

    while len(valid_parts) < count and attempts < max_attempts:
        part = generate_random_instance(model_class)
        if part:
            valid_parts.add(part.build_part_number())
        attempts += 1

    return list(valid_parts)

MODEL_MAP = {
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

    "SY-1 Type 10/11 DSUB Manifold" : SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL
}

model_choice = st.selectbox("Select Model", list(MODEL_MAP.keys()))
model_class = MODEL_MAP[model_choice]

count = st.selectbox("How many parts to generate?", [1, 10, 100])

if st.button("Generate"):
    result = generate_valid_parts(model_class, count)
    
    if result:
        df = pd.DataFrame(result, columns=["Part Number"])
        st.success(f"Generated {len(df)} valid part numbers:")
        st.dataframe(df, use_container_width=True)

        # download as excel
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="Parts")
        excel_buffer.seek(0)
        st.download_button("Download as Excel", data=excel_buffer, file_name="part_numbers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # download as notepad (.txt)
        txt_buffer = StringIO()
        txt_buffer.write("\n".join(df["Part Number"]))
        st.download_button("Download as Text", data=txt_buffer.getvalue(), file_name="part_numbers.txt", mime="text/plain")

    else:
        st.error("Could not generate valid part numbers. Try fewer or review model constraints.")
