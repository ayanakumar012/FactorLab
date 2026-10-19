# FactorLab

**Does inflation change which types of stocks perform best?**

FactorLab is an interactive, browser-hosted quantitative finance research dashboard comparing six U.S. stock portfolios across inflation environments, with optional Fama–French five-factor regressions.

**Live application:** https://factorlab-research.streamlit.app/

## Navigate the dashboard

1. **Performance overview:** See high- and low-inflation sample leaders, historical monthly returns, and an optional detailed table.
2. **Factor analysis:** Pick a stock group and sample to examine estimated market, size, value, profitability, and investment exposures.
3. **Research notes:** Read the methodology, source links, and limitations.

Set the sample start and inflation threshold in the sidebar. Downloadable CSVs are available inside expandable sections.

## Data and methods

- Six size/book-to-market portfolios and monthly five-factor series from the [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).
- CPIAUCSL index from [FRED](https://fred.stlouisfed.org/series/CPIAUCSL).
- Inflation: year-over-year CPI percentage change, shifted two calendar months as a conservative *approximation* for publication lag. This uses revised CPI, not point-in-time vintages.
- Regressions: monthly portfolio return minus RF on the five Fama–French factors with an intercept and HAC(3) standard errors.

**Interpretation warning:** Descriptive differences are not causal evidence, a prediction, or proof of statistical robustness. Sensitivity to inflation threshold, crisis years, CPI vintage, and multiple hypothesis tests warrants further validation.

## Deploy

Streamlit Community Cloud: connect this repository, choose the `main` branch and `app.py` as the entry point. No laptop-side installations are required for visitors.

## Repository structure

`app.py` (interface), `src/data.py` (data sources/prep), `src/analysis.py` (descriptive statistics), `src/factors.py` (regressions), `tests/` (automated checks).
