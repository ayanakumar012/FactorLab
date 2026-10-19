"""Optional Phase 2 Streamlit app. Run: streamlit run app.py"""
import streamlit as st
import plotly.express as px
from src.data import fetch_french_monthly, fetch_cpi, prepare_data
from src.analysis import summary_table, contrast_table, interpretation_warning

st.set_page_config(page_title='FactorLab', layout='wide')
st.title('FactorLab')
st.subheader('Does inflation change which types of stocks perform best?')
st.caption('Historical U.S. stock portfolios by size and value; research, not investment advice.')
threshold = st.slider('High-inflation threshold (year-over-year CPI, %)', 1.0, 8.0, 3.0, 0.5)
start = st.selectbox(
    "Start year",
    list(range(1990, 2027)),
    index=10
)

@st.cache_data(ttl=86400)
def download():
    return fetch_french_monthly(), fetch_cpi()

try:
    ret, cpi = download()
    df = prepare_data(ret, cpi, start=f'{start}-01', threshold=threshold)
    summary = summary_table(df)
    contrast = contrast_table(summary)
    st.info(f'Sample: {df.index.min()} through {df.index.max()} · {len(df)} months · '
            f"high inflation: {(df.regime == 'High inflation').sum()} months")
    fig = px.bar(summary, x='portfolio', y='average_monthly_return_pct', color='regime',
                 barmode='group', title='Average monthly return (%) by inflation regime')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(contrast.round(3), use_container_width=True)
st.download_button('Download comparison CSV', contrast.to_csv(index=False), 'factorlab_comparison.csv', 'text/csv')
    st.warning(interpretation_warning())
except Exception as exc:
    st.error(f'Unable to run AlphaLens: {exc}')
    st.info('Check your internet connection and whether the public data source URLs are available.')
