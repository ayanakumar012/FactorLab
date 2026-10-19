# FactorLab

**Does inflation change which types of stocks perform best?**

A browser-based interactive research application comparing monthly returns of six U.S. size/value portfolios across high- and low-inflation environments. It also estimates historical Fama–French five-factor exposures with HAC standard errors.

## Data sources
- Kenneth French Data Library: value-weighted **6 Portfolios Formed on Size and Book-to-Market**; U.S. **Fama/French 5 Factors (2x3)**, monthly.
- FRED **CPIAUCSL**: monthly CPI levels, transformed to year-over-year inflation, lagged two months for a simple publication-delay proxy.

## How to deploy
Upload `app.py`, `requirements.txt`, `README.md`, and the full `src/` folder into the repository root. On Streamlit Community Cloud, select `app.py` as the entry point. No local installation required.

## Limitations
Exploratory historical comparisons, not causality or investment recommendations. Latest-revised CPI rather than point-in-time release vintages. Model fit is in-sample and factor portfolios are related by construction. Differences across inflation regimes require appropriate formal testing and robustness checks before publication as conclusive findings.

## Reader guide
Choose a start year and inflation threshold, read the Compare stock groups tab, then use Five-factor regression for a deeper analysis. Group winners are descriptive averages rather than statistical or investment recommendations.
