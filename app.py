import streamlit as st
import pandas as pd

st.title("Fund Portfolio Analysis")

try:
    # Lê o CSV
    df = pd.read_csv('Funds.csv')
    
    # Mostra informações básicas
    st.write(f"Total de linhas: {len(df)}")
    st.write(f"Colunas: {list(df.columns)}")
    
    # Mostra os dados
    st.dataframe(df)
    
except Exception as e:
    st.error(f"Erro: {str(e)}")

