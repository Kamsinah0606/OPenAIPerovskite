import streamlit as st
import pandas as pd

st.title("📚 Publication Explorer")

DATA_URL = "https://raw.githubusercontent.com/Kamsinah0606/OPenAIPerovskite/research/Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.replace(" ", "_")
    return df

df = load_data()

st.dataframe(
    df[[
        "Publication_Date",
        "PCE%",
        "Metal",
        "A_Cation",
        "Perovskite_Thickness_nm",
        "DOI_Number"
    ]],
    use_container_width=True
)

