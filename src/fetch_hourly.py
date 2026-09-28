"""Fetch BTCUSDT hourly closes from Binance and write data/btc_hourly.csv (D-023)."""

import os

import pandas as pd
import requests

BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1h"
LIMIT = 1000
HOUR_MS = 60 * 60 * 1000

# Fixed window, open times of the first and last candle, both inclusive.
# The extra first hour is needed for the first hourly return of 2023-09-23 (D-023).
START = pd.Timestamp("2023-09-22 23:00:00", tz="UTC")
END = pd.Timestamp("2026-09-21 23:00:00", tz="UTC")

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "btc_hourly.csv")


def fetch_klines(start_ms: int, end_ms: int) -> list:
    rows = []
    cur_start = start_ms
    while cur_start <= end_ms:
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "startTime": cur_start,
            "endTime": end_ms,
            "limit": LIMIT,
        }
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        rows.extend(data)
        # Step by one hour, not one day: a daily step would silently skip data.
        cur_start = data[-1][0] + HOUR_MS
    return rows


def main():
    start_ms = int(START.timestamp() * 1000)
    end_ms = int(END.timestamp() * 1000)

    rows = fetch_klines(start_ms, end_ms)

    open_times = pd.to_datetime([row[0] for row in rows], unit="ms", utc=True)
    df = pd.DataFrame(
        {
            "open_time": open_times.strftime("%Y-%m-%d %H:%M:%S"),
            "close": [float(row[4]) for row in rows],
        }
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    expected = pd.date_range(START, END, freq="h")
    missing = expected.difference(open_times)

    print(f"rows: {len(df)}")
    print(f"first open_time: {df['open_time'].iloc[0]}")
    print(f"last open_time: {df['open_time'].iloc[-1]}")
    print(f"expected rows: {len(expected)}")
    print(f"duplicate open_times: {int(open_times.duplicated().sum())}")
    print(f"missing hours: {len(missing)}")
    for ts in missing[:20]:
        print(f"  {ts.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
