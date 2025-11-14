#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LassoLars
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_absolute_percentage_error as mape
import joblib, os

FEATURES = ['Close','ma_4w','ma_16w','ma_52w','vol_shock','price_shock']

def prepare(df, symbol):
    df = df[df['symbol']==symbol].sort_values('Date').reset_index(drop=True)
    df = df.dropna(subset=['Close'])
    df['target'] = df['Close'].shift(-1)
    X = df[FEATURES].fillna(method='ffill').dropna()
    y = df.loc[X.index,'target']
    return X, y, df.loc[X.index]

def quick_build(X,y):
    lr = LinearRegression()
    lr.fit(X,y)
    return lr

def grid_tune(X,y):
    model = LassoLars(max_iter=500)
    params = {'alpha':[0.001,0.01,0.1]}
    tscv = TimeSeriesSplit(n_splits=3)
    gs = GridSearchCV(model, params, cv=tscv, scoring='neg_mean_absolute_error', n_jobs=1)
    gs.fit(X,y)
    return gs.best_estimator_, gs.best_score_

def evaluate(model, X_test, y_test):
    preds = model.predict(X_test)
    return mape(y_test, preds), preds

def main():
    df = pd.read_csv('processed/combined.csv', parse_dates=['Date'])
    os.makedirs('models', exist_ok=True)
    for sym in df['symbol'].unique():
        X,y,meta = prepare(df,sym)
        if len(X) < 20:
            continue
        quick = quick_build(X,y)
        tuned, score = grid_tune(X,y)
        m, preds = evaluate(tuned, X.tail(5), y.tail(5))
        joblib.dump({'quick':quick,'tuned':tuned}, f'models/{sym}_models.pkl')
        print(sym, 'MAPE on last 5:', m)

if __name__ == '__main__':
    main()
