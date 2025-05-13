import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objs as go

# Set page configuration
st.set_page_config(page_title="Bangweulu GMA Dashboard", layout="wide")

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["Interactive Map", "NDVI Charts", "Documentation"])

with tab1:
    st.header("Forage Analysis Map")

    # **Using the Vercel-hosted map instead of a local HTML file**
    map_url = "https://acre-map.vercel.app/"
    st.markdown(
        f'<iframe src="{map_url}" width="100%" height="600px" style="border:none;"></iframe>',
        unsafe_allow_html=True
    )

with tab2:
    st.header("NDVI Time Series Charts")

    def plot_ndvi_interactive(csv_filename, title):
        csv_path = os.path.join("assets", csv_filename)

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)

            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)

            start_date = df['Date'].min().to_pydatetime()
            end_date = df['Date'].max().to_pydatetime()

            date_range = st.slider(
                f"Date Range for {title}",
                min_value=start_date,
                max_value=end_date,
                value=(start_date, end_date),
                format="YYYY-MM"
            )

            filtered_df = df[
                (df['Date'] >= pd.to_datetime(date_range[0])) & 
                (df['Date'] <= pd.to_datetime(date_range[1]))
            ]

            col1, _ = st.columns([3, 2])  # 60% width plot
            with col1:
                fig, ax = plt.subplots(figsize=(10, 4))
                for uai in filtered_df['UAI'].unique():
                    subset = filtered_df[filtered_df['UAI'] == uai]
                    ax.plot(subset['Date'], subset['NDVI'], marker='o', label=uai, linewidth=1.5)

                ax.set_title(title, fontsize=10)
                ax.set_xlabel("Date", fontsize=9)
                ax.set_ylabel("NDVI", fontsize=9)
                ax.tick_params(axis='both', labelsize=8)
                ax.legend(fontsize=7, ncol=2, loc='upper right')
                ax.grid(True)
                plt.tight_layout()
                st.pyplot(fig)
        else:
            st.warning(f"⚠️ {title} data is unavailable.")

    # Standard NDVI charts
    plot_ndvi_interactive("Bangweulu_MODIS_NDVI_TimeSeries_UAIs.csv", "UAI NDVI - MODIS")
    plot_ndvi_interactive("Bangweulu_VIIRS_NDVI_TimeSeries_UAIs.csv", "UAI NDVI - VIIRS")
    plot_ndvi_interactive("Bangweulu_MODIS_NDVI_TimeSeries_MCDA_UAIs.csv", "MCDA NDVI - MODIS")
    plot_ndvi_interactive("Bangweulu_VIIRS_NDVI_TimeSeries_MCDA_UAIs.csv", "MCDA NDVI - VIIRS")

    # Comparison using Plotly
    st.subheader("Comparison: NDVI-only vs MCDA UAIs (MODIS NDVI)")

    # Load data
    modis_uai_df = pd.read_csv(os.path.join("assets", "Bangweulu_MODIS_NDVI_TimeSeries_UAIs.csv"))
    modis_mcda_df = pd.read_csv(os.path.join("assets", "Bangweulu_MODIS_NDVI_TimeSeries_MCDA_UAIs.csv"))

    modis_uai_df['Date'] = pd.to_datetime(modis_uai_df['Date'], dayfirst=False)
    modis_mcda_df['Date'] = pd.to_datetime(modis_mcda_df['Date'], dayfirst=False)

    # Extract all valid UAI numbers
    uai_ids = sorted(modis_uai_df['UAI'].astype(str).str.extract(r'(\d+)')[0].dropna().astype(int).unique())

    fig = go.Figure()
    colors = ['green', 'blue', 'orange', 'purple', 'brown']

    for i, uai_num in enumerate(uai_ids):
        color = colors[i % len(colors)]
        uai_label = f"UAI {uai_num}"
        mcda_label = f"MCDA UAI {uai_num}"

        # NDVI-only line
        df_ndvi = modis_uai_df[modis_uai_df['UAI'] == uai_label]
        if not df_ndvi.empty:
            fig.add_trace(go.Scatter(
                x=df_ndvi['Date'],
                y=df_ndvi['NDVI'],
                mode='lines+markers',
                name=f"{uai_label} (NDVI-only)",
                line=dict(color=color, dash='dot'),
                hoverinfo='x+y+name'
            ))

        # MCDA line
        df_mcda = modis_mcda_df[modis_mcda_df['UAI'] == mcda_label]
        if not df_mcda.empty:
            fig.add_trace(go.Scatter(
                x=df_mcda['Date'],
                y=df_mcda['NDVI'],
                mode='lines+markers',
                name=f"{uai_label} (MCDA)",
                line=dict(color=color),
                hoverinfo='x+y+name'
            ))

    fig.update_layout(
        title="NDVI-only vs MCDA UAIs (MODIS NDVI, 2020–2024)",
        xaxis_title="Date",
        yaxis_title="Mean NDVI",
        template="plotly_white",
        height=400,
        margin=dict(t=40, l=20, r=20, b=40),
        legend=dict(font=dict(size=10))
    )

    col1, _ = st.columns([3, 2])  # 60% layout
    with col1:
        st.plotly_chart(fig, use_container_width=True)

    st.caption("[Comparison] NDVI-only vs MCDA time series exported: Bangweulu_NDVI_Comparison_NDVI_vs_MCDA.csv")

with tab3:
    st.header("Workflow Documentation")
    st.markdown("""
    ### Workflow Overview
    This document outlines the geospatial workflow developed to generate edible vegetation masks and segment Unit Areas of Insurance (UAIs) using satellite-derived vegetation indices.
    
    **Objective:**  
    To derive an edible vegetation mask and segment the landscape into Unit Areas of Insurance (UAIs) using NDVI and supporting datasets.
    
    **Methodology Steps:**  
    - Load AOI: GMAs  
    - Load MODIS NDVI Data (2020–2024)  
    - Load Sentinel-2 & ESA WorldCover  
    - Extract Monthly NDVI Time Series  
    - Apply Multi-Criteria Decision Analysis (MCDA)  
    - Build Streamlit Dashboard  
    """)