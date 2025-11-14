#!/usr/bin/env python3
"""Download OCLHV data for given tickers and an index between dates.
"""
import os
import yfinance as yf
import argparse

def download_ticker_data(symbol, start_date, end_date, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        if not data.empty:
            # yfinance uses 'Adj Close' so we rename it to 'Close' to match the old format
            if 'Adj Close' in data.columns:
                data = data.rename(columns={'Adj Close': 'Close'})
            
            # Ensure all expected columns are present, fill with 0 if not
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col not in data.columns:
                    data[col] = 0

            # Select and reorder columns to match the old format
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

            # Format the date index to string 'YYYY-MM-DD'
            data.index = data.index.strftime('%Y-%m-%d')
            
            # Save to CSV with 'Date' as a column
            filename = f"{symbol.replace('^', '')}.csv"
            data.to_csv(os.path.join(out_dir, filename), index_label='Date', header=True)
            print(f"Downloaded {symbol} data to {out_dir}")
        else:
            print(f"No data found for {symbol} between {start_date} and {end_date}")
    except Exception as e:
        print(f"Could not download {symbol}. Error: {e}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tickers', nargs='+', default=['INFY.NS', 'TCS.NS'])
    p.add_argument('--index', default='^NSEI')
    p.add_argument('--start', default='2000-01-01')
    p.add_argument('--end', default='2023-12-31')
    p.add_argument('--out', default='data')
    args = p.parse_args()

    # Download data for tickers and index
    for ticker in args.tickers:
        download_ticker_data(ticker, args.start, args.end, args.out)
    download_ticker_data(args.index, args.start, args.end, args.out)

if __name__ == '__main__':
    main()
