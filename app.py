import streamlit as st
import pandas as pd

st.title("Fund Portfolio Analysis")
st.subheader("Geographic and Sector Distribution")

try:
    # Tenta ler o CSV
    df = pd.read_csv('Funds.csv')
    
    # Remove linhas com valores vazios
    df_clean = df.dropna(subset=['Amount Committed'])
    
    # Mostra métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Committed", f"${df_clean['Amount Committed'].sum()/1_000_000:.1f}M")
    with col2:
        st.metric("Active Funds", len(df_clean))
    with col3:
        st.metric("Not Invested Yet", len(df) - len(df_clean))
    
    st.markdown("---")
    
    # Tabela por Geografia
    st.subheader("By Geography")
    geo = df_clean.groupby('Geography')['Amount Committed'].agg(['sum', 'count'])
    geo.columns = ['Total ($)', 'Count']
    st.dataframe(geo)
    
    # Tabela por Setor
    st.subheader("By Sector")
    sector = df_clean.groupby('Fund Sector')['Amount Committed'].agg(['sum', 'count'])
    sector.columns = ['Total ($)', 'Count']
    st.dataframe(sector)
    
    # Insight principal
    st.info("""
    **Key Finding:**
    - US: Specialist funds
    - LATAM + Brazil: Generalist funds (Multisector)
    """)
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("Files in repository:", pd.DataFrame({'file': ['Funds.csv', 'app.py', 'requirements.txt']}))



