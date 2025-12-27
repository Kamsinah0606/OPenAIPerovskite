import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="2D Perovskite PCE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. SOLAR CELL THEME (SAFE CSS)
# --------------------------------------------------
st.markdown("""
<style>
/* App background */
.stApp {
    background-color: #F9FAF7;
}

/* Headers */
h1, h2, h3 {
    color: #0B3C5D;
    font-weight: 700;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFF6E0;
    border-right: 2px solid #FDB813;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border-left: 6px solid #FDB813;
}

/* Dataframe */
.stDataFrame {
    border-radius: 10px;
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
URL = "https://raw.githubusercontent.com/Kamsinah0606/OPenAIPerovskite/research/Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv"

# --------------------------------------------------
# 5. DATA LOADING & CLEANING
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(URL)

    # Normalize column names
    df.columns = (
        df.columns
        .str.replace(' ', '_')
        .str.replace('%', 'pct')
        .str.replace('(', '', regex=False)
        .str.replace(')', '', regex=False)
    )

    # Clean PCE
    df['PCEpct'] = df['PCEpct'].astype(str).str.replace('$', '', regex=False).str.strip()
    df['PCE_Clean'] = pd.to_numeric(df['PCEpct'], errors='coerce')
    df = df.dropna(subset=['PCE_Clean'])
    df = df[df['PCE_Clean'] > 0.1].copy()

    # Thickness cleaning
    if 'Perovskite_Thickness_nm' in df.columns:
        df['Thickness_Clean'] = (
            df['Perovskite_Thickness_nm']
            .astype(str)
            .str.replace(r'[^\d\.]', '', regex=True)
        )
        df['Thickness_Clean'] = pd.to_numeric(df['Thickness_Clean'], errors='coerce')

    # Publication date
    if 'Publication_Date' in df.columns:
        df['Publication_Date'] = pd.to_datetime(df['Publication_Date'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['Publication_Date'])

    return df

data = load_data()

if data.empty:
    st.stop()

# --------------------------------------------------
# 6. OVERVIEW METRIC
# --------------------------------------------------
st.subheader("Overview of Power Conversion Efficiency (PCE)")
st.metric(
    "Maximum PCE Recorded",
    f"{data['PCE_Clean'].max():.2f} %",
    f"Median PCE: {data['PCE_Clean'].median():.2f} %"
)

# --------------------------------------------------
# 7. SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Data Filters")

pce_min, pce_max = data['PCE_Clean'].min(), data['PCE_Clean'].max()
pce_range = st.sidebar.slider(
    "PCE Range (%)",
    float(pce_min),
    float(pce_max),
    (float(pce_min), float(pce_max)),
    step=0.1
)

min_year = data['Publication_Date'].dt.year.min()
max_year = data['Publication_Date'].dt.year.max()
year_range = st.sidebar.slider(
    "Publication Year",
    int(min_year),
    int(max_year),
    (int(min_year), int(max_year))
)

filtered_data = data[
    (data['PCE_Clean'] >= pce_range[0]) &
    (data['PCE_Clean'] <= pce_range[1]) &
    (data['Publication_Date'].dt.year >= year_range[0]) &
    (data['Publication_Date'].dt.year <= year_range[1])
]

st.sidebar.info(f"Showing {len(filtered_data)} of {len(data)} records")

# --------------------------------------------------
# 8. VISUALIZATIONS
# --------------------------------------------------

# Histogram
st.subheader("PCE Distribution")
fig_hist = px.histogram(
    filtered_data,
    x="PCE_Clean",
    nbins=30,
    title="Distribution of PCE (%)",
    color_discrete_sequence=["#FDB813"]
)
fig_hist.update_layout(xaxis_title="PCE (%)", yaxis_title="Count")
st.plotly_chart(fig_hist, use_container_width=True)

# Line chart
st.subheader("PCE Trend Over Time")
yearly_pce = (
    filtered_data
    .groupby(filtered_data['Publication_Date'].dt.year)['PCE_Clean']
    .mean()
    .reset_index(name="Mean PCE (%)")
)

fig_line = px.line(
    yearly_pce,
    x="Publication_Date",
    y="Mean PCE (%)",
    markers=True,
    title="Average PCE Evolution",
    color_discrete_sequence=["#0B3C5D"]
)
fig_line.update_layout(xaxis_title="Year", yaxis_title="Mean PCE (%)")
st.plotly_chart(fig_line, use_container_width=True)

# Pie chart
st.subheader("Metal Composition")
metal_counts = filtered_data['Metal'].dropna().value_counts().reset_index()
metal_counts.columns = ["Metal", "Count"]

fig_pie = px.pie(
    metal_counts,
    names="Metal",
    values="Count",
    hole=0.4,
    title="Distribution of Metal Types",
    color_discrete_sequence=px.colors.sequential.Solar
)
st.plotly_chart(fig_pie, use_container_width=True)

# Bar chart
st.subheader("A-Site Cation Distribution")
a_cation_counts = filtered_data['A_Cation'].dropna().value_counts().reset_index()
a_cation_counts.columns = ["A-Site Cation", "Count"]

fig_bar = px.bar(
    a_cation_counts,
    x="A-Site Cation",
    y="Count",
    text="Count",
    title="A-Site Cation Usage",
    color_discrete_sequence=["#F85A40"]
)
fig_bar.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------------------------------
# 9. RAW DATA TABLE
# --------------------------------------------------
st.subheader("Filtered Dataset")
st.dataframe(
    filtered_data[['PCE_Clean', 'Metal', 'A_Cation', 'Thickness_Clean', 'DOI_Number']]
    .rename(columns={
        'PCE_Clean': 'PCE (%)',
        'A_Cation': 'A-Site Cation',
        'Thickness_Clean': 'Thickness (nm)',
        'DOI_Number': 'DOI'
    }),
    use_container_width=True
)
