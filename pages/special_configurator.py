import streamlit as st
from pydantic import ValidationError
from typing import get_args, get_origin, Literal
import base64

# --------------------- Part Validation Models -------------------------

# -------------------------- SY-1 --------------------------
from SY1.manifold_type_10_11_dsub_flatribbon import SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL 
from SY1.manifold_type_10_11_terminal_block_spring_type import SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL
from SY1.valve_base_mounted import SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL
from SY1.valve_blank_plate import SY1_PLUGIN_BLANKING_PLATE_MODEL

# -------------------------- SY ----------------------------
from SY.valve_body_ported import SY_BODY_PORTED_VALVE_MODEL

# ----------------------------- Model Map (for user selection of models) -----------------------------
# -- Product Series
# ----- Manifold Models
# ----- Valve model related to manifold model
MANIFOLD_VALVE_ASSOCIATIONS = {
    "SY-1": {
        "Type 10/11 DSUB Manifold": {
            "manifold_model": SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL,
            "valve_model": SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL,
            "blanking_plate_model": SY1_PLUGIN_BLANKING_PLATE_MODEL,
            "hto_pdf": "SY1/HTO/manifold_type_10_11_dsub_flatribbon_hto.pdf"
        },
        "Type 10/11 Terminal Block Manifold": {
            "manifold_model": SY1_MFLD_TYPE_10_11_TERM_BLOCK_SPRING_MODEL,
            "valve_model": SY1_BASE_MOUNTED_PLUGIN_VALVE_MODEL,
            "blanking_plate_model": SY1_PLUGIN_BLANKING_PLATE_MODEL,
            "hto_pdf": "SY1/HTO/manifold_type_10_11_terminal_block_spring_type_hto.pdf"
        }
    },
    "SY": {
        "SY MANIFOLD MODEL": {
            # "manifold_model" : MANIFOLD_MODEL_HERE,
            "valve_model": SY_BODY_PORTED_VALVE_MODEL
        }
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

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    
# Modal dialog definition
@st.dialog("How To Order")
def show_order_pdf():
    if hto_pdf_path:
        show_pdf(hto_pdf_path)
    else:
        st.warning("No How to Order PDF available for this manifold type.")

# ------------------------------------ ---------- ----------------------------------------

st.set_page_config(page_title="Part Generator", layout="wide")
st.title("SY Simple Special Configurator")
st.divider()

col1, col2 = st.columns([1, 2.5])

# -------------------- Column 1 UI -------------------------

with col1:
    msubcol1, msubcol2 = st.columns([1, 2])

    # select Product Series
    with msubcol1:
        product_series = st.selectbox("Product Series", list(MANIFOLD_VALVE_ASSOCIATIONS.keys()))

    # select Manifold Type (Model)
    with msubcol2:
        available_manifolds = list(MANIFOLD_VALVE_ASSOCIATIONS[product_series].keys())
        manifold_choice = st.selectbox("Select Manifold Type", available_manifolds)

        # extract models
        selected_entry = MANIFOLD_VALVE_ASSOCIATIONS[product_series][manifold_choice]
        manifold_model = selected_entry.get("manifold_model", "N/A")
        valve_model = selected_entry.get("valve_model", "N/A")
        blanking_plate_model = selected_entry.get("blanking_plate_model", "N/A")
        hto_pdf_path = selected_entry.get("hto_pdf", "N/A")

    # how to order popover - could be useful to display link to how to order page
    with msubcol1:
        if st.button("How To Order", use_container_width=True):
            show_order_pdf()   # --------------->>>>>> remember to change this to dynamic

    # dropdown expander to explain configuration
    with msubcol2:
        with st.popover("🛠️ Help", use_container_width=True):
            st.markdown("""
            - Select a Product series and Manifold type from the dropdowns above
            - Configure the manifold to your specifications
            - Upon successful determination of manifold, valves can be configured
            """)
            
    with st.container(border=True):
        st.subheader("Configure Manifold")
        user_defaults = {}
        literal_fields = get_literal_fields(manifold_model)

        for field_name, choices in literal_fields.items():
            if len(choices) == 1:
                # auto-apply the only available choice
                user_defaults[field_name] = choices[0]
            else:
                selection = st.selectbox(
                    f"{field_name.replace('_', ' ').title()}:",
                    list(choices),
                    key=field_name
                )
                user_defaults[field_name] = selection 

# Second column for displaying configured manifold part number
# --- shows valve configuration for each station
# ----------------------------------------------------------------------------------
# --- Helper Functions ---
def get_all_literal_fields(model_cls):
    fields = {}
    for field_name, field_type in model_cls.__annotations__.items():
        if get_origin(field_type) is Literal:
            fields[field_name] = get_args(field_type)
    return fields

# categorizes fields to be or not to be displayed in configurators
# --- fields that are static (no configurable option) should not be displayed for simplicity
def split_fields(fields):
    visible = {k: v for k, v in fields.items() if len(v) > 1 and k != "series"}
    hidden = {k: v[0] for k, v in fields.items() if len(v) == 1 or k == "series"}
    return visible, hidden

# This will act as displayed text for valve configuration options if selected
# It should be made for the cleaned version of pydantic model field names that previously contained underscores and no capitalization
custom_map = {
    # Base Mounted Valve Fields
    "Actuation Type": "Actuation",
    "Back Pressure Check Valve": "Back Pres. Chk",
    "Light Surge Voltage Suppressor": "Light Surge",
    "Manual Override": "Man Override",
    "Mounting Screw": "Mount Screw"
}

def smart_abbreviate(text: str, max_len: int = 13) -> str:
    normalized = text.replace('_', ' ').strip().title()
    # If the normalized label is already short enough, return it as-is
    if len(normalized) <= max_len:
        return normalized
    # Check for custom abbreviation
    if normalized in custom_map:
        return custom_map[normalized][:max_len]
    # Fallback: use initials
    return ''.join(w[0] for w in normalized.split())[:max_len]

# ----------------------------------------------------------------------------------

# --- Column 2 UI ---
with col2:
    try:
        if manifold_model != "N/A":
            model_instance = manifold_model(**user_defaults)
            st.subheader("Part Number Preview")
            st.info(f"**{model_instance.build_part_number()}**")

            with st.container(border=True):
                st.subheader('Configure Valves')

                valve_station_count = user_defaults.get('valve_stations', 0)
                try:
                    station_count = int(valve_station_count)
                except ValueError:
                    station_count = 0

                # --- Defining class that relate to options available on a manifold station ---
                valve_model_cls = valve_model
                blanking_plate_model_cls = blanking_plate_model
                
                STATION_TYPE_MODELS = {
                    "Valve": valve_model_cls,
                    "Blanking Plate": blanking_plate_model_cls
                }

                # --- Extract Fields ---
                all_valve_fields = get_all_literal_fields(valve_model_cls)
                val_visible_fields, val_hidden_defaults = split_fields(all_valve_fields)
                
                all_blanking_plate_fields = get_all_literal_fields(blanking_plate_model_cls)
                blanking_plate_visible_fields, blanking_plate_hidden_defaults = split_fields(all_blanking_plate_fields)
                

                station_configs = []

                for sta in range(station_count):
                    st.markdown(f"### Station {sta + 1}")
                    
                    # --- Station Type Selection ---
                    station_type = st.radio(
                        "Select Station Type",
                        list(STATION_TYPE_MODELS.keys()),
                        horizontal=True,
                        key=f"station_type_{sta}"
                    )

                    config = {}

                    if station_type == "Valve":
                        header_cols = st.columns(len(val_visible_fields))
                        cols = st.columns(len(val_visible_fields))

                        for i, (field_name, options) in enumerate(val_visible_fields.items()):
                            short_label = smart_abbreviate(field_name, max_len=13)

                            with header_cols[i]:
                                st.markdown(f"<div style='text-align:center; font-weight:600;'>{short_label}</div>", unsafe_allow_html=True)

                            with cols[i]:
                                selected = st.selectbox(
                                    "",
                                    options,
                                    key=f"{field_name}_{sta}",
                                    label_visibility="collapsed"
                                )
                                config[field_name] = selected

                        config.update(val_hidden_defaults)
                        config["series"] = model_instance.series

                    elif station_type == "Blanking Plate":
                            header_cols = st.columns(len(blanking_plate_visible_fields))
                            cols = st.columns(len(blanking_plate_visible_fields))

                            for i, (field_name, options) in enumerate(blanking_plate_visible_fields.items()):
                                short_label = smart_abbreviate(field_name, max_len=13)

                                with header_cols[i]:
                                    st.markdown(f"<div style='text-align:center; font-weight:600;'>{short_label}</div>", unsafe_allow_html=True)

                                with cols[i]:
                                    selected = st.selectbox(
                                        "",
                                        options,
                                        key=f"blanking_{field_name}_{sta}",
                                        label_visibility="collapsed"
                                    )
                                    config[field_name] = selected

                            config.update(blanking_plate_hidden_defaults)
                            config["series"] = model_instance.series

                    st.divider()
                    station_configs.append((station_type, config))

                # --- Validate and Preview Station Part Numbers ---
                for idx, (station_type, config) in enumerate(station_configs):
                    model_cls = STATION_TYPE_MODELS[station_type]
                    try:
                        instance = model_cls(**config)
                        part_number = instance.build_part_number() if hasattr(instance, "build_part_number") else "N/A"
                        st.success(f"Station {idx + 1} ({station_type}): {part_number}")
                    except ValidationError as e:
                        st.error(f"Station {idx + 1} Invalid {station_type} Configuration")
                        for err in e.errors():
                            msg = err["msg"]
                            if msg.lower().startswith("value error, "):
                                msg = msg[len("Value error, "):]
                            for line in msg.splitlines():
                                st.write(f"• {line}")

        else:
            st.warning("No valid manifold model selected.")
            
    # --- Error Output for Manifold Part Number ---
    except ValidationError as e:
        st.error("Invalid manifold configuration")
        for err in e.errors():
            msg = err["msg"]
            if msg.lower().startswith("value error, "):
                msg = msg[len("Value error, "):]
            for line in msg.splitlines():
                st.write(f"• {line}")