"""Descriptive historical comparisons. No forecast or causal interpretation."""
import numpy as np
import pandas as pd
from .data import PORTFOLIOS


def summary_table(df):
    output = []
    for regime, subset in df.groupby('regime'):
        for portfolio in PORTFOLIOS:
            x = subset[portfolio].dropna()
            output.append({'regime': regime, 'portfolio': portfolio,
                           'months': len(x), 'average_monthly_return_pct': x.mean(),
                           'annualized_arithmetic_return_pct': x.mean() * 12,
                           'monthly_volatility_pct': x.std(ddof=1)})
    return pd.DataFrame(output)


def contrast_table(summary):
    pivot = summary.pivot(index='portfolio', columns='regime', values='average_monthly_return_pct')
    required = {'High inflation', 'Low inflation'}
    if not required.issubset(pivot.columns):
        raise ValueError('Both inflation regimes required for comparison; adjust sample or threshold')
    pivot['high_minus_low_percentage_points'] = pivot['High inflation'] - pivot['Low inflation']
    return pivot.reset_index()


def interpretation_warning():
    return ('These are descriptive conditional historical averages, not expected future returns. '
            'Inflation regimes use the latest revised CPI series with a two-month lag, not true historical release vintages. '
            'The portfolios are research portfolios rather than investable funds; transaction costs are not included. '
            'Averages alone do not establish statistically reliable differences or causation.')
