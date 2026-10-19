import numpy as np
import pandas as pd
from src.factors import fit_factor_model, FACTOR_NAMES


def test_factor_model_toy_data():
    r = np.random.default_rng(8)
    idx = pd.period_range('2010-01', periods=72, freq='M')
    df = pd.DataFrame(r.normal(0, 1, (72, 5)), columns=FACTOR_NAMES, index=idx)
    df['RF'] = 0.1
    df['Small Growth'] = df['RF'] + 0.2 + 1.2 * df['Mkt-RF'] + 0.7 * df['SMB']
    df['regime'] = ['High inflation'] * 36 + ['Low inflation'] * 36
    model, coeffs, n = fit_factor_model(df, 'Small Growth')
    assert n == 72
    assert np.isclose(model.params['Mkt-RF'], 1.2)
    assert np.isclose(model.params['SMB'], 0.7)
    assert len(coeffs) == 6
