import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fund Portfolio", page_icon="📊", layout="wide")

st.title("Fund Portfolio Analysis")
st.subheader("Geographic and Sector Distribution")

# Load data
try:
    df = pd.read_excel('Funds.csv')
    df_clean = df[df['Amount Committed'].notna()]
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Committed", f"${df_clean['Amount Committed'].sum()/1_000_000:.1f}M")
    with col2:
        st.metric("Active Funds", len(df_clean))
    with col3:
        st.metric("Pending Investment", len(df[df['Amount Committed'].isna()]))
    
    st.markdown("---")
    
    # Geography breakdown
    st.subheader("Investment by Geography")
    geo_summary = df_clean.groupby('Geography')['Amount Committed'].agg(['sum', 'count'])
    geo_summary.columns = ['Total Investment', 'Number of Funds']
    geo_summary['Total Investment'] = geo_summary['Total Investment'].apply(lambda x: f"${x/1_000_000:.1f}M")
    st.dataframe(geo_summary)
    
    # Sector breakdown
    st.subheader("Investment by Sector")
    sector_summary = df_clean.groupby('Fund Sector')['Amount Committed'].agg(['sum', 'count'])
    sector_summary.columns = ['Total Investment', 'Number of Funds']
    sector_summary['Total Investment'] = sector_summary['Total Investment'].apply(lambda x: f"${x/1_000_000:.1f}M")
    st.dataframe(sector_summary)
    
    # Key insight
    st.markdown("---")
    st.info("""
    **Key Finding from the data:**
    - **US/Canada**: Predominantly specialist funds (Education/FoW, Health, Climate)
    - **LATAM + Brazil**: Predominantly generalist funds (Multisector)
    
    → As noted: "If you want to invest in LATAM funds, it's not going to be a bullseye on your preferred sector 100% of the time"
    """)
    
    # Show raw data
    with st.expander("View Raw Data"):
        st.dataframe(df_clean)
        
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please ensure 'Funds.xlsx' is in the repository")

