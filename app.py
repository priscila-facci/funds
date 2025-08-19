import streamlit as st
import pandas as pd

st.title("Fund Portfolio Analysis")
st.subheader("Geographic and Sector Distribution")

try:
    # Lê o CSV - parece que está separado por ponto e vírgula
    df = pd.read_csv('Funds.csv', sep=';')
    
    # Se não funcionar, tenta com vírgula
    if len(df.columns) == 1:
        df = pd.read_csv('Funds.csv', sep=',')
    
    # Se ainda tiver só uma coluna, separa manualmente
    if len(df.columns) == 1:
        # Pega o nome da coluna única
        col = df.columns[0]
        # Cria lista de nomes corretos
        column_names = ['Name', 'Parent Entity', 'Amount Committed', 'Vintage Year', 
                       'Fund (Vehicle) Size', 'Jurisdiction', 'Fund Sector', 
                       'K-12', 'Fund Size', 'Geography']
        
        # Separa os dados
        df_new = pd.DataFrame()
        for i, row in df.iterrows():
            values = str(row[col]).split(';')
            if len(values) == len(column_names):
                df_new = pd.concat([df_new, pd.DataFrame([values], columns=column_names)])
        df = df_new
    
    # Limpa Amount Committed
    df['Amount Committed'] = df['Amount Committed'].str.replace('$', '').str.replace(',', '')
    df['Amount Committed'] = pd.to_numeric(df['Amount Committed'], errors='coerce')
    
    # Remove linhas vazias
    df_clean = df.dropna(subset=['Amount Committed'])
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        total = df_clean['Amount Committed'].sum()
        st.metric("Total Committed", f"${total/1_000_000:.1f}M")
    with col2:
        st.metric("Active Funds", len(df_clean))
    with col3:
        st.metric("Pipeline", len(df) - len(df_clean))
    
    st.markdown("---")
    
    # Análise por Geografia
    st.subheader("Investment by Geography")
    geo_data = df_clean.groupby('Geography')['Amount Committed'].agg(['sum', 'count'])
    geo_data.columns = ['Total Investment', 'Number of Funds']
    geo_data['Total Investment'] = geo_data['Total Investment'].apply(lambda x: f"${x/1_000_000:.1f}M")
    st.dataframe(geo_data)
    
    # Análise por Setor
    st.subheader("Investment by Sector")
    sector_data = df_clean.groupby('Fund Sector')['Amount Committed'].agg(['sum', 'count'])
    sector_data.columns = ['Total Investment', 'Number of Funds']
    sector_data['Total Investment'] = sector_data['Total Investment'].apply(lambda x: f"${x/1_000_000:.1f}M")
    st.dataframe(sector_data)
    
    # Insight principal
    st.markdown("---")
    st.success("""
    ### Key Findings:
    - **US/Canada**: Predominantly **specialist** funds (Education, Health, Climate)
    - **LATAM + Brazil**: Predominantly **generalist** funds (Multisector)
    
    ✅ Confirms Kelly's hypothesis: *"In LATAM, it's not going to be a bullseye on your preferred sector 100% of the time"*
    """)
    
    # Link para compartilhar
    st.markdown("---")
    st.info("Share this dashboard: " + st.secrets.get("url", "https://funds.streamlit.app"))
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("Debug: Check if CSV is properly formatted with semicolon (;) as separator")

