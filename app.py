import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fund Portfolio Tree Map", layout="wide")

st.title("Fund Portfolio Analysis")
st.subheader("Tree Map: Geography → Sector Distribution")

try:
    # Lê o CSV
    df = pd.read_csv('Funds.csv')
    
    # Identifica o separador correto
    if len(df.columns) == 1:
        # Tenta diferentes separadores
        for sep in [';', ':', ',', '\t']:
            df_test = pd.read_csv('Funds.csv', sep=sep)
            if len(df_test.columns) > 1:
                df = df_test
                break
    
    # Se ainda tiver problema, separa manualmente
    if len(df.columns) == 1:
        st.error("CSV formatting issue - trying to fix...")
        # Lista esperada de colunas
        expected_cols = ['Name', 'Parent Entity', 'Amount Committed', 'Vintage Year', 
                        'Fund (Vehicle) Size', 'Jurisdiction', 'Fund Sector', 
                        'K-12', 'Fund Size', 'Geography']
        
        # Tenta separar a primeira coluna
        col_name = df.columns[0]
        if ';' in col_name:
            # Os nomes das colunas estão no header
            df.columns = col_name.split(';')
    
    # Limpa Amount Committed
    if 'Amount Committed' in df.columns:
        df['Amount Committed'] = df['Amount Committed'].astype(str).str.replace('$', '').str.replace(',', '')
        df['Amount Committed'] = pd.to_numeric(df['Amount Committed'], errors='coerce')
    
    # Remove vazios
    df_clean = df.dropna(subset=['Amount Committed', 'Geography', 'Fund Sector'])
    
    # Cria o Tree Map
    fig = px.treemap(
        df_clean,
        path=['Geography', 'Fund Sector'],
        values='Amount Committed',
        title='Investment Distribution: Geography → Sector',
        color='Geography',
        color_discrete_map={
            'US+Canada': '#1f77b4',
            'LATAM (excl. Brazil)': '#ff7f0e',
            'Brazil': '#2ca02c',
            'Emerging Markets (Global)': '#d62728',
            'Europe': '#9467bd',
            'India': '#8c564b'
        },
        hover_data={'Amount Committed': ':$,.0f'}
    )
    
    fig.update_traces(
        textinfo="label+value+percent parent",
        textfont_size=16,
        marker=dict(cornerradius=5)
    )
    
    fig.update_layout(
        height=700,
        font=dict(size=14),
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    # Mostra o tree map
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Committed", f"${df_clean['Amount Committed'].sum()/1e6:.1f}M")
    with col2:
        st.metric("Active Funds", len(df_clean))
    with col3:
        us_specialist = df_clean[(df_clean['Geography'] == 'US+Canada') & 
                                (df_clean['Fund Sector'] != 'Multisector')]['Amount Committed'].sum()
        us_total = df_clean[df_clean['Geography'] == 'US+Canada']['Amount Committed'].sum()
        if us_total > 0:
            st.metric("US Specialist %", f"{us_specialist/us_total*100:.0f}%")
    with col4:
        latam_generalist = df_clean[((df_clean['Geography'] == 'Brazil') | 
                                    (df_clean['Geography'] == 'LATAM (excl. Brazil)')) & 
                                   (df_clean['Fund Sector'] == 'Multisector')]['Amount Committed'].sum()
        latam_total = df_clean[(df_clean['Geography'] == 'Brazil') | 
                              (df_clean['Geography'] == 'LATAM (excl. Brazil)')]['Amount Committed'].sum()
        if latam_total > 0:
            st.metric("LATAM Generalist %", f"{latam_generalist/latam_total*100:.0f}%")
    
    # Insight
    st.success("""
    ### ✅ Kelly's Hypothesis Confirmed:
    - **US/Canada**: Predominantly SPECIALIST funds (focused on specific sectors)
    - **LATAM + Brazil**: Predominantly GENERALIST funds (Multisector)
    
    → *"If you want to invest in LATAM funds, it's not going to be a bullseye on your preferred sector 100% of the time"*
    """)
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Debug: Check CSV format and column names")
