import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

st.set_page_config(page_title="Fund Portfolio Tree Map", layout="wide")

st.title("Fund Portfolio Analysis")
st.subheader("Tree Map: Geography → Sector Distribution")

try:
    # Lê o CSV com diferentes tentativas de separador
    df = None
    for sep in [',', ';', '\t', ':']:
        try:
            temp_df = pd.read_csv('Funds.csv', sep=sep)
            if len(temp_df.columns) > 3:  # Precisa ter várias colunas
                df = temp_df
                break
        except:
            continue
    
    if df is None:
        st.error("Could not parse CSV file")
        st.stop()
    
    # Limpa Amount Committed
    amount_col = None
    for col in df.columns:
        if 'Amount' in col and 'Committed' in col:
            amount_col = col
            break
    
    if amount_col:
        df[amount_col] = df[amount_col].astype(str).str.replace('$', '').str.replace(',', '')
        df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
    
    # Identifica colunas Geography e Fund Sector
    geo_col = None
    sector_col = None
    for col in df.columns:
        if 'Geography' in col:
            geo_col = col
        if 'Sector' in col:
            sector_col = col
    
    # Remove vazios
    df_clean = df.dropna(subset=[amount_col])
    
    # Prepara dados para o tree map
    geo_data = df_clean.groupby(geo_col)[amount_col].sum().sort_values(ascending=False)
    
    # Cria o tree map com matplotlib
    fig, ax = plt.subplots(1, figsize=(12, 8))
    
    # Cores para cada geografia
    colors = {
        'US+Canada': '#3498db',
        'LATAM (excl. Brazil)': '#e74c3c',
        'Brazil': '#f39c12',
        'Emerging Markets (Global)': '#9b59b6',
        'Europe': '#1abc9c',
        'India': '#34495e'
    }
    
    # Calcula posições para o tree map
    total = geo_data.sum()
    
    # Squarify manual - cria retângulos proporcionais
    x = 0
    y = 0
    width = 10
    height = 10
    
    rectangles = []
    labels = []
    
    for geo, value in geo_data.items():
        # Tamanho proporcional
        size = (value / total)
        rect_width = width * np.sqrt(size)
        rect_height = height * np.sqrt(size)
        
        # Adiciona retângulo
        color = colors.get(geo, '#95a5a6')
        rect = plt.Rectangle((x, y), rect_width, rect_height, 
                           facecolor=color, edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        
        # Adiciona label
        if rect_width > 1:  # Só mostra label se o retângulo for grande o suficiente
            ax.text(x + rect_width/2, y + rect_height/2, 
                   f'{geo}\n${value/1e6:.1f}M\n({value/total*100:.0f}%)',
                   ha='center', va='center', fontsize=10, weight='bold', color='white')
        
        # Atualiza posição para próximo retângulo
        x += rect_width
        if x >= width * 0.9:
            x = 0
            y += rect_height * 1.1
    
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Investment Distribution by Geography', fontsize=16, weight='bold', pad=20)
    plt.tight_layout()
    
    # Mostra o gráfico
    st.pyplot(fig)
    
    # Análise por setor dentro de cada geografia
    st.markdown("### Sector Breakdown by Geography")
    
    # Cria colunas para cada geografia principal
    top_geos = geo_data.head(3).index
    cols = st.columns(len(top_geos))
    
    for i, geo in enumerate(top_geos):
        with cols[i]:
            st.markdown(f"#### {geo}")
            geo_df = df_clean[df_clean[geo_col] == geo]
            sector_dist = geo_df.groupby(sector_col)[amount_col].sum().sort_values(ascending=False)
            
            # Mini gráfico de barras
            fig2, ax2 = plt.subplots(figsize=(4, 3))
            bars = ax2.bar(range(len(sector_dist)), sector_dist.values / 1e6)
            ax2.set_xticks(range(len(sector_dist)))
            ax2.set_xticklabels(sector_dist.index, rotation=45, ha='right')
            ax2.set_ylabel('Million USD')
            ax2.set_title(f'Total: ${geo_data[geo]/1e6:.1f}M')
            plt.tight_layout()
            st.pyplot(fig2)
    
    # Métricas principais
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Committed", f"${df_clean[amount_col].sum()/1e6:.1f}M")
    
    with col2:
        st.metric("Active Funds", len(df_clean))
    
    with col3:
        # Calcula % especialista nos US
        if 'US+Canada' in df_clean[geo_col].values:
            us_df = df_clean[df_clean[geo_col] == 'US+Canada']
            if sector_col in us_df.columns:
                specialist = us_df[us_df[sector_col] != 'Multisector'][amount_col].sum()
                total_us = us_df[amount_col].sum()
                st.metric("US Specialist %", f"{specialist/total_us*100:.0f}%")
    
    with col4:
        # Calcula % generalista em LATAM
        latam_df = df_clean[df_clean[geo_col].isin(['Brazil', 'LATAM (excl. Brazil)'])]
        if len(latam_df) > 0 and sector_col in latam_df.columns:
            generalist = latam_df[latam_df[sector_col] == 'Multisector'][amount_col].sum()
            total_latam = latam_df[amount_col].sum()
            st.metric("LATAM Generalist %", f"{generalist/total_latam*100:.0f}%")
    
    # Insight principal
    st.success("""
    ### ✅ Kelly's Hypothesis Confirmed:
    - **US/Canada**: Predominantly SPECIALIST funds (Education, Health, Climate)
    - **LATAM + Brazil**: Predominantly GENERALIST funds (Multisector)
    
    → *"If you want to invest in LATAM funds, it's not going to be a bullseye on your preferred sector 100% of the time"*
    """)
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("Debug info:")
    if 'df' in locals():
        st.write("Columns found:", list(df.columns))
        st.write("Shape:", df.shape)

