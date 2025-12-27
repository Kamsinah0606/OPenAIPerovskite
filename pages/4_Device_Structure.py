import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📐 Device Structure & Thickness Analysis")

# --------------------------------------------------
# Load shared dataset
# --------------------------------------------------
DATA_URL = st.session_state.get("DATA_URL")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "pct")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df

df = load_data()

# --------------------------------------------------
# Validate required columns
# --------------------------------------------------
required_cols = ["Perovskite_Thickness_nm", "PCEpct"]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.stop()

# --------------------------------------------------
# Clean thickness data
# --------------------------------------------------
df["Thickness_nm"] = (
    df["Perovskite_Thickness_nm"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
)

df["Thickness_nm"] = pd.to_numeric(df["Thickness_nm"], errors="coerce")
df = df.dropna(subset=["Thickness_nm", "PCEpct"])

# --------------------------------------------------
# Visualization 1: Thickness distribution
# --------------------------------------------------
fig_hist = px.histogram(
    df,
    x="Thickness_nm",
    nbins=30,
    title="Distribution of Perovskite Layer Thickness (nm)"
)
st.plotly_chart(fig_hist, use_container_width=True)

# --------------------------------------------------
# Visualization 2: Thickness vs PCE (NO OLS)
# --------------------------------------------------
fig_scatter = px.scatter(
    df,
    x="Thickness_nm",
    y="PCEpct",
    title="Perovskite Thickness vs Power Conversion Efficiency",
)
st.plotly_chart(fig_scatter, use_container_width=True)
