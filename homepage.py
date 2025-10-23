import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="OpenAIPerovskite"
)

st.header("OPenAIPerovskite", divider="gray")

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="2D Perovskite PCE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DATA LOADING AND CLEANING ---
@st.cache_data
def load_data():
    """Loads and cleans the 2D Perovskite dataset."""
    # NOTE: Assuming the CSV file is accessible relative to this script, 
    # e.g., in a 'data' folder or uploaded to the Streamlit environment if run locally.
    # Replace 'path/to/your/data.csv' with the actual path or name of the dataset file.
    try:
        df = pd.read_csv('Dataset 2D Perovskite (2016-2025) - Mixed.csv')
    except FileNotFoundError:
        st.error("Error: 'Dataset 2D Perovskite (2016-2025) - Mixed.csv' not found. Please ensure the file is in the correct directory.")
        return pd.DataFrame() # Return empty DataFrame on failure

    # Normalize column names for easier access (optional but recommended)
    df.columns = df.columns.str.replace(' ', '_').str.replace('%', 'pct').str.replace('(', '').str.replace(')', '')
    
    # Clean the PCE% column to numeric, coercing errors to NaN
    # The PCE column often requires cleaning due to variations like '76' vs '0.76' in FF, 
    # or trailing characters/spaces if manually entered.
    
    # Clean up non-numeric data in the PCE column (handling potential string artifacts)
    df['PCEpct'] = df['PCEpct'].astype(str).str.replace('$', '').str.strip()
    
    # Attempt to convert to float. Errors are coerced to NaN (Missing Data)
    df['PCE_Clean'] = pd.to_numeric(df['PCEpct'], errors='coerce')
    
    # Filter out rows where PCE is missing or unreasonably low (e.g., < 0.1% are often errors)
    df = df.dropna(subset=['PCE_Clean'])
    df = df[df['PCE_Clean'] > 0.1].copy()

    # Convert Publication Date to datetime object for time series analysis
    df = pd.to_datetime(df, errors='coerce', dayfirst=True)
    df = df.dropna(subset=)

    return df

data = load_data()

# --- 3. DASHBOARD TITLE AND OVERVIEW ---
st.title("OpenAIPerovskite Dashboard: 2D Perovskite Efficiency Analysis")
st.markdown("---")

if data.empty:
    st.stop()

st.header("Overview of Power Conversion Efficiency (PCE)")
st.metric(
    label="Maximum PCE Recorded (2016–2025)", 
    value=f"{data['PCE_Clean'].max():.2f} %", 
    delta=f"Median PCE: {data['PCE_Clean'].median():.2f} %"
)

# --- 4. INTERACTIVE FILTERS (SIDEBAR) ---
st.sidebar.header("Data Filters")

# Filter 1: PCE Range
pce_min, pce_max = data['PCE_Clean'].min(), data['PCE_Clean'].max()
pce_range = st.sidebar.slider(
    'Filter PCE (%) Range',
    min_value=float(pce_min),
    max_value=float(pce_max),
    value=(float(pce_min), float(pce_max)),
    step=0.1
)

# Filter 2: Publication Year
min_year = data.dt.year.min()
max_year = data.dt.year.max()
year_range = st.sidebar.slider(
    'Filter Publication Year',
    min_value=int(min_year),
    max_value=int(max_year),
    value=(int(min_year), int(max_year)),
    step=1
)

# Apply filters
filtered_data = data[
    (data['PCE_Clean'] >= pce_range) & 
    (data['PCE_Clean'] <= pce_range[1]) &
    (data.dt.year >= year_range) &
    (data.dt.year <= year_range[1])
]

st.sidebar.info(f"Showing {len(filtered_data)} of {len(data)} total records.")

# --- 5. VISUALIZATIONS ---

# VIZ 1: PCE Distribution (Histogram)
st.subheader("PCE Distribution by Count")
fig_hist = px.histogram(
    filtered_data, 
    x='PCE_Clean', 
    nbins=30, 
    title='Distribution of PCE (%) in 2D Perovskite Devices',
    color_discrete_sequence=
)
fig_hist.update_layout(xaxis_title="Power Conversion Efficiency (PCE) %", yaxis_title="Number of Devices")
st.plotly_chart(fig_hist, use_container_width=True)


# VIZ 2: Performance Over Time (Scatter Plot)
st.subheader("PCE Trend Over Time")
fig_time = px.scatter(
    filtered_data,
    x='Publication_Date', 
    y='PCE_Clean', 
    color='PCE_Clean',
    size='Perovskite_Thickness_nm', # Use a key metric for size
    hover_data=,
    title='PCE (%) vs. Publication Date (Size by Thickness)',
    color_continuous_scale=px.colors.sequential.Sunset
)
fig_time.update_layout(xaxis_title="Publication Date (2016–2025)", yaxis_title="PCE (%)")
st.plotly_chart(fig_time, use_container_width=True)

# VIZ 3: Performance Breakdown by Categorical Factor (Metal)
st.subheader("PCE Breakdown by Metal Cation")
metal_data = filtered_data.groupby('Metal')['PCE_Clean'].agg(['count', 'mean', 'max']).reset_index()
metal_data = metal_data.sort_values(by='mean', ascending=False)

fig_metal = px.bar(
    metal_data,
    x='Metal',
    y='mean',
    error_y=None,  # No standard deviation is calculated yet, keep simple mean
    title='Average PCE (%) by Metal Cation (Pb vs Sn)',
    hover_data={'count': True, 'max': True},
    color='mean',
    color_continuous_scale=px.colors.sequential.Plasma
)
fig_metal.update_layout(xaxis_title="Metal Cation (B-site)", yaxis_title="Average PCE (%)")
st.plotly_chart(fig_metal, use_container_width=True)


# --- 6. RAW DATA TABLE ---
st.subheader("Raw Filtered Data")
# Display relevant columns for quick reference
display_cols =
st.dataframe(filtered_data[display_cols].rename(columns={'PCE_Clean': 'PCE (%)', 'DOI_Number': 'DOI'}), use_container_width=True)


