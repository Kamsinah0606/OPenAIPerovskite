import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📐 Device Structure & Thickness Analysis")

DATA_URL = "https://raw.githubusercontent.com/Kamsinah0606/OPenAIPerovskite/research/Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.replace(" ", "_")
    df["PCEpct"] = df["PCE%"].astype(str).str.replace("%", "")
    df["PCE_Clean"] = pd.to_numeric(df["PCEpct"], errors="coerce")
    df["Thickness_Clean"] = pd.to_numeric(
        df["Perovskite_Thickness_nm"].astype(str).str.replace(r"[^\d.]", "", regex=True),
        errors="coerce"
    )
    return df.dropna(subset=["Thickness_Clean", "PCE_Clean"])

df = load_data()

fig1 = px.scatter(df, x="Thickness_Clean", y="PCE_Clean", trendline="ols")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.histogram(df, x="Thickness_Clean")
st.plotly_chart(fig2, use_container_width=True)

