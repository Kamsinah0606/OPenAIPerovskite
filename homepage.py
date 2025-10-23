import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="2D Perovskite PCE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("OPenAIPerovskite", divider="gray")

# Defined URL to load the data from GitHub
URL = 'https://raw.githubusercontent.com/Kamsinah0606/OPenAIPerovskite/refs/heads/research/Dataset%202D%20Perovskite%20(2016-2025)%20-%20Mixed.csv'

# --- 2. DATA LOADING AND CLEANING ---
@st.cache_data
def load_data():
    """Loads and cleans the 2D Perovskite dataset."""
    
    # Use the defined URL to load the data
    try:
        df = pd.read_csv(URL) 
    except Exception as e:
        st.error(f"Error loading data from URL. Please check the link and internet connection. Error: {e}")
        return pd.DataFrame() 

    # Normalize column names for easier access
    df.columns = df.columns.str.replace(' ', '_').str.replace('%', 'pct').str.replace('(', '').str.replace(')', '', regex=False)
    
    # Clean up non-numeric data in the PCE column
    df['PCEpct'] = df['PCEpct'].astype(str).str.replace('$', '', regex=False).str.strip()
    
    # Convert PCE to float. Errors are coerced to NaN (Missing Data)
    df['PCE_Clean'] = pd.to_numeric(df['PCEpct'], errors='coerce')
    
    # Filter out rows where PCE is missing or unreasonably low
    df = df.dropna(subset=['PCE_Clean'])
    df = df[df['PCE_Clean'] > 0.1].copy()

    # >>> NEW CLEANING STEP FOR THICKNESS <<<
    if 'Perovskite_Thickness_nm' in df.columns:
        # Clean thickness column: convert to string, remove non-numeric artifacts, then coerce to float.
        df['Thickness_Clean'] = df['Perovskite_Thickness_nm'].astype(str).str.replace(r'[^\d\.]', '', regex=True).str.strip()
        df['Thickness_Clean'] = pd.to_numeric(df['Thickness_Clean'], errors='coerce')
        # Use a reasonable minimum filter if necessary, or just drop NaNs for the plot
        df = df[df['Thickness_Clean'].notna()].copy() 
    else:
        st.warning("Column 'Perovskite_Thickness_nm' not found. Scatter plot size will be disabled.")
        df['Thickness_Clean'] = 1 # Set to a non-zero constant to prevent errors if used later

    # Convert Publication Date to datetime object
    # ASSUMPTION: The column containing dates is named 'Publication_Date'
    if 'Publication_Date' in df.columns:
        df['Publication_Date'] = pd.to_datetime(df['Publication_Date'], errors='coerce', dayfirst=True)
        # Drop rows where the date conversion failed
        df = df.dropna(subset=['Publication_Date']).copy() 
    else:
        st.warning("Column 'Publication_Date' not found. Time-based filters/plots will be skipped.")
        df['Publication_Date'] = pd.NaT 

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
# Check if the date column exists and is populated before setting year filters
if not data['Publication_Date'].isnull().all():
    min_year = data['Publication_Date'].dt.year.min()
    max_year = data['Publication_Date'].dt.year.max()
    year_range = st.sidebar.slider(
        'Filter Publication Year',
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year)),
        step=1
    )
    # Year filter condition
    year_filter = (data['Publication_Date'].dt.year >= year_range[0]) & \
                  (data['Publication_Date'].dt.year <= year_range[1])
else:
    # If no date column, bypass the year filter
    year_filter = True

# Apply filters
filtered_data = data[
    (data['PCE_Clean'] >= pce_range[0]) & 
    (data['PCE_Clean'] <= pce_range[1]) &
    year_filter
].copy() # Ensure we're working on a copy

st.sidebar.info(f"Showing **{len(filtered_data)}** of **{len(data)}** total records.")

# --- 5. VISUALIZATIONS ---

# VIZ 1: PCE Distribution (Histogram)
st.subheader("PCE Distribution by Count")
fig_hist = px.histogram(
    filtered_data, 
    x='PCE_Clean', 
    nbins=30, 
    title='Distribution of PCE (%) in 2D Perovskite Devices',
    color_discrete_sequence=['#636EFA'] 
)
fig_hist.update_layout(xaxis_title="Power Conversion Efficiency (PCE) %", yaxis_title="Number of Devices")
st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# --- 6. RAW DATA TABLE ---
st.subheader("Raw Filtered Data")
# Added Thickness_Clean to display columns
display_cols_required = ['PCE_Clean', 'Metal', 'Long_Organic_Cation', 'Thickness_Clean', 'DOI_Number'] 
# Filter the list to only include columns that exist in the DataFrame
display_cols = [col for col in display_cols_required if col in filtered_data.columns]

st.dataframe(filtered_data[display_cols].rename(columns={'PCE_Clean': 'PCE (%)', 'DOI_Number': 'DOI', 'Thickness_Clean': 'Thickness (nm)'}), use_container_width=True)
