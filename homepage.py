import streamlit as st
import pandas as pd

# --------------------------------------------------
# 1. PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------
st.set_page_config(
    page_title="OpenAIPerovskite Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. SIDEBAR BRANDING (DO NOT OVERRIDE NAVIGATION)
# --------------------------------------------------
st.sidebar.markdown("## ☀️ OpenAIPerovskite")
st.sidebar.markdown(
    "Interactive dashboard for **2D Perovskite Solar Cell Research** "
    "supporting performance analysis, material exploration, and literature discovery."
)
st.sidebar.markdown("---")
st.sidebar.markdown("⬅️ Select a page from the navigation above")

# --------------------------------------------------
# 3. HEADER
# --------------------------------------------------
st.title("2D Perovskite Solar Cell Research Dashboard")
st.subheader("2016 – 2025")
st.markdown(
    """
    This dashboard provides an interactive platform for visualizing and analyzing
    experimental results, material compositions, and publication trends in
    **2D perovskite solar cell research**.

    Use the **sidebar navigation** to explore different analytical modules.
    """
)

# --------------------------------------------------
# 4. DATA SOURCE (URL-BASED, SAFE)
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/Kamsinah0606/"
    "OPenAIPerovskite/research/"
    "Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"
)

@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL)

# --------------------------------------------------
# 5. QUICK DATA PREVIEW (NO STOP)
# --------------------------------------------------
try:
    df = load_data()

    st.markdown("### 📊 Dataset Snapshot")
    st.write(f"Total records loaded: **{len(df)}**")
    st.dataframe(df.head(5), use_container_width=True)

except Exception as e:
    st.warning("Dataset could not be loaded at the moment.")
    st.code(str(e))

# --------------------------------------------------
# 6. FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(
    "<center>© 2025 OpenAIPerovskite | Academic Research Dashboard</center>",
    unsafe_allow_html=True
)
