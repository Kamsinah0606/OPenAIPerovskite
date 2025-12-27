import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Overview & Key Insights")

DATA_URL = "https://raw.githubusercontent.com/Kamsinah0606/OPenAIPerovskite/research/Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.replace(" ", "_").str.replace("%", "pct")
    df["PCEpct"] = df["PCEpct"].astype(str).str.replace("%", "")
    df["PCE_Clean"] = pd.to_numeric(df["PCEpct"], errors="coerce")
    df = df.dropna(subset=["PCE_Clean"])
    df["Publication_Date"] = pd.to_datetime(df["Publication_Date"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["Publication_Date"])
    df["Year"] = df["Publication_Date"].dt.year
    return df

df = load_data()

fig = px.histogram(df, x="PCE_Clean", title="PCE Distribution")
st.plotly_chart(fig, use_container_width=True)

