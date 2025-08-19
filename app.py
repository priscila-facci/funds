import streamlit as st
import pandas as pd

st.title("Fund Portfolio Analysis")
st.subheader("Tree Map: Sector + Geography")

try:
    # Lê o CSV
    df = pd.read_csv('Funds.csv', sep=';')
    
    # Se não funcionar, tenta outros separadores
    if len(df.columns) == 1:
        # Tenta identificar o separador correto
        first_row = df.iloc[0].values[0]
        if ':' in str(first_row):
            df = pd.read_csv('Funds.csv', sep=':')
        elif ',' in str(first_row):
            df = pd.read_csv('Funds.csv', sep=',')
    
    # Se ainda tiver problema, separa manualmente
    if len(df.columns) == 1:
        col = df.columns[0]
        column_names = ['Name', 'Parent Entity', 'Amount Committed', 'Vintage Year', 
                       'Fund (Vehicle) Size', 'Jurisdiction', 'Fund Sector', 
                       'K-12', 'Fund Size', 'Geography']
        df[column_names] = df[col].str.split(';', expand=True)
        df = df[column_names]
    
    # Limpa Amount Committed
    df['Amount Committed'] = df['Amount Committed'].str.replace('$', '').str.replace(',', '')
    df['Amount Committed'] = pd.to_numeric(df['Amount Committed'], errors='coerce')
    
    # Remove vazios
    df_clean = df.dropna(subset=['Amount Committed'])
    
    # TREE MAP VISUAL usando métricas do Streamlit
    st.markdown("### 🌳 Tree Map Visualization")
    
    # Agrupa por Geografia
    geo_groups = df_clean.groupby('Geography').agg({
        'Amount Committed': 'sum',
        'Fund Sector': lambda x: x.value_counts().to_dict()
    })
    
    # Cores para cada geografia
    colors = {
        'US+Canada': '🔵',
        'LATAM (excl. Brazil)': '🔴', 
        'Brazil': '🟠',
        'Emerging Markets (Global)': '🟣',
        'Europe': '🟢'
    }
    
    # Cria colunas para o tree map visual
    cols = st.columns(len(geo_groups))
    
    for i, (geo, data) in enumerate(geo_groups.iterrows()):
        with cols[i]:
            # Box principal por geografia
            total = data['Amount Committed']
            emoji = colors.get(geo, '⚪')
            
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 5px;'>
                <h3>{emoji} {geo}</h3>
                <h2>${total/1_000_000:.1f}M</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Sub-boxes por setor
            sectors = data['Fund Sector']
            for sector, count in sectors.items():
                sector_total = df_clean[(df_clean['Geography'] == geo) & 
                                       (df_clean['Fund Sector'] == sector)]['Amount Committed'].sum()
                
                # Tamanho do box baseado no valor
                size = min(100, max(50, int(sector_total/total * 200)))
                
                st.markdown(f"""
                <div style='background-color: #e0e0e0; padding: 10px; border-radius: 5px; 
                            margin: 5px 0; font-size: {size}%;'>
                    <b>{sector}</b><br>
                    ${sector_total/1_000_000:.1f}M ({count} funds)
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Métricas resumidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Portfolio", f"${df_clean['Amount Committed'].sum()/1_000_000:.1f}M")
    with col2:
        st.metric("Active Funds", len(df_clean))
    with col3:
        st.metric("Average Ticket", f"${df_clean['Amount Committed'].mean()/1_000_000:.1f}M")
    
    # Tabela detalhada
    st.markdown("### 📊 Detailed Analysis")
    
    # Por Geografia
    tab1, tab2 = st.tabs(["By Geography", "By Sector"])
    
    with tab1:
        geo_summary = df_clean.groupby('Geography').agg({
            'Amount Committed': ['sum', 'count', 'mean']
        })
        geo_summary.columns = ['Total', 'Count', 'Average']
        geo_summary['Total'] = geo_summary['Total'].apply(lambda x: f"${x/1_000_000:.1f}M")
        geo_summary['Average'] = geo_summary['Average'].apply(lambda x: f"${x/1_000_000:.1f}M")
        st.dataframe(geo_summary)
    
    with tab2:
        sector_summary = df_clean.groupby('Fund Sector').agg({
            'Amount Committed': ['sum', 'count']
        })
        sector_summary.columns = ['Total', 'Count']
        sector_summary['Percentage'] = (sector_summary['Total'] / sector_summary['Total'].sum() * 100).round(1)
        sector_summary['Total'] = sector_summary['Total'].apply(lambda x: f"${x/1_000_000:.1f}M")
        st.dataframe(sector_summary)
    
    # Insight principal
    st.markdown("---")
    st.success("""
    ### 🎯 Key Finding - Exactly as Kelly noted:
    
    - **US/Canada**: Specialist funds dominate (Education, Health, Climate)
    - **LATAM + Brazil**: Generalist funds dominate (Multisector)
    
    ✅ *"If you want to invest in LATAM funds, it's not going to be a bullseye on your preferred sector 100% of the time"*
    """)
    
except Exception as e:
    st.error(f"Error: {str(e)}")

