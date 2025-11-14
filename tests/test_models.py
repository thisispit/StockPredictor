import os, pytest
import pandas as pd
from models import prepare, quick_build, grid_tune, evaluate

@pytest.fixture(scope='module')
def data():
    df = pd.read_csv('processed/combined.csv', parse_dates=['Date'])
    return df

def test_two_models_run(data):
    for sym in ['INFY','TCS']:
        X,y,meta = prepare(data,sym)
        if len(X) < 10:
            pytest.skip(f'Not enough data for {sym}')
        quick = quick_build(X,y)
        tuned, score = grid_tune(X,y)
        m, preds = evaluate(tuned, X.tail(5), y.tail(5))
        assert m >= 0
