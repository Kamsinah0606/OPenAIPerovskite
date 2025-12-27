import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="2D Perovskite Dashboard",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #F9FAF7; color: black; }
h1,h2,h3,h4,h5,h6,p,span,label,div { color: black !important; }
</style>
""", unsafe_allow_html=True)

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

st.title("☀️ OpenAIPerovskite Dashboard")
st.subheader("Overview of 2D Perovskite Research (2016–2025)")

col1, col2, col3 = st.columns(3)
col1.metric("Max PCE (%)", f"{df['PCE_Clean'].max():.2f}")
col2.metric("Median PCE (%)", f"{df['PCE_Clean'].median():.2f}")
col3.metric("Total Publications", len(df))

fig = px.histogram(df, x="PCE_Clean", nbins=30, title="PCE Distribution")
st.plotly_chart(fig, use_container_width=True)

pub_trend = df.groupby("Year").size().reset_index(name="Publications")
fig2 = px.line(pub_trend, x="Year", y="Publications", markers=True, title="Publication Trend")
st.plotly_chart(fig2, use_container_width=True)
