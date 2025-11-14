import os
import argparse
import pandas as pd
import numpy as np

WEEKS = [4, 16, 52]

def load_csv(path):
    df = pd.read_csv(path)

    # IMPORTANT: remove accidental header rows inside data
    df = df[df["Date"] != "Date"]

    # Ensure proper dtypes
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df


def compute_moving_averages(df):
    for w in WEEKS:
        days = w * 5  # approximate trading days
        df[f"ma_{w}w"] = df["Close"].rolling(days, min_periods=1).mean()
    return df


def compute_rolling(df, win):
    df[f"roll_mean_{win}"] = df["Close"].rolling(win, min_periods=1).mean()
    return df


def volume_shocks(df):
    pct = df["Volume"].pct_change()
    df["vol_shock"] = (pct.abs() >= 0.10).astype(int)
    df["vol_shock_dir"] = (pct > 0).astype(int)
    return df


def price_shocks(df):
    pct = df["Close"].pct_change()
    df["price_shock"] = (pct.abs() >= 0.02).astype(int)
    df["price_shock_dir"] = (pct > 0).astype(int)
    return df


def black_swan(df):
    pct = df["Close"].pct_change()
    df["black_swan"] = (pct.abs() >= 0.05).astype(int)
    return df


def price_no_volume(df):
    df["price_no_vol"] = ((df["price_shock"] == 1) & (df["vol_shock"] == 0)).astype(int)
    return df


def process_file(path):
    df = load_csv(path)

    if df.empty:
        return None

    df = compute_moving_averages(df)
    df = compute_rolling(df, 10)
    df = compute_rolling(df, 75)
    df = volume_shocks(df)
    df = price_shocks(df)
    df = black_swan(df)
    df = price_no_volume(df)

    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data")
    parser.add_argument("--output-dir", default="processed")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    combined = []

    for fname in os.listdir(args.input_dir):
        if fname.endswith(".csv"):
            symbol = fname.split(".")[0]
            df = process_file(os.path.join(args.input_dir, fname))

            if df is None or df.empty:
                print(f"Skipping {symbol}, no valid data.")
                continue

            df["symbol"] = symbol
            df.to_csv(f"{args.output_dir}/{symbol}_features.csv", index=False)
            combined.append(df)

    if combined:
        final = pd.concat(combined).sort_values(["symbol", "Date"])
        final.to_csv(f"{args.output_dir}/combined.csv", index=False)
        print("Saved processed/combined.csv")


if __name__ == "__main__":
    main()