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
# Clean Thickness Column SAFELY
# --------------------------------------------------
if "Perovskite_Thickness_nm" not in df.columns:
    st.error("❌ Perovskite thickness data is not available in this dataset.")
    st.stop()

df["Thickness_Clean"] = (
    df["Perovskite_Thickness_nm"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
)

df["Thickness_Clean"] = pd.to_numeric(df["Thickness_Clean"], errors="coerce")

df = df.dropna(subset=["Thickness_Clean", "PCEpct"])

# --------------------------------------------------
# Visualization 1: Thickness Distribution
# --------------------------------------------------
fig_hist = px.histogram(
    df,
    x="Thickness_Clean",
    nbins=30,
    title="Distribution of Perovskite Layer Thickness (nm)"
)
st.plotly_chart(fig_hist, use_container_width=True)

# --------------------------------------------------
# Visualization 2: Thickness vs PCE
# --------------------------------------------------
fig_scatter = px.scatter(
    df,
    x="Thickness_Clean",
    y="PCEpct",
    title="Relationship Between Perovskite Thickness and PCE",
    trendline="ols"
)
st.plotly_chart(fig_scatter, use_container_width=True)
