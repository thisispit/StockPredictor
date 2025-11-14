#!/usr/bin/env python3
import os, argparse
import pandas as pd
import numpy as np

WEEKS = [4,16,52]

def load_csv(path):
    df = pd.read_csv(path, parse_dates=['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    return df

def compute_moving_averages(df):
    for w in WEEKS:
        days = max(1, w*5)
        df[f'ma_{w}w'] = df['Close'].rolling(window=days, min_periods=1).mean()
    return df

def compute_rolling_windows(df, win=10):
    df = df.set_index('Date').asfreq('B')  # business day index
    for col in ['Open','High','Low','Close','Volume']:
        if col in df.columns:
            df[col] = df[col].astype(float)
    df[f'roll_mean_{win}'] = df['Close'].rolling(window=win, min_periods=1).mean()
    df = df.reset_index()
    return df

def volume_shocks(df, pct=0.10):
    v = df['Volume'].fillna(method='ffill')
    pctchg = v.pct_change()
    shock = (pctchg.abs() >= pct).astype(int)
    dir_shock = (pctchg >= pct).astype(int) - (pctchg <= -pct).astype(int)
    df['vol_shock'] = shock
    df['vol_shock_dir'] = (dir_shock>0).astype(int)
    return df

def price_shocks(df, pct=0.02):
    p = df['Close']
    pctchg = p.pct_change()
    shock = (pctchg.abs() >= pct).astype(int)
    dir_shock = (pctchg >= pct).astype(int) - (pctchg <= -pct).astype(int)
    df['price_shock'] = shock
    df['price_shock_dir'] = (dir_shock>0).astype(int)
    return df

def pricing_black_swan(df, pct=0.05):
    p = df['Close']
    pctchg = p.pct_change().abs()
    swan = (pctchg >= pct).astype(int)
    df['black_swan'] = swan
    return df

def price_shock_without_volume(df):
    df['price_no_vol'] = ((df.get('price_shock',0)==1) & (df.get('vol_shock',0)==0)).astype(int)
    return df

def process_file(path, rolling_windows=[10,75]):
    df = load_csv(path)
    df = compute_moving_averages(df)
    for w in rolling_windows:
        df = compute_rolling_windows(df, win=w)
    df = volume_shocks(df)
    df = price_shocks(df)
    df = pricing_black_swan(df)
    df = price_shock_without_volume(df)
    return df

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', default='data')
    p.add_argument('--output-dir', default='processed')
    args = p.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    combined = []
    for fname in os.listdir(args.input_dir):
        if fname.lower().endswith('.csv'):
            sym = os.path.splitext(fname)[0].upper()
            df = process_file(os.path.join(args.input_dir, fname))
            df['symbol'] = sym
            combined.append(df)
            df.to_csv(os.path.join(args.output_dir, f"{sym}_features.csv"), index=False)
    if combined:
        all_df = pd.concat(combined).sort_values(['symbol','Date'])
        all_df.to_csv(os.path.join(args.output_dir, 'combined.csv'), index=False)
        print('Wrote processed/combined.csv')

if __name__ == '__main__':
    main()
