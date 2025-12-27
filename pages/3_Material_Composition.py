import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🧪 Material Composition Analysis")

DATA_URL = "https://raw.githubusercontent.com/Kamsinah0606/OPenAIPerovskite/research/Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.replace(" ", "_")
    return df

df = load_data()

metal_counts = df["Metal"].value_counts().reset_index()
metal_counts.columns = ["Metal", "Count"]

fig1 = px.pie(metal_counts, names="Metal", values="Count", hole=0.4)
st.plotly_chart(fig1, use_container_width=True)

a_counts = df["A_Cation"].value_counts().reset_index()
a_counts.columns = ["A-Site Cation", "Count"]

fig2 = px.bar(a_counts, x="A-Site Cation", y="Count")
st.plotly_chart(fig2, use_container_width=True)

