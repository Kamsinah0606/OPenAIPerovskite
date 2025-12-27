import streamlit as st

# ------------------------------------------------
# Page Configuration
# ------------------------------------------------
st.set_page_config(
    page_title="OpenAIPerovskite Dashboard",
    page_icon="☀️",
    layout="wide"
)

# ------------------------------------------------
# Shared Dataset URL (USED BY ALL PAGES)
# ------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/Kamsinah0606/"
    "OPenAIPerovskite/research/"
    "Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"
)

# Make DATA_URL accessible to all pages
st.session_state["DATA_URL"] = DATA_URL

# ------------------------------------------------
# Define Pages
# ------------------------------------------------
overview = st.Page(
    "pages/1_Overview_Insights.py",
    title="Overview & Key Insights",
    icon=":material/dashboard:",
    default=True
)

efficiency = st.Page(
    "pages/2_Efficiency_Trends.py",
    title="Efficiency Trends & Performance",
    icon=":material/trending_up:"
)

materials = st.Page(
    "pages/3_Material_Composition.py",
    title="Material Composition Analysis",
    icon=":material/science:"
)

device = st.Page(
    "pages/4_Device_Structure.py",
    title="Device Structure Analysis",
    icon=":material/layers:"
)

comparative = st.Page(
    "pages/5_Comparative_Analysis.py",
    title="Comparative & Multivariate Analysis",
    icon=":material/insights:"
)

explorer = st.Page(
    "pages/6_Publication_Explorer.py",
    title="Publication & Dataset Explorer",
    icon=":material/menu_book:"
)

# ------------------------------------------------
# Navigation Menu
# ------------------------------------------------
pg = st.navigation(
    {
        "OpenAIPerovskite Dashboard": [
            overview,
            efficiency,
            materials,
            device,
            comparative,
            explorer
        ]
    }
)

# ------------------------------------------------
# Run Selected Page
# ------------------------------------------------
pg.run()
