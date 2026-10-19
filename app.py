"""FactorLab Streamlit application. Deploy app.py from GitHub on Streamlit Community Cloud."""
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data import PORTFOLIOS, fetch_french_monthly, fetch_cpi, prepare_data
from src.analysis import summary_table, contrast_table, interpretation_warning
from src.factors import FACTOR_NAMES, fetch_five_factors, fit_factor_model

st.set_page_config(page_title='FactorLab | Equity Research', layout='wide')
st.title('FactorLab')
st.subheader('Does inflation change which types of stocks perform best?')
st.caption('Explore historical U.S. size/value research portfolios. Descriptive research, not investment advice.')

@st.cache_data(ttl=86400)
def download_returns_and_cpi():
    return fetch_french_monthly(), fetch_cpi()

@st.cache_data(ttl=86400)
def download_factors():
    return fetch_five_factors()

try:
    returns, cpi = download_returns_and_cpi()
    year_options = list(range(1990, min(returns.index.max().year, cpi.index.max().year) + 1))
    if not year_options:
        raise ValueError('No eligible starting years in data.')
    col1, col2 = st.columns(2)
    with col1:
        start_year = st.selectbox('Start year', year_options, index=year_options.index(2000) if 2000 in year_options else 0)
    with col2:
        threshold = st.slider('High inflation if lagged annual CPI inflation exceeds (%)', 1.0, 8.0, 3.0, 0.5)

    df = prepare_data(returns, cpi, start=f'{start_year}-01', threshold=threshold)
    st.info(f'Sample: {df.index.min()} through {df.index.max()} · {len(df)} months · '
            f"high inflation: {(df['regime'] == 'High inflation').sum()} months")
    tab1, tab2, tab3 = st.tabs(['Compare stock groups', 'Five-factor regression', 'About the research'])
    with tab1:
        summary = summary_table(df)
        contrast = contrast_table(summary)
        figure = px.bar(summary, x='portfolio', y='average_monthly_return_pct', color='regime', barmode='group',
                        title='Average monthly returns by inflation regime', labels={'average_monthly_return_pct': 'Average return (% per month)', 'portfolio': 'Stock group'})
        st.plotly_chart(figure, use_container_width=True)
        st.dataframe(contrast.round(3), use_container_width=True, hide_index=True)
        st.download_button('Download comparison CSV', contrast.to_csv(index=False).encode('utf-8'), 'factorlab_comparison.csv', 'text/csv')
        st.warning(interpretation_warning())
    with tab2:
        st.markdown('### What helps explain a stock group’s returns?')
        st.write('The Fama–French five-factor regression measures how a portfolio’s *historical* excess returns move with common market factors. It does not predict future returns.')
        selected = st.selectbox('Choose a stock group', PORTFOLIOS)
        selected_regime = st.selectbox('Choose inflation environment', ['All months', 'High inflation', 'Low inflation'])
        with st.spinner('Loading monthly factor returns...'):
            factors = download_factors()
        aligned = df.join(factors, how='inner')
        model, coeff_table, n_months = fit_factor_model(aligned, selected, selected_regime)
        a, b, c = st.columns(3)
        a.metric('Months analyzed', str(n_months))
        b.metric('R² (in sample)', f'{model.rsquared:.1%}')
        c.metric('Monthly alpha', f'{model.params["const"]:.3f}%')
        chart_data = coeff_table.loc[coeff_table.factor.isin(FACTOR_NAMES)]
        figure = px.bar(chart_data, x='factor', y='coefficient', title=f'{selected}: estimated factor exposures',
                        labels={'factor': 'Factor', 'coefficient': 'Coefficient'})
        st.plotly_chart(figure, use_container_width=True)
        st.dataframe(coeff_table.round(4), use_container_width=True, hide_index=True)
        st.download_button('Download regression CSV', coeff_table.to_csv(index=False).encode('utf-8'), 'factorlab_factor_regression.csv', 'text/csv')
        st.caption('Model: monthly portfolio return minus risk-free rate regressed on market, size, value, profitability, and investment factors with an intercept. Monthly returns and factor values are in percentage points. Standard errors use HAC with 3 lags. A portfolio’s exposure to its defining size/value factors is partly expected by construction.')
        st.warning('Comparing coefficients across separate regimes does not, by itself, establish statistically significant differences. This screen reports separate historical fits; interaction tests and robustness checks are future work.')
    with tab3:
        st.markdown('### The research question')
        st.write('Does inflation change which types of U.S. stocks perform best? The six portfolios are grouped by company size and book-to-market valuation, not six individual companies.')
        st.markdown('### Data and interpretation')
        st.write('Portfolio returns and five factors: Kenneth French Data Library. Inflation: FRED CPIAUCSL. High inflation is defined with a configurable threshold and inflation lagged two months as a conservative publication-delay approximation. CPI uses a revised series, not real-time vintages.')
        st.write('Historical associations do not prove inflation caused performance differences. The six portfolios may overlap with the portfolios used to build the explanatory factors. The application is an exploratory research tool, not a trading recommendation.')
except Exception as exc:
    st.error(f'Unable to run FactorLab: {exc}')
    st.info('Try a longer date window or check whether the public research datasets are available.')
