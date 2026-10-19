# AlphaLens

**Research question:** Does inflation change which types of stocks perform best?

An educational dashboard comparing historical average monthly returns for six U.S. size/book-to-market research portfolios during high- and low-inflation periods.

## Try the dashboard

Once deployed, open your Streamlit app URL. Choose a starting year and an inflation threshold to compare returns and export results.

## Data & methods

- **Stocks:** Kenneth French Data Library, *6 Portfolios Formed on Size and Book-to-Market (2 x 3)*, value-weighted monthly returns. These are constructed research portfolios, not named individual companies.
- **Inflation:** Federal Reserve Economic Data (FRED), CPIAUCSL, year-over-year percent change.
- **Timing:** For a return in month t, the app classifies the regime using inflation for month t-2 as a simplified release-lag rule. This does **not** reconstruct real-time CPI vintages; historical CPI levels may have been revised.
- **High inflation:** available year-over-year CPI inflation > 3% by default; this threshold is adjustable.
- **Statistics:** historical conditional arithmetic means (monthly %), not predictions. Observed differences do **not** demonstrate causation or statistical significance.

## Deploy with GitHub + Streamlit Community Cloud — browser only

1. Sign into GitHub, create a **public** repository called `AlphaLens`, and do **not** add a README during repository creation.
2. From your computer, upload the **contents of this folder**, not the enclosing folder, so `app.py` and `requirements.txt` sit at the repository root.
3. Visit https://share.streamlit.io/ and sign in with GitHub. Select **Create app** / **Deploy an app**, and select the AlphaLens repository, branch `main`, and main file `app.py`.
4. Deploy and wait for Streamlit to install packages and load publicly available datasets.
5. If it fails, copy the **error logs** from Streamlit and ask for troubleshooting help. Never paste GitHub passwords or tokens.

The app fetches public data when launched; the server needs network access to the Kenneth French Data Library and FRED. Free hosting and remote sites can have temporary rate limits or outages.

## Project files

- `app.py`: browser dashboard
- `src/data.py`: downloads and harmonizes data
- `src/analysis.py`: calculates comparison summaries
- `research_notebook.ipynb`: introductory Colab notebook for learning; its earlier regime choices may differ from the dashboard's lagged-regime methodology
- `requirements.txt`: Python dependencies installed by Streamlit
- `tests/test_analysis.py`: basic offline tests

## Important limitations

The dashboard is an exploratory analysis, not a finished academic finding. Before making strong research claims, verify data windows, data releases/revisions, sensitivity to crises and regime thresholds, serial correlation, and multiple-testing corrections. The separately conducted Fama–French five-factor regressions are **not yet part of this dashboard** and should not be presented as dashboard functionality.

**Not investment advice.**
