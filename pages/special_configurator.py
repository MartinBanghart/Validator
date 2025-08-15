import streamlit as st
import random
import pandas as pd
from pydantic import ValidationError
from typing import get_args, get_origin, Literal
from io import BytesIO, StringIO

# -------- To resolve moving up into different directory and importing files in separate folder --------
import sys
import os

# --------------------- Part Validation Models -------------------------

# -------------------------- SY-1 --------------------------
from SY1.manifold_type_10_11_dsub_flatribbon import SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL 
from SY1.manifold_type_10_11_terminal_block_spring_type import SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL
from SY1.valve_base_mounted import SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL

# -------------------------- SY ----------------------------
from SY.valve_body_ported import SY_BODY_PORTED_VALVE_MODEL

# ----------------------------- Model Map (for user selection of models) -----------------------------

MODEL_SERIES_MAP = {

    "SY-1": {
        "Type 10/11 DSUB Manifold" : SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL,
        "Type 10/11 Terminal Block Manifold" : SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL,
        "SY-1 Base Mounted Valve" : SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL
    },

    "SY": {
        "SY Body Ported Valve" : SY_BODY_PORTED_VALVE_MODEL
    }
}

# ------------------------------------ Functions ----------------------------------------
def get_literal_choices(type_):
    # extract choices from a Literal[...] type --> if choices are not defined as a literal type it will not work
    if get_origin(type_) == Literal:
        return get_args(type_)
    return None


# Extract valid default options based on Literal[...] fields
def get_literal_fields(model_class):
    literal_fields = {}
    for name, field in model_class.model_fields.items():
        choices = get_literal_choices(field.annotation)
        if choices:
            literal_fields[name] = choices
    return literal_fields


st.set_page_config(page_title="Part Generator", layout="wide")
st.title("SY Simple Special Configurator")
st.divider()

col1, col2, col3 = st.columns(3)

# -------------------- Column 1 -------------------------

with col1:
    msubcol1, msubcol2 = st.columns([1, 2])
    with msubcol1:
        product_series = st.selectbox("Product Series", list(MODEL_SERIES_MAP.keys()))
        
    with msubcol2:
        available_models = list(MODEL_SERIES_MAP[product_series].keys())
        model_choice = st.selectbox("Select Model", available_models)
        model_class = MODEL_SERIES_MAP[product_series][model_choice]

    with msubcol1:
        with st.popover("How To Order"):
            st.markdown('How to order pdf pop out page link goes here')


    # dropdown expander to explain configuration
    with msubcol2:
        with st.popover("🛠️ Help", use_container_width=True):
            st.markdown("""
            - Select a Manifold part number model from the dropdown above
            - Then, configure the manifold to your specifications
            - Click __________________ to ____________
            """)

    st.subheader("Configure Manifold")
    user_defaults = {}
    literal_fields = get_literal_fields(model_class)

    for field_name, choices in literal_fields.items():
        if len(choices) == 1:
            # Auto-apply the only available choice
            user_defaults[field_name] = choices[0]
        else:
            selection = st.selectbox(
                f"{field_name.replace('_', ' ').title()}:",
                list(choices),
                key=field_name
            )
            user_defaults[field_name] = selection 

with col2:
    try:
        model_instance = model_class(**user_defaults)
        st.subheader("Part Number Preview")
        st.subheader(f"**{model_instance.build_part_number()}**")
        st.divider()
        
        # generate line for each stations
        for sta in range(int(user_defaults['valve_stations'])):
            st.markdown(f"Valve Station {sta + 2}:")
        
        

    except ValidationError as e:
        st.error("Invalid configuration")
        for err in e.errors():
            msg = err["msg"]
            if msg.lower().startswith("value error, "):
                msg = msg[len("Value error, "):]
            for line in msg.splitlines():
                st.write(f"• {line}")
                
    
    # generate line for each stations
    