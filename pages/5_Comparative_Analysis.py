import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Comparative & Multivariate Analysis")

DATA_URL = "https://raw.githubusercontent.com/Kamsinah0606/OPenAIPerovskite/research/Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.replace(" ", "_").str.replace("%", "pct")
    df["PCE_Clean"] = pd.to_numeric(df["PCEpct"].astype(str).str.replace("%", ""), errors="coerce")
    df["Publication_Date"] = pd.to_datetime(df["Publication_Date"], errors="coerce", dayfirst=True)
    df["Year"] = df["Publication_Date"].dt.year
    return df.dropna(subset=["PCE_Clean", "Year"])

df = load_data()

heat = df.groupby(["Year", "Metal"], as_index=False)["PCE_Clean"].mean()

fig1 = px.density_heatmap(heat, x="Year", y="Metal", z="PCE_Clean")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.box(df, x="Metal", y="PCE_Clean")
st.plotly_chart(fig2, use_container_width=True)

