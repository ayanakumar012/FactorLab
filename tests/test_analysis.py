import pandas as pd
from src.analysis import contrast_table, summary_table
from src.data import PORTFOLIOS


def test_tables_from_toy_sample():
    dates = pd.period_range('2020-01', periods=4, freq='M')
    sample = pd.DataFrame({key: [1., 2., 3., 4.] for key in PORTFOLIOS}, index=dates)
    sample['regime'] = ['High inflation', 'Low inflation', 'High inflation', 'Low inflation']
    summary = summary_table(sample)
    out = contrast_table(summary)
    assert len(out) == 6
    assert (out['high_minus_low_percentage_points'] == -1.0).all()
