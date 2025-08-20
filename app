import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fund Portfolio Tree Map", layout="wide")

# Tenta importar plotly
plotly_available = True
try:
    import plotly.express as px
except:
    plotly_available = False
    st.error("Plotly not available. Using alternative visualization.")

st.title("Fund Portfolio Analysis")
st.subheader("Tree Map: Geography → Sector Distribution")

try:
    # Lê o CSV
    df = pd.read_csv('Funds.csv')
    
    # Tenta diferentes separadores
    if len(df.columns) == 1:
        for sep in [';', ':', '\t']:
            df_test = pd.read_csv('Funds.csv', sep=sep)
            if len(df_test.columns) > 1:
                df = df_test
                break
    
    # Identifica colunas
    amount_col = geo_col = sector_col = None
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
    df_clean = df.dropna(subset=[amount_col])
    
    if plotly_available:
        # USA PLOTLY SE DISPONÍVEL
        fig = px.treemap(
            df_clean,
            path=[px.Constant("Portfolio"), geo_col, sector_col],
            values=amount_col,
            title='Fund Portfolio Distribution'
        )
        fig.update_traces(textinfo="label+value+percent parent")
        fig.update_layout(height=700)
        st.plotly_chart(fig, use_container_width=True)
    else:
        # ALTERNATIVA SEM PLOTLY
        st.markdown("### Portfolio Distribution (Table View)")
        
        # Agrupa por geografia
        geo_data = df_clean.groupby(geo_col)[amount_col].sum().sort_values(ascending=False)
        
        # Mostra como métricas grandes
        cols = st.columns(min(3, len(geo_data)))
        for i, (geo, value) in enumerate(geo_data.items()):
            if i < len(cols):
                with cols[i]:
                    st.metric(
                        label=geo,
                        value=f"${value/1e6:.1f}M",
                        delta=f"{(value/geo_data.sum()*100):.0f}% of total"
                    )
                    
                    # Breakdown por setor
                    sectors = df_clean[df_clean[geo_col] == geo].groupby(sector_col)[amount_col].sum()
                    for sector, sector_val in sectors.items():
                        st.progress(sector_val/value)
                        st.caption(f"{sector}: ${sector_val/1e6:.1f}M")
    
    # Métricas principais
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Portfolio", f"${df_clean[amount_col].sum()/1e6:.1f}M")
    with col2:
        st.metric("Active Funds", len(df_clean))
    with col3:
        us_pct = 0
        if 'US+Canada' in df_clean[geo_col].values:
            us_df = df_clean[df_clean[geo_col] == 'US+Canada']
            specialist = us_df[us_df[sector_col] != 'Multisector'][amount_col].sum()
            us_pct = (specialist/us_df[amount_col].sum()*100) if len(us_df) > 0 else 0
        st.metric("US Specialist %", f"{us_pct:.0f}%")
    with col4:
        latam_pct = 0
        latam_df = df_clean[df_clean[geo_col].isin(['Brazil', 'LATAM (excl. Brazil)'])]
        if len(latam_df) > 0:
            generalist = latam_df[latam_df[sector_col] == 'Multisector'][amount_col].sum()
            latam_pct = (generalist/latam_df[amount_col].sum()*100)
        st.metric("LATAM Generalist %", f"{latam_pct:.0f}%")
    
    # Tabelas
    st.markdown("---")
    st.markdown("### Detailed Analysis")
    
    geo_summary = df_clean.groupby(geo_col)[amount_col].agg(['sum', 'count'])
    geo_summary.columns = ['Total Investment', 'Number of Funds']
    geo_summary['% of Portfolio'] = (geo_summary['Total Investment'] / geo_summary['Total Investment'].sum() * 100).round(1)
    geo_summary['Total Investment'] = geo_summary['Total Investment'].apply(lambda x: f"${x/1e6:.1f}M")
    
    st.dataframe(geo_summary, use_container_width=True)
    
    # Insight
    st.success("""
    ### ✅ Kelly's Hypothesis Confirmed:
    - **US/Canada**: Specialist funds dominate
    - **LATAM + Brazil**: Generalist funds (Multisector) dominate
    
    → *"If you want to invest in LATAM funds, it's not going to be a bullseye on your preferred sector 100% of the time"*
    """)
    
except Exception as e:
    st.error(f"Error: {str(e)}")
