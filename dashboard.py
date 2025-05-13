import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Bangweulu GMA Dashboard", layout="wide")

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["Interactive Map", "NDVI Charts", "Documentation"])

# **Tab 1: Interactive Map**
with tab1:
    st.header("Forage Analysis Map")

    # Embed the interactive map from Google Drive (replace with your public URL)
    map_url = "https://drive.google.com/uc?id=1EXQ8XAUNI1dexVMj15oQF0OqSOnQzyKH"
    st.markdown(
        f'<iframe src="{map_url}" width="100%" height="600px" style="border:none;"></iframe>',
        unsafe_allow_html=True
    )

# **Tab 2: NDVI Time Series Charts**
with tab2:
    st.header("NDVI Time Series Charts")

    def plot_ndvi(csv_filename, title):
        csv_path = os.path.join("assets", csv_filename)

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date'])

            col1, _ = st.columns([3, 2])
            with col1:
                fig, ax = plt.subplots(figsize=(10, 4))
                for uai in df['UAI'].unique():
                    subset = df[df['UAI'] == uai]
                    ax.plot(subset['Date'], subset['NDVI'], marker='o', label=uai, linewidth=1.5)

                ax.set_title(title, fontsize=10)
                ax.set_xlabel("Date", fontsize=9)
                ax.set_ylabel("NDVI", fontsize=9)
                ax.tick_params(axis='both', labelsize=8)
                ax.legend(fontsize=7, ncol=2, loc='upper right')
                ax.grid(True)
                st.pyplot(fig)
        else:
            st.warning(f"⚠️ {title} data is unavailable.")

    # Render only available CSVs
    plot_ndvi("Bangweulu_MODIS_NDVI_TimeSeries_UAIs.csv", "UAI NDVI - MODIS")
    plot_ndvi("Bangweulu_VIIRS_NDVI_TimeSeries_UAIs.csv", "UAI NDVI - VIIRS")
    plot_ndvi("Bangweulu_MODIS_NDVI_TimeSeries_MCDA_UAIs.csv", "MCDA NDVI - MODIS")
    plot_ndvi("Bangweulu_VIIRS_NDVI_TimeSeries_MCDA_UAIs.csv", "MCDA NDVI - VIIRS")

# **Tab 3: Documentation**
with tab3:
    st.header("Workflow Documentation")
    st.markdown("""
    ### Workflow Overview
    This document outlines the geospatial workflow developed to generate edible vegetation masks 
    and segment Unit Areas of Insurance (UAIs) using satellite-derived vegetation indices.
    
    **Troubleshooting:**
    - If the map doesn’t load, verify the Google Drive link.
    - Ensure all CSV files are present in the `assets/` folder.
    """)