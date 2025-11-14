#!/usr/bin/env python3
"""Download OCLHV data for given tickers and an index between dates.
Tries raw GitHub repo URL first; falls back to asking user to place CSVs.
"""
import os, argparse
import requests

RAW_BASE = 'https://raw.githubusercontent.com/swapniljariwala/nsepy/master/data'

def try_download_csv(symbol, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{symbol}.csv"
    urls = [
        f"{RAW_BASE}/{filename}",
        f"{RAW_BASE}/{symbol.lower()}.csv"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and 'Date' in r.text:
                with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(r.text)
                print('Downloaded', url)
                return os.path.join(out_dir, filename)
        except Exception:
            pass
    print(f"Could not download {symbol}. Place {filename} in {out_dir} manually.")
    return None

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--tickers', nargs='+', default=['INFY','TCS'])
    p.add_argument('--index', default='NIFTYIT')
    p.add_argument('--out', default='data')
    args = p.parse_args()
    for t in args.tickers + [args.index]:
        try_download_csv(t, args.out)

if __name__ == '__main__':
    main()
