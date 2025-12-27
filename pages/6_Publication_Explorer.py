import streamlit as st
import pandas as pd

st.title("📚 Publication & Dataset Explorer")

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

    # Convert publication date if exists
    if "Publication_Date" in df.columns:
        df["Publication_Date"] = pd.to_datetime(
            df["Publication_Date"], errors="coerce", dayfirst=True
        )

    return df

df = load_data()

# --------------------------------------------------
# Select Available Columns SAFELY
# --------------------------------------------------
desired_columns = [
    "Publication_Date",
    "PCEpct",
    "Metal",
    "A_Cation",
    "Perovskite_Thickness_nm",
    "DOI_Number"
]

available_columns = [col for col in desired_columns if col in df.columns]

if not available_columns:
    st.error("❌ No publication-related columns found in the dataset.")
    st.stop()

# --------------------------------------------------
# Display Dataset
# --------------------------------------------------
st.dataframe(
    df[available_columns]
        .rename(columns={
            "PCEpct": "PCE (%)",
            "A_Cation": "A-Site Cation",
            "Perovskite_Thickness_nm": "Thickness (nm)",
            "DOI_Number": "DOI"
        }),
    use_container_width=True
)
