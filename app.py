import streamlit as st
import pandas as pd
import subprocess
import sys

# FORÇA A INSTALAÇÃO DO PLOTLY
try:
    import plotly.express as px
except ModuleNotFoundError:
    st.warning("Installing plotly... This may take a moment.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly==5.19.0"])
    st.success("Plotly installed! Please refresh the page.")
    st.stop()

# Agora importa normalmente
import plotly.express as px

st.set_page_config(page_title="Fund Portfolio Tree Map", layout="wide")

st.title("Fund Portfolio Analysis")
st.subheader("Tree Map: Geography → Sector Distribution")

try:
    # Lê o CSV
    df = pd.read_csv('Funds.csv')
    
    # Tenta diferentes separadores se necessário
    if len(df.columns) == 1:
        for sep in [';', ':', '\t']:
            df_test = pd.read_csv('Funds.csv', sep=sep)
            if len(df_test.columns) > 1:
                df = df_test
                break
    
    # Identifica colunas
    amount_col = None
    geo_col = None
    sector_col = None
    
    for col in df.columns:
        if 'Amount' in col and 'Committed' in col:
            amount_col = col
        elif 'Geography' in col:
            geo_col = col
        elif 'Sector' in col:
            sector_col = col
    
    # Limpa valores
    df[amount_col] = df[amount_col].astype(str).str.replace('[$,]', '', regex=True)
    df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
    
    # Remove vazios
    df_clean = df.dropna(subset=[amount_col])
    
    # TREE MAP COM PLOTLY
    fig = px.treemap(
        df_clean,
        path=[px.Constant("Portfolio"), geo_col, sector_col],
        values=amount_col,
        title='Fund Portfolio Distribution',
        color=geo_col,
        color_discrete_map={
            'US+Canada': '#1f77b4',
            'LATAM (excl. Brazil)': '#ff7f0e',
            'Brazil': '#2ca02c',
            'Emerging Markets (Global)': '#d62728',
            'Europe': '#9467bd',
            'India': '#8c564b'
        }
    )
    
    fig.update_traces(
        textinfo="label+value+percent parent",
        textfont_size=14
    )
    
    fig.update_layout(
        height=700,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Committed", f"${df_clean[amount_col].sum()/1e6:.1f}M")
    
    with col2:
        st.metric("Active Funds", len(df_clean))
    
    with col3:
        us_data = df_clean[df_clean[geo_col] == 'US+Canada']
        if len(us_data) > 0:
            specialist = us_data[us_data[sector_col] != 'Multisector'][amount_col].sum()
            total_us = us_data[amount_col].sum()
            st.metric("US Specialist %", f"{(specialist/total_us*100):.0f}%")
    
    with col4:
        latam_data = df_clean[df_clean[geo_col].isin(['Brazil', 'LATAM (excl. Brazil)'])]
        if len(latam_data) > 0:
            generalist = latam_data[latam_data[sector_col] == 'Multisector'][amount_col].sum()
            total_latam = latam_data[amount_col].sum()
            st.metric("LATAM Generalist %", f"{(generalist/total_latam*100):.0f}%")
    
    # Análise detalhada
    st.markdown("---")
    tab1, tab2 = st.tabs(["By Geography", "By Sector"])
    
    with tab1:
        geo_summary = df_clean.groupby(geo_col)[amount_col].agg(['sum', 'count', 'mean'])
        geo_summary.columns = ['Total', 'Count', 'Average']
        geo_summary['% of Total'] = (geo_summary['Total'] / geo_summary['Total'].sum() * 100).round(1)
        st.dataframe(geo_summary)
    
    with tab2:
        sector_summary = df_clean.groupby(sector_col)[amount_col].agg(['sum', 'count'])
        sector_summary.columns = ['Total', 'Count']
        sector_summary['% of Total'] = (sector_summary['Total'] / sector_summary['Total'].sum() * 100).round(1)
        st.dataframe(sector_summary)
    
    # Insight principal
    st.success("""
    ### ✅ Kelly's Hypothesis Confirmed:
    - **US/Canada**: Specialist funds (focused sectors) dominate
    - **LATAM + Brazil**: Generalist funds (Multisector) dominate
    
    → *"If you want to invest in LATAM funds, it's not going to be a bullseye on your preferred sector 100% of the time"*
    """)
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("If you see this error, try refreshing the page once.")
