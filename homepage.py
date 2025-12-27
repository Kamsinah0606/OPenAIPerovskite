import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------------------------------
# 1. PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="2D Perovskite PCE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. SOLAR THEME (SAFE CSS)
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #F9FAF7; }

h1, h2, h3 {
    color: #0B3C5D;
    font-weight: 700;
}

section[data-testid="stSidebar"] {
    background-color: #FFF6E0;
    border-right: 2px solid #FDB813;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border-left: 6px solid #FDB813;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. HEADER
# --------------------------------------------------
st.header("☀️ OpenAIPerovskite", divider="gray")
st.title("2D Perovskite Solar Cell Efficiency Dashboard (2016–2025)")
st.markdown("---")

# --------------------------------------------------
# 4. DATA SOURCE
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/"
    "Kamsinah0606/OPenAIPerovskite/research/"
    "Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"
)

# --------------------------------------------------
# 5. LOAD & CLEAN DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "pct")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    # ---- PCE ----
    if "PCEpct" not in df.columns:
        st.error("❌ PCE column not found in dataset.")
        return pd.DataFrame()

    df["PCEpct"] = df["PCEpct"].astype(str).str.replace("%", "", regex=False)
    df["PCE_Clean"] = pd.to_numeric(df["PCEpct"], errors="coerce")
    df = df.dropna(subset=["PCE_Clean"])
    df = df[df["PCE_Clean"] > 0.1]

    # ---- Publication Date ----
    if "Publication_Date" in df.columns:
        df["Publication_Date"] = pd.to_datetime(
            df["Publication_Date"],
            errors="coerce",
            dayfirst=True
        )
        df = df.dropna(subset=["Publication_Date"])
        df["Year"] = df["Publication_Date"].dt.year
    else:
        st.error("❌ Publication_Date column missing.")
        return pd.DataFrame()

    # ---- Thickness ----
    if "Perovskite_Thickness_nm" in df.columns:
        df["Thickness_Clean"] = (
            df["Perovskite_Thickness_nm"]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
        )
        df["Thickness_Clean"] = pd.to_numeric(
            df["Thickness_Clean"], errors="coerce"
        )

    return df


data = load_data()
if data.empty:
    st.stop()

# --------------------------------------------------
# 6. METRICS
# --------------------------------------------------
st.subheader("Overview of Power Conversion Efficiency (PCE)")

st.metric(
    label="Maximum PCE Recorded",
    value=f"{data['PCE_Clean'].max():.2f} %",
    delta=f"Median: {data['PCE_Clean'].median():.2f} %"
)

# --------------------------------------------------
# 7. FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Filters")

pce_range = st.sidebar.slider(
    "PCE Range (%)",
    float(data["PCE_Clean"].min()),
    float(data["PCE_Clean"].max()),
    (
        float(data["PCE_Clean"].min()),
        float(data["PCE_Clean"].max())
    ),
    step=0.1
)

year_range = st.sidebar.slider(
    "Publication Year",
    int(data["Year"].min()),
    int(data["Year"].max()),
    (
        int(data["Year"].min()),
        int(data["Year"].max())
    )
)

filtered_data = data[
    data["PCE_Clean"].between(*pce_range)
    & data["Year"].between(*year_range)
]

# --------------------------------------------------
# 8. VISUALIZATIONS
# --------------------------------------------------

# --- Histogram ---
fig_hist = px.histogram(
    filtered_data,
    x="PCE_Clean",
    nbins=30,
    title="Distribution of PCE (%)",
    color_discrete_sequence=["#FDB813"]
)
st.plotly_chart(fig_hist, use_container_width=True)

# --- Line Chart (FIXED & SAFE) ---
yearly_pce = (
    filtered_data
    .groupby("Year", as_index=False)["PCE_Clean"]
    .mean()
    .rename(columns={"PCE_Clean": "Mean PCE (%)"})
)

fig_line = px.line(
    yearly_pce,
    x="Year",
    y="Mean PCE (%)",
    markers=True,
    title="Average PCE Trend",
    color_discrete_sequence=["#0B3C5D"]
)
st.plotly_chart(fig_line, use_container_width=True)

# --- Pie Chart ---
if "Metal" in filtered_data.columns:
    metal_counts = (
        filtered_data["Metal"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    metal_counts.columns = ["Metal", "Count"]

    fig_pie = px.pie(
        metal_counts,
        names="Metal",
        values="Count",
        hole=0.4,
        title="Metal Composition",
        color_discrete_sequence=px.colors.sequential.YlOrBr
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- Bar Chart ---
if "A_Cation" in filtered_data.columns:
    a_counts = (
        filtered_data["A_Cation"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    a_counts.columns = ["A-Site Cation", "Count"]

    fig_bar = px.bar(
        a_counts,
        x="A-Site Cation",
        y="Count",
        text="Count",
        title="A-Site Cation Distribution",
        color_discrete_sequence=["#F85A40"]
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------------------------------
# 9. DATA TABLE
# --------------------------------------------------
st.subheader("Filtered Dataset")

table_cols = [
    c for c in
    ["PCE_Clean", "Metal", "A_Cation", "Thickness_Clean", "DOI_Number"]
    if c in filtered_data.columns
]

st.dataframe(
    filtered_data[table_cols].rename(columns={
        "PCE_Clean": "PCE (%)",
        "A_Cation": "A-Site Cation",
        "Thickness_Clean": "Thickness (nm)",
        "DOI_Number": "DOI"
    }),
    use_container_width=True
)
