"""FactorLab: explanatory historical equity-factor research dashboard."""
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data import PORTFOLIOS, fetch_french_monthly, fetch_cpi, prepare_data
from src.analysis import summary_table, contrast_table, interpretation_warning
from src.factors import FACTOR_NAMES, fetch_five_factors, fit_factor_model

st.set_page_config(page_title='FactorLab | Equity & Inflation Research', layout='wide', page_icon='📊')
st.markdown('''<style>
.block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
h1,h2,h3 {letter-spacing:-0.025em;}
[data-testid="stMetric"] {padding: .9rem 1rem; border: 1px solid rgba(125,125,125,.2); border-radius: 10px;}
</style>''', unsafe_allow_html=True)
st.title('FactorLab')
st.caption('INDEPENDENT EQUITY RESEARCH  /  INFLATION & INVESTMENT STYLES')
st.subheader('Does inflation change which types of stocks perform best?')
st.write('Explore historical returns for six U.S. stock portfolios. Compare the performance first, investigate the risk factors second, and review the research assumptions when you want more detail.')

@st.cache_data(ttl=86400)
def load_returns_cpi():
    return fetch_french_monthly(), fetch_cpi()

@st.cache_data(ttl=86400)
def load_factors():
    return fetch_five_factors()

try:
    returns, cpi = load_returns_cpi()
    latest_year = min(returns.index.max().year, cpi.index.max().year)
    year_options = list(range(1990, latest_year + 1))
    if not year_options:
        raise ValueError('No eligible dates for analysis.')
    with st.sidebar:
        st.header('Research settings')
        start_year = st.selectbox('Start year', year_options, index=year_options.index(2000) if 2000 in year_options else 0)
        threshold = st.slider('High inflation threshold (%)', min_value=1.0, max_value=8.0, value=3.0, step=0.5)
        st.caption('High inflation means available lagged annual CPI inflation is above your chosen threshold. Historical CPI is revised.')
        st.divider()
        st.caption('Sources: Kenneth French Data Library and FRED CPIAUCSL. Educational research; not investment advice.')
    df = prepare_data(returns, cpi, start=f'{start_year}-01', threshold=threshold)
    summary = summary_table(df)
    contrast = contrast_table(summary)
    high = summary.loc[summary.regime.eq('High inflation')].sort_values('average_monthly_return_pct', ascending=False)
    low = summary.loc[summary.regime.eq('Low inflation')].sort_values('average_monthly_return_pct', ascending=False)
    if high.empty or low.empty:
        raise ValueError('Both high- and low-inflation months are needed. Try an earlier start year or another threshold.')
    n_high = int(df.regime.eq('High inflation').sum())
    n_low = int(df.regime.eq('Low inflation').sum())
    st.caption(f'Sample: {df.index.min()}–{df.index.max()}  ·  {len(df)} months  ·  High inflation: {n_high} months  ·  Low inflation: {n_low} months')
    overview, factor_tab, methods = st.tabs(['01  Performance overview', '02  Factor analysis', '03  Research notes'])
    with overview:
        st.markdown('### What happened?')
        m1, m2, m3 = st.columns(3)
        m1.metric('High-inflation leader', high.iloc[0]['portfolio'])
        m2.metric('Low-inflation leader', low.iloc[0]['portfolio'])
        m3.metric('Stock portfolios', len(PORTFOLIOS))
        st.caption('Leaders have the highest *sample average* monthly return under the selected settings, not proven future outperformance.')
        fig = px.bar(summary, x='portfolio', y='average_monthly_return_pct', color='regime',
                     barmode='group', color_discrete_map={'High inflation':'#C97843', 'Low inflation':'#346C90'},
                     category_orders={'portfolio':PORTFOLIOS, 'regime':['High inflation','Low inflation']},
                     labels={'portfolio':'Stock group', 'average_monthly_return_pct':'Average monthly return (%)', 'regime':'Inflation environment'})
        fig.update_layout(margin=dict(l=10,r=10,t=25,b=10), legend_title_text='',
                          legend_orientation='h', legend_y=1.13, xaxis_tickangle=-22)
        st.plotly_chart(fig, use_container_width=True)
        most_affected = contrast.sort_values('high_minus_low_percentage_points').iloc[0]
        least_affected = contrast.sort_values('high_minus_low_percentage_points', ascending=False).iloc[0]
        st.markdown('#### Reading the chart')
        st.write(f'In this sample, **{high.iloc[0]["portfolio"]}** had the highest average return during high-inflation months, while **{low.iloc[0]["portfolio"]}** led during low-inflation months. The biggest high-minus-low return difference was for **{most_affected["portfolio"]}** ({most_affected["high_minus_low_percentage_points"]:+.2f} percentage points per month). These are descriptive patterns, not evidence that inflation caused them.')
        with st.expander('Detailed comparison table and CSV download'):
            show = contrast.rename(columns={'portfolio':'Stock group','High inflation':'High inflation (%)',
                      'Low inflation':'Low inflation (%)','high_minus_low_percentage_points':'High minus low (percentage points)'})
            st.dataframe(show.round(3), use_container_width=True, hide_index=True)
            st.download_button('Download comparison CSV', contrast.to_csv(index=False).encode(), 'factorlab_comparison.csv', 'text/csv')
        with st.expander('What do the six stock groups mean?'):
            st.write('**Small / Big** classify firms by relative market capitalization. **Growth / Value** refer to low / high book-to-market ratios—not necessarily actual earnings growth. **Neutral** is the middle valuation group. The figures reflect diversified research portfolios, not individual companies.')
        st.caption(interpretation_warning())
    with factor_tab:
        st.markdown('### What helps explain returns?')
        st.write('The Fama–French five-factor model measures how the selected portfolio historically moved with market, size, value, profitability, and investment factors. It is an explanation of the sample—not a forecast.')
        f1,f2 = st.columns(2)
        with f1:
            selected = st.selectbox('Stock group', PORTFOLIOS)
        with f2:
            selected_regime = st.selectbox('Period to analyze', ['All months', 'High inflation', 'Low inflation'])
        with st.spinner('Calculating factor exposures...'):
            factors = load_factors()
            aligned = df.join(factors, how='inner')
            model, table, n_months = fit_factor_model(aligned, selected, selected_regime)
        c1,c2,c3=st.columns(3)
        c1.metric('Months analyzed',n_months)
        c2.metric('Historical model fit (R²)',f'{model.rsquared:.1%}')
        c3.metric('Estimated monthly alpha',f'{model.params["const"]:+.3f}%')
        labels = {'Mkt-RF':'Market','SMB':'Size','HML':'Value','RMW':'Profitability','CMA':'Investment'}
        plot = table.loc[table.factor.isin(FACTOR_NAMES)].copy()
        plot['Factor'] = plot.factor.map(labels)
        fig2=px.bar(plot,x='Factor',y='coefficient',labels={'coefficient':'Estimated exposure'},text_auto='.2f')
        fig2.update_layout(margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig2,use_container_width=True)
        st.write('**How to interpret this:** A positive coefficient means the portfolio tended to rise when that factor rose, after accounting for the other factors. R² measures in-sample fit, not forecasting accuracy. Alpha is not proof of skill.')
        with st.expander('Five-factor definitions in plain English'):
            for term,explanation in [
                ('Market (Mkt-RF)','Broad stock-market return above the risk-free rate.'),
                ('Size (SMB)','Small-company returns compared with large-company returns.'),
                ('Value (HML)','High book-to-market (value) relative to low book-to-market (growth).'),
                ('Profitability (RMW)','Firms with robust profitability compared with weak profitability.'),
                ('Investment (CMA)','Conservative corporate investment compared with aggressive investment.')]:
                st.markdown(f'**{term}** — {explanation}')
        with st.expander('Regression coefficients, p-values, confidence intervals and CSV'):
            display = table.rename(columns={'factor':'Factor','coefficient':'Estimated exposure',
               'p_value':'P-value','ci_low_95':'95% interval: low','ci_high_95':'95% interval: high'})
            st.dataframe(display.round(4),use_container_width=True,hide_index=True)
            st.download_button('Download regression CSV',table.to_csv(index=False).encode(),'factorlab_factor_regression.csv','text/csv')
        st.caption('Regime-specific coefficients are descriptive. To establish whether they differ statistically requires an explicit interaction test. The five factors partially reflect the same size and value characteristics used to define the portfolios.')
    with methods:
        st.markdown('### What are we testing?')
        st.write('**Research question:** Does inflation change which types of stocks have higher average historical returns? We compare six U.S. size/value portfolios across high- and low-inflation months, then use a five-factor regression to analyze return exposures.')
        st.markdown('### Data & choices')
        st.write('**Portfolios and factors:** Kenneth French Data Library. **Inflation:** FRED CPIAUCSL. We calculate annual CPI inflation and shift it by two months as an approximate information delay. Inflation threshold and sample start are adjustable in the sidebar.')
        st.markdown('### What we can — and cannot — conclude')
        st.write('This is exploratory analysis. Historical averages do not establish causes or profitable trading signals. CPI comes from a revised series rather than the inflation values originally published in each month. Periods such as 2008 and 2022 may shape the results. The multiple comparisons and regime differences need robustness testing before strong statistical claims.')
        st.write('Regression fits use monthly excess returns and HAC standard errors with three lags; factor exposures for size/value portfolios are partly expected by construction. Estimates can change with sample choices.')
        st.markdown('### Original sources')
        st.markdown('[Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) · [FRED CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL)')
except Exception as exc:
    st.error(f'Unable to load FactorLab: {exc}')
    st.info('If the data downloads are unavailable, try reloading later. For short windows with too few observations, choose an earlier start year.')
