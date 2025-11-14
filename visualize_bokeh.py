#!/usr/bin/env python3
import os, argparse
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource

from statsmodels.graphics.tsaplots import pacf

def make_timeseries(df, sym, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    df = df[df["symbol"] == sym].copy()

    # Ensure proper datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # FIX: Remove unwanted leftover index columns before ColumnDataSource
    for col in ["level_0", "index"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    # ColumnDataSource must use a clean copy
    src = ColumnDataSource(df)

    p = figure(
        x_axis_type="datetime",
        title=f"{sym} Close Price",
        width=900,
        height=300,
        toolbar_location="right"
    )

    # FIX: Ensure the y-axis shows the line
    p.y_range.start = df["Close"].min() * 0.95
    p.y_range.end = df["Close"].max() * 1.05

    # Main close price line
    p.line("Date", "Close", source=src, line_width=2, color="blue")

    # Volume shock segments
    shocks = df.index[df["vol_shock"] == 1]
    for i in shocks:
        if i > 0:
            p.line(
                [df.loc[i-1, "Date"], df.loc[i, "Date"]],
                [df.loc[i-1, "Close"], df.loc[i, "Close"]],
                line_width=3,
                color="red"
            )

    # Price no-volume markers
    indices = df.index[df["price_no_vol"] == 1]
    p.circle(df.loc[indices, "Date"], df.loc[indices, "Close"],
             size=8, fill_color="yellow", line_color="black")

    output_file(f"{out_dir}/{sym}_timeseries.html")
    save(p)

def make_pacf(df, sym, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df = df[df['symbol']==sym].sort_values('Date').reset_index(drop=True)
    df = df.drop(columns=[col for col in ["level_0", "index"] if col in df.columns])
    vals = df['Close'].dropna().values
    nlags = min(40, len(vals)//2 - 1)
    if nlags < 0:
        print(f"Skipping PACF for {sym} due to insufficient data.")
        return
    pacf_vals = pacf(vals, nlags=nlags, method='yw')
    p = figure(title=f"PACF - {sym}", width=900, height=300)
    p.vbar(x=list(range(len(pacf_vals))), top=pacf_vals, width=0.8)
    out = os.path.join(out_dir, f"{sym}_pacf.html")
    output_file(out)
    save(p)
    print('Saved', out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='processed')
    p.add_argument('--out', default='plots')
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for fname in os.listdir(args.input):
        if fname.lower().endswith('_features.csv'):
            sym = fname.split('_')[0]
            df = pd.read_csv(os.path.join(args.input, fname), parse_dates=['Date'])
            symbol_df = df.reset_index(drop=True)
            make_timeseries(symbol_df, sym, args.out)
            make_pacf(symbol_df, sym, args.out)
    print(f'Wrote plots to {args.out}')

if __name__ == '__main__':
    main()
