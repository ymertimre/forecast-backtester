"""Fetch BTCUSDT daily closes from Binance and write data/btc_daily.csv."""

import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1d"
LIMIT = 1000
DAY_MS = 24 * 60 * 60 * 1000
YEARS_OF_HISTORY = 3
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "btc_daily.csv")


def fetch_klines(start_ms: int, end_ms: int) -> list:
    """Page through the klines endpoint and return raw candle rows."""
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
        cur_start = data[-1][0] + DAY_MS
        if len(data) < LIMIT:
            break
    return rows


def main():
    now = datetime.now(timezone.utc)
    today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end_date = today - timedelta(days=1)  # last fully closed day; today's candle is still open
    start_date = end_date - timedelta(days=YEARS_OF_HISTORY * 365 - 1)

    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)
    end_date_str = end_date.strftime("%Y-%m-%d")

    rows = fetch_klines(start_ms, end_ms)

    df = pd.DataFrame(
        {
            "date": pd.to_datetime([row[0] for row in rows], unit="ms", utc=True).strftime("%Y-%m-%d"),
            "close": [float(row[4]) for row in rows],
        }
    )
    df = df[df["date"] <= end_date_str]
    df = df.drop_duplicates(subset="date").sort_values("date").reset_index(drop=True)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"rows: {len(df)}")
    print(f"first date: {df['date'].iloc[0]}")
    print(f"last date: {df['date'].iloc[-1]}")


if __name__ == "__main__":
    main()
