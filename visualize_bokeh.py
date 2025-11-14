#!/usr/bin/env python3
import os, argparse
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource

from statsmodels.graphics.tsaplots import pacf

def make_timeseries(df, sym, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df = df[df['symbol']==sym].sort_values('Date').reset_index(drop=True)
    src = ColumnDataSource(df)
    p = figure(x_axis_type='datetime', title=f"{sym} Close Price", width=900, height=300)
    p.line('Date','Close', source=src, line_width=2, legend_label='Close')
    # red segments between consecutive volume shocks
    for i in range(1,len(df)):
        if df.loc[i-1,'vol_shock']==1 and df.loc[i,'vol_shock']==1:
            p.line([df.loc[i-1,'Date'], df.loc[i,'Date']], [df.loc[i-1,'Close'], df.loc[i,'Close']], line_color='red', line_width=3)
    # mark price_no_vol
    idxs = df[df.get('price_no_vol',0)==1].index
    for i in idxs:
        p.circle([df.loc[i,'Date']], [df.loc[i,'Close']], size=8, fill_color='yellow', line_color='black')
    out = os.path.join(out_dir, f"{sym}_timeseries.html")
    output_file(out)
    save(p)
    print('Saved', out)

def make_pacf(df, sym, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df = df[df['symbol']==sym].sort_values('Date').reset_index(drop=True)
    vals = df['Close'].dropna().values
    pacf_vals = pacf(vals, nlags=min(40, len(vals)-1), method='ywunbiased')
    p = figure(title=f"PACF - {sym}", width=900, height=300)
    p.vbar(x=list(range(len(pacf_vals))), top=pacf_vals, width=0.8)
    out = os.path.join(out_dir, f"{sym}_pacf.html")
    output_file(out)
    save(p)
    print('Saved', out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='processed/combined.csv')
    p.add_argument('--out', default='plots')
    args = p.parse_args()
    df = pd.read_csv(args.input, parse_dates=['Date'])
    symbols = df['symbol'].unique()
    for s in symbols:
        make_timeseries(df, s, args.out)
        make_pacf(df, s, args.out)

if __name__ == '__main__':
    main()
