import streamlit as st
import pandas as pd

st.title("📚 Publication Explorer")

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
# Safely select available columns
# --------------------------------------------------
candidate_columns = [
    "Publication_Year",
    "PCEpct",
    "Metal",
    "A_Cation",
    "Perovskite_Thickness_nm",
    "DOI"
]

available_columns = [c for c in candidate_columns if c in df.columns]

if not available_columns:
    st.error("❌ No publication-related columns available in this dataset.")
    st.stop()

# --------------------------------------------------
# Display table
# --------------------------------------------------
st.dataframe(
    df[available_columns],
    use_container_width=True
)
