import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Fund Portfolio Tree Map",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("Fund Portfolio Analysis")
st.subheader("Tree Map: Sector + Geography")

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel('Funds.xlsx')
    # Limpar dados - remover linhas com valores vazios nas colunas importantes
    df = df.dropna(subset=['Geography', 'Fund Sector'])
    # Pegar apenas fundos com valores comprometidos
    df = df[df['Amount Committed'].notna()]
    return df

try:
    df = load_data()
    
    # Criar o Tree Map
    fig = px.treemap(
        df,
        path=['Geography', 'Fund Sector'],  # Hierarquia: Geografia -> Setor
        values='Amount Committed',
        title='Investment Distribution by Geography and Sector',
        color='Geography',
        color_discrete_map={
            'US+Canada': '#2E86AB',
            'LATAM (excl. Brazil)': '#A23B72',
            'Brazil': '#F18F01',
            'Emerging Markets (Global)': '#C73E1D',
            'Europe': '#6A994E'
        },
        hover_data={'Amount Committed': ':$,.0f'}
    )
    
    # Ajustar o layout
    fig.update_traces(
        textinfo="label+value+percent parent",
        textfont_size=14
    )
    
    fig.update_layout(
        height=700,
        font=dict(size=14)
    )
    
    # Mostrar o gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise simples embaixo
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Committed", f"${df['Amount Committed'].sum():,.0f}")
        st.metric("Number of Funds", len(df))
    
    with col2:
        # Mostrar a mensagem principal
        st.info("""
        **Key Finding:**
        - **US**: Specialist funds (focused sectors)
        - **LATAM + Brazil**: Mostly generalist funds (Multisector)
        
        → *Not a bullseye on your preferred sector 100% of the time in LATAM*
        """)
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please make sure 'Funds.xlsx' is in the same folder as app.py")