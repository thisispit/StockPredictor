#!/usr/bin/env python3
import sys, joblib, pandas as pd, os
def main():
    if len(sys.argv)<2:
        print('Usage: python stockpredictor.py SYMBOL')
        return
    sym = sys.argv[1].upper()
    modelpath = f'models/{sym}_models.pkl'
    if not os.path.exists(modelpath):
        print('Model not found. Run models.py first to train and save models.')
        return
    models = joblib.load(modelpath)
    tuned = models.get('tuned', models.get('quick'))
    df = pd.read_csv('processed/combined.csv', parse_dates=['Date'])
    X,y,meta = __import__('models').prepare(df,sym)
    last_X = X.tail(1)
    pred = tuned.predict(last_X)[0]
    print(pred)

if __name__=='__main__':
    main()
