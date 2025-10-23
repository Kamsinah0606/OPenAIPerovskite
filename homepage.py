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

    # >>> FIX FOR VALUEERROR: Clean and convert Thickness column <<<
    if 'Perovskite_Thickness_nm' in df.columns:
        # Remove non-digit/non-dot characters (like 'nm', 'approx', ranges) and convert to float
        df['Thickness_Clean'] = df['Perovskite_Thickness_nm'].astype(str).str.replace(r'[^\d\.]', '', regex=True).str.strip()
        df['Thickness_Clean'] = pd.to_numeric(df['Thickness_Clean'], errors='coerce')
        # Drop rows where Thickness_Clean is NaN, as the scatter plot size requires numeric data
        df = df[df['Thickness_Clean'].notna()].copy() 
    else:
        st.warning("Column 'Perovskite_Thickness_nm' not found. Scatter plot size will be constant.")
        df['Thickness_Clean'] = 1 # Constant size if column is missing

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

# VIZ 2: Performance Over Time (Scatter Plot)
st.subheader("PCE Trend Over Time")
# Only plot if we have a valid date column
if not filtered_data['Publication_Date'].isnull().all() and not filtered_data['Thickness_Clean'].isnull().all():
    fig_time = px.scatter(
        filtered_data,
        x='Publication_Date', 
        y='PCE_Clean', 
        color='PCE_Clean',
        # FIX: Using the cleaned numeric column for size
        size='Thickness_Clean', 
        # FIX: Updated hover data to use the cleaned thickness column
        hover_data=['PCE_Clean', 'Metal', 'Long_Organic_Cation', 'Thickness_Clean'], 
        title='PCE (%) vs. Publication Date (Size by Thickness)',
        color_continuous_scale=px.colors.sequential.Sunset
    )
    fig_time.update_layout(xaxis_title="Publication Date (2016–2025)", yaxis_title="PCE (%)")
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.warning("Cannot plot PCE Trend Over Time as 'Publication_Date' or 'Perovskite_Thickness_nm' data is missing or invalid.")

st.markdown("---")

# VIZ 3: Performance Breakdown by Categorical Factor (Metal)
st.subheader("PCE Breakdown by Metal Cation")
# Check if 'Metal' column exists and has data
if 'Metal' in filtered_data.columns and not filtered_data['Metal'].empty:
    metal_data = filtered_data.groupby('Metal')['PCE_Clean'].agg(['count', 'mean', 'max']).reset_index()
    metal_data = metal_data.sort_values(by='mean', ascending=False)

    fig_metal = px.bar(
        metal_data,
        x='Metal',
        y='mean',
        title='Average PCE (%) by Metal Cation (B-site)',
        hover_data={'count': True, 'max': True},
        color='mean',
        color_continuous_scale=px.colors.sequential.Plasma
    )
    fig_metal.update_layout(xaxis_title="Metal Cation (B-site)", yaxis_title="Average PCE (%)")
    st.plotly_chart(fig_metal, use_container_width=True)
else:
    st.warning("The 'Metal' column is not available or is empty in the filtered data. Cannot display Metal Cation breakdown.")

st.markdown("---")

# --- 6. RAW DATA TABLE ---
st.subheader("Raw Filtered Data")
# Added Thickness_Clean to display columns
display_cols_required = ['PCE_Clean', 'Metal', 'Long_Organic_Cation', 'Thickness_Clean', 'DOI_Number'] 
# Filter the list to only include columns that exist in the DataFrame
display_cols = [col for col in display_cols_required if col in filtered_data.columns]

st.dataframe(filtered_data[display_cols].rename(columns={'PCE_Clean': 'PCE (%)', 'DOI_Number': 'DOI', 'Thickness_Clean': 'Thickness (nm)'}), use_container_width=True)
