import streamlit as st

# --------------------- Part Validation Models -------------------------
# ---- PLUG IN -----
from jsy_plugin.valve import JSY_PLUGIN_VALVE_MODEL, PLUGIN_VALVE_TOKEN_MAP
from jsy_plugin.manifold_dsub_flatribbon import JJ5SY_PLUGIN_MFLD_DSUB_MODEL, JJ5SY_PLUGIN_MFLD_DSUB_TOKEN_MAP
from jsy_plugin.manifold_terminalbox import JJ5SY_PLUGIN_MFLD_TERMBOX_MODEL, JJ5SY_PLUGIN_MFLD_TERMBOX_TOKEN_MAP
from jsy_plugin.manifold_leadwire import JJ5SY_PLUGIN_MFLD_LEADWIRE_MODEL, JJ5SY_PLUGIN_MFLD_LEADWIRE_TOKEN_MAP
from jsy_plugin.manifold_ex600 import JJ5SY_PLUGIN_MFLD_EX600_MODEL, JJ5SY_PLUGIN_MFLD_EX600_TOKEN_MAP
from jsy_plugin.manifold_ex260 import JJ5SY_PLUGIN_MFLD_EX260_MODEL, JJ5SY_PLUGIN_MFLD_EX260_TOKEN_MAP
from jsy_plugin.manifold_ex260_profisafe import JJ5SY_PLUGIN_MFLD_EX260_PROFISAFE_MODEL, JJ5SY_PLUGIN_MFLD_EX260_PROFISAFE_TOKEN_MAP
from jsy_plugin.manifold_ex120 import JJ5SY_PLUG_IN_MFLD_EX120_MODEL, JJ5SY_PLUGIN_MFLD_EX120_TOKEN_MAP

# ----- NON PLUG IN -----
from jsy_nonplugin.valve import JSY_NONPLUGIN_VALVE_MODEL, NONPLUGIN_VALVE_TOKEN_MAP
from jsy_nonplugin.manifold_metalbase import JJ5SY_NONPLUGIN_MFLD_METALBASE_MODEL, JJ5SY_NONPLUGIN_MFLD_METALBASE_TOKEN_MAP

# ----- SY-1 -----
from SY1.manifold_type_10_11_dsub_flatribbon import SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL, SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_TOKEN_MAP

# ----- GENERAL FUNCTIONS -----
from general_functions.parser import TokenMapParser
# ----------------------------------------------------------------------
from pydantic import ValidationError
import pandas as pd
import re

# -------------------------- MAIN CODE --------------------------

st.title("JSY Part Number Validator")

# Regex Pattern Matching for Model Recognition
# --------------------- JSY ---------------------------
# --- plugin
VALVE_DETECTOR = r"^JSY(?P<series>[135])(?P<actuation>[1-5A-C])(?P<static>\d{2})" # actually covers both plugin and non plugin
JSY_DSUB_MANIFOLD = r"^JJ5SY[135]-10(F|FW|FC|P|PG|PH|PC|PGC|PHC)[12]-"
JSY_TERMINAL_BOX_MANIFOLD = r"^JJ5SY[135]-10(TC|T)-"
JSY_LEADWIRE_MANIFOLD = r"^JJ5SY[135]-10(L1|L2|L3)[123]-"
JSY_EX600_MANIFOLD = r"^JJ5SY[135]-10S6"
JSY_EX260_MANIFOLD  = r"^JJ5SY[135]-10S(?!FPN|DPN|0)[A-Z0-9]{2,3}"
JSY_EX260_PROFISAFE_MANIFOLD = r"^JJ5SY[135]-10S(FPN|DPN|0)"
JSY_EX120_MANIFOLD = r"^JJ5SY[135]-10S3(ZBN|ZB|V|Q|0)-"

# --- non plugin
JSY_METALBASE_MANIFOLD = r"^JJ5SY[135]-(40|41)"

# --------------------- --- ---------------------------
# --------------------- SY1 ---------------------------
SY1_TYPE_10_11_DSUB_MANIFOLD = r"^SS5Y[357]-(10|11)(F|FW|P|PG|PH)"

# ---------- USER INPUT ----------

part_number = st.text_input("Enter a part number", "")

# --------- MODEL RECOGNITION ---------

if part_number:
    model = None
    token_map = None

    # ---------------- JSY MANIFOLDS -----------------------
    if re.match(JSY_TERMINAL_BOX_MANIFOLD, part_number):
        model = JJ5SY_PLUGIN_MFLD_TERMBOX_MODEL
        token_map = JJ5SY_PLUGIN_MFLD_TERMBOX_TOKEN_MAP

    elif re.match(JSY_DSUB_MANIFOLD, part_number):
        model = JJ5SY_PLUGIN_MFLD_DSUB_MODEL
        token_map = JJ5SY_PLUGIN_MFLD_DSUB_TOKEN_MAP

    elif re.match(JSY_LEADWIRE_MANIFOLD, part_number):
        model = JJ5SY_PLUGIN_MFLD_LEADWIRE_MODEL
        token_map = JJ5SY_PLUGIN_MFLD_LEADWIRE_TOKEN_MAP

    elif re.match(JSY_EX600_MANIFOLD, part_number):
        model = JJ5SY_PLUGIN_MFLD_EX600_MODEL
        token_map = JJ5SY_PLUGIN_MFLD_EX600_TOKEN_MAP

    elif re.match(JSY_EX260_MANIFOLD, part_number):
        model = JJ5SY_PLUGIN_MFLD_EX260_MODEL
        token_map = JJ5SY_PLUGIN_MFLD_EX260_TOKEN_MAP

    elif re.match(JSY_EX260_PROFISAFE_MANIFOLD, part_number):
        model = JJ5SY_PLUGIN_MFLD_EX260_PROFISAFE_MODEL
        token_map = JJ5SY_PLUGIN_MFLD_EX260_PROFISAFE_TOKEN_MAP

    elif re.match(JSY_EX120_MANIFOLD, part_number):
        model = JJ5SY_PLUG_IN_MFLD_EX120_MODEL
        token_map = JJ5SY_PLUGIN_MFLD_EX120_TOKEN_MAP
    
    elif re.match(JSY_METALBASE_MANIFOLD, part_number):
        model = JJ5SY_NONPLUGIN_MFLD_METALBASE_MODEL
        token_map = JJ5SY_NONPLUGIN_MFLD_METALBASE_TOKEN_MAP

    # ---------------- SY1 MANIFOLDS -----------------------
    elif re.match(SY1_TYPE_10_11_DSUB_MANIFOLD, part_number):
        model = SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_MODEL
        token_map = SY1_MFLD_TYPE_10_11_DSUB_FLATRIBBON_TOKEN_MAP

    else:
    # checking valve options
        match = re.match(VALVE_DETECTOR, part_number)
        if match:
            static_code = match.group("static")
            if static_code == "40":
                model = JSY_NONPLUGIN_VALVE_MODEL
                token_map = NONPLUGIN_VALVE_TOKEN_MAP
            elif static_code == "00":
                model = JSY_PLUGIN_VALVE_MODEL
                token_map = PLUGIN_VALVE_TOKEN_MAP
            else:
                st.error(f"Unknown static code `{static_code}` — cannot determine part type.")
                st.stop()
        else:
            st.error("Invalid part number format — unable to route to a model.")
            st.stop()


    # ------------ PART VALIDATION ------------
    try:
        parser = TokenMapParser(token_map)
        tokens = parser.parse(part_number)
        valve = model(**tokens)

        validator_df = pd.DataFrame(valve.model_dump().items(), columns=["Field", "Value"])
        st.success("✅ Part number is valid.")
        st.dataframe(validator_df, use_container_width=True, height=35 * (len(tokens) + 1))

        st.markdown(f"### {valve.description()}:\n`{valve.build_part_number()}`")

    # PyDantic Model is Throwing Error
    except ValidationError as e:
        st.error("❌ Validation error:")
        for err in e.errors():
            message = err["msg"].removeprefix("Value error, ")
            st.markdown(f"{message}")

        if "tokens" in locals():
            st.subheader("Parsed Tokens")
            st.dataframe(pd.DataFrame([tokens]), use_container_width=True)

    # Parser is Throwing Error
    except ValueError as e:
        st.error(f"❌ Parse error: {e}")
        if "tokens" in locals():
            st.subheader("🔍 Partial Tokens Extracted")
            st.dataframe(pd.DataFrame([tokens]).T, use_container_width=True)
        else:
            st.warning("⚠️ Parsing failed before any tokens could be generated.")
