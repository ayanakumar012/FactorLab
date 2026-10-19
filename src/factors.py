"""Fama–French 5 factor monthly loader and descriptive regression tools."""
import io
import re
import urllib.request
import zipfile
import pandas as pd
import statsmodels.api as sm

FACTOR_URL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip'
FACTOR_NAMES = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']


def fetch_five_factors(url=FACTOR_URL):
    request = urllib.request.Request(url, headers={'User-Agent': 'FactorLab educational research'})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        name = next((name for name in archive.namelist() if name.lower().endswith('.csv')), None)
        if name is None:
            raise ValueError('Five-factor archive has no CSV')
        content = archive.read(name).decode('utf-8-sig', errors='replace')
    rows = []
    for line in content.splitlines():
        parts = [item.strip() for item in line.split(',')]
        if len(parts) == 7 and re.fullmatch(r'\d{6}', parts[0]):
            if rows and int(parts[0]) <= int(rows[-1][0]):
                break
            rows.append(parts)
        elif rows:
            break
    if len(rows) < 120:
        raise ValueError('Could not parse the monthly five-factor data')
    frame = pd.DataFrame(rows, columns=['month'] + FACTOR_NAMES + ['RF'])
    frame.index = pd.PeriodIndex(frame.pop('month'), freq='M')
    frame.index.name = 'month'
    frame = frame.apply(pd.to_numeric, errors='coerce')
    return frame.mask(frame <= -99).dropna()


def fit_factor_model(research_data, portfolio, regime='All months'):
    """Fit percentage-point monthly excess returns with HAC (3 lag) covariance."""
    cols = FACTOR_NAMES + ['RF', portfolio]
    subset = research_data.copy()
    if regime != 'All months':
        subset = subset.loc[subset['regime'] == regime]
    subset = subset.dropna(subset=cols).sort_index()
    if len(subset) < 36:
        raise ValueError(f'Only {len(subset)} months in {regime}. Choose a longer sample (at least 36 months).')
    y = subset[portfolio] - subset['RF']
    X = sm.add_constant(subset[FACTOR_NAMES], has_constant='add')
    model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
    table = pd.DataFrame({
        'coefficient': model.params,
        'p_value': model.pvalues,
        'ci_low_95': model.conf_int()[0],
        'ci_high_95': model.conf_int()[1],
    })
    table.index.name = 'factor'
    return model, table.reset_index(), len(subset)
