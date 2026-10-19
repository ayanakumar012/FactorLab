"""AlphaLens data loader. Returns percent monthly portfolio returns and CPI levels."""
import io
import re
import urllib.request
import zipfile
import pandas as pd

FRENCH_URL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/6_Portfolios_2x3_CSV.zip'
FRED_URL = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL'
PORTFOLIOS = ['Small Growth', 'Small Neutral', 'Small Value', 'Big Growth', 'Big Neutral', 'Big Value']


def fetch_french_monthly(url=FRENCH_URL):
    """Download Kenneth French six size/value portfolios, percent monthly returns."""
    req = urllib.request.Request(url, headers={'User-Agent': 'AlphaLens educational research (public data)'})
    with urllib.request.urlopen(req, timeout=40) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        csv_name = next((n for n in archive.namelist() if n.lower().endswith('.csv')), None)
        if csv_name is None:
            raise ValueError('Kenneth French archive did not contain a CSV file')
        content = archive.read(csv_name).decode('utf-8-sig', errors='replace')
    # File starts with notes; the first block of YYYYMM, six monthly returns is value-weighted monthly portfolios.
    rows = []
    for line in content.splitlines():
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 7 and re.fullmatch(r'\d{6}', parts[0]):
            if rows and int(parts[0]) <= int(rows[-1][0]):
                break  # next section: do not accidentally join equal-weight or annual data
            rows.append(parts[:7])
        elif rows:
            break
    if len(rows) < 120:
        raise ValueError(f'Unexpected French CSV format: only {len(rows)} monthly rows')
    df = pd.DataFrame(rows, columns=['month'] + PORTFOLIOS)
    df.index = pd.PeriodIndex(df.pop('month'), freq='M')
    for column in PORTFOLIOS:
        df[column] = pd.to_numeric(df[column], errors='coerce')
        df.loc[df[column] <= -99, column] = float('nan')  # missing-value codes
    df.index.name = 'month'
    return df


def fetch_cpi(url=FRED_URL):
    """Get historical CPI levels; latest revised vintage, not real-time vintage."""
    frame = pd.read_csv(url)
    date_col = 'DATE' if 'DATE' in frame.columns else 'observation_date'
    if date_col not in frame.columns or 'CPIAUCSL' not in frame.columns:
        raise ValueError(f'Unexpected FRED columns: {list(frame.columns)}')
    dates = pd.to_datetime(frame[date_col], errors='coerce')
    out = pd.DataFrame({'CPI': pd.to_numeric(frame['CPIAUCSL'], errors='coerce').to_numpy()},
                       index=pd.PeriodIndex(dates, freq='M'))
    out.index.name = 'month'
    return out.dropna().sort_index()


def prepare_data(returns, cpi, start='1990-01', end=None, threshold=3.0):
    """Merge data and lag inflation information by two months as conservative proxy for release delay."""
    c = cpi.copy()
    c['inflation_yoy'] = c['CPI'].pct_change(12, fill_method=None) * 100
    c['known_inflation'] = c['inflation_yoy'].shift(2)
    combined = returns.join(c[['known_inflation']], how='inner')
    combined = combined.loc[pd.Period(start, freq='M'):pd.Period(end, freq='M') if end else None]
    combined = combined.dropna(subset=['known_inflation'] + PORTFOLIOS)
    if combined.empty:
        raise ValueError('No overlapping observations. Check your dates and downloads.')
    combined['regime'] = combined['known_inflation'].map(lambda x: 'High inflation' if x > threshold else 'Low inflation')
    return combined
