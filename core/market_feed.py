"""
Market Feed and Data Ingestion Module.
Provides realistic live-market continuous feeds for global & Indian instruments,
parses broker CSV exports (Zerodha, TradingView, etc.), and generates OHLCV from manual inputs.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import datetime
import pandas as pd
import numpy as np


class MarketFeedManager:
    # Supported Active Instruments
    INSTRUMENTS = {
        "NIFTY 50": {"base_price": 24550.0, "tick_size": 0.05, "category": "Indian Index", "timeframe": "5 Min"},
        "BANKNIFTY": {"base_price": 52100.0, "tick_size": 0.05, "category": "Indian Index", "timeframe": "15 Min"},
        "FINNIFTY": {"base_price": 23400.0, "tick_size": 0.05, "category": "Indian Index", "timeframe": "5 Min"},
        "SENSEX": {"base_price": 80400.0, "tick_size": 0.10, "category": "Indian Index", "timeframe": "15 Min"},
        "RELIANCE": {"base_price": 2780.0, "tick_size": 0.05, "category": "Indian Equity", "timeframe": "15 Min"},
        "HDFC BANK": {"base_price": 1720.0, "tick_size": 0.05, "category": "Indian Equity", "timeframe": "15 Min"},
        "TCS": {"base_price": 3960.0, "tick_size": 0.10, "category": "Indian Equity", "timeframe": "15 Min"},
        "TATA MOTORS": {"base_price": 890.0, "tick_size": 0.05, "category": "Indian Equity", "timeframe": "5 Min"},
        "GOLD (XAUUSD)": {"base_price": 2755.0, "tick_size": 0.01, "category": "Commodity / FX", "timeframe": "15 Min"},
        "SILVER (XAGUSD)": {"base_price": 33.50, "tick_size": 0.005, "category": "Commodity", "timeframe": "15 Min"},
        "CRUDE OIL": {"base_price": 71.20, "tick_size": 0.01, "category": "Commodity", "timeframe": "15 Min"},
        "BITCOIN (BTC/USDT)": {"base_price": 69400.0, "tick_size": 0.10, "category": "Crypto", "timeframe": "1 Hour"},
        "ETHEREUM (ETH/USDT)": {"base_price": 2520.0, "tick_size": 0.05, "category": "Crypto", "timeframe": "15 Min"},
        "SOLANA (SOL/USDT)": {"base_price": 178.0, "tick_size": 0.01, "category": "Crypto", "timeframe": "15 Min"},
        "NVIDIA (NVDA)": {"base_price": 141.50, "tick_size": 0.01, "category": "US Equity", "timeframe": "15 Min"},
        "APPLE (AAPL)": {"base_price": 231.00, "tick_size": 0.01, "category": "US Equity", "timeframe": "15 Min"},
        "SPDR S&P 500 (SPY)": {"base_price": 582.00, "tick_size": 0.01, "category": "US Index ETF", "timeframe": "15 Min"}
    }

    @classmethod
    def get_supported_instruments(cls) -> Dict[str, Dict[str, Any]]:
        return cls.INSTRUMENTS

    @classmethod
    def generate_instrument_feed(
        cls,
        symbol: str,
        n_candles: int = 70,
        regime: str = "INSTITUTIONAL_SMC"
    ) -> pd.DataFrame:
        """
        Synthesizes a realistic institutional continuous price action feed with:
        - Liquidity sweeps
        - Order Blocks & FVGs
        - Volatility expansion
        """
        meta = cls.INSTRUMENTS.get(symbol, {"base_price": 1000.0, "tick_size": 0.05, "timeframe": "5 Min"})
        base_price = meta["base_price"]
        volatility = base_price * 0.0025  # 0.25% per candle ATR

        np.random.seed(abs(hash(symbol)) % 10000)
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(minutes=5 * n_candles)

        timestamps = [start_time + datetime.timedelta(minutes=5 * i) for i in range(n_candles)]
        opens, highs, lows, closes, volumes = [], [], [], [], []

        p = base_price
        for i in range(n_candles):
            if i < 25:
                # Accumulation / range
                p += np.random.normal(0, volatility * 0.4)
                o = p
                h = o + abs(np.random.normal(volatility * 0.6, volatility * 0.2))
                l = o - abs(np.random.normal(volatility * 0.6, volatility * 0.2))
                c = (h + l) / 2 + np.random.normal(0, volatility * 0.2)
                v = np.random.randint(20000, 45000)
            elif i < 35:
                # Liquidity Sweep below range low
                p -= volatility * 0.5
                o = p
                l = o - (volatility * 2.2 if i == 30 else volatility * 0.8)  # Deep sweep
                h = o + volatility * 0.5
                c = o + (volatility * 1.5 if i == 30 else -volatility * 0.3)
                v = np.random.randint(60000, 110000) if i == 30 else np.random.randint(25000, 50000)
            elif i < 55:
                # Strong institutional displacement creating OB and FVG
                p += volatility * 0.8
                o = p
                h = o + volatility * 1.4
                l = o - volatility * 0.3
                c = h - volatility * 0.2
                v = np.random.randint(55000, 95000)
            elif i < 63:
                # Low volume healthy pullback into 50% discount
                p -= volatility * 0.35
                o = p
                h = o + volatility * 0.4
                l = o - volatility * 0.7
                c = (h + l) / 2
                v = np.random.randint(15000, 28000)
            else:
                # Continuation breakout with high volume
                p += volatility * 1.1
                o = p
                h = o + volatility * 1.6
                l = o - volatility * 0.2
                c = h - volatility * 0.1
                v = np.random.randint(80000, 140000)

            opens.append(round(o, 2))
            highs.append(round(max(o, c, h), 2))
            lows.append(round(min(o, c, l), 2))
            closes.append(round(c, 2))
            volumes.append(int(v))

        df = pd.DataFrame({
            "timestamp": [ts.strftime("%Y-%m-%d %H:%M") for ts in timestamps],
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes
        })
        return df

    @classmethod
    def parse_broker_csv(cls, file_or_path: Any) -> pd.DataFrame:
        """
        Robustly parses broker CSV exports (Zerodha, TradingView, Upstox, Angel One).
        Normalizes column names to: timestamp, open, high, low, close, volume.
        """
        df = pd.read_csv(file_or_path)

        # Mapping variations
        col_map = {}
        for col in df.columns:
            clean = col.lower().strip().replace(" ", "").replace("_", "")
            if clean in ["timestamp", "date", "time", "datetime"]:
                col_map[col] = "timestamp"
            elif clean in ["open", "o"]:
                col_map[col] = "open"
            elif clean in ["high", "h"]:
                col_map[col] = "high"
            elif clean in ["low", "l"]:
                col_map[col] = "low"
            elif clean in ["close", "c", "ltp"]:
                col_map[col] = "close"
            elif clean in ["volume", "vol", "v", "qty"]:
                col_map[col] = "volume"

        df = df.rename(columns=col_map)
        req_cols = ["open", "high", "low", "close"]
        for r in req_cols:
            if r not in df.columns:
                raise ValueError(f"CSV missing mandatory column: '{r}'. Found: {list(df.columns)}")

        if "volume" not in df.columns:
            df["volume"] = 10000.0

        if "timestamp" not in df.columns:
            df["timestamp"] = [f"T_{i}" for i in range(len(df))]

        return df

    @classmethod
    def generate_from_manual_levels(
        cls,
        symbol: str,
        current_price: float,
        support: float,
        resistance: float,
        trend_bias: str = "BULLISH",
        n_candles: int = 50
    ) -> pd.DataFrame:
        """
        Constructs a realistic OHLCV dataframe from on-the-go trader manual inputs.
        """
        range_span = max(abs(resistance - support), current_price * 0.015)
        step = range_span / 15.0

        opens, highs, lows, closes, volumes, timestamps = [], [], [], [], [], []
        start_time = datetime.datetime.now() - datetime.timedelta(minutes=5 * n_candles)

        p = support if trend_bias == "BULLISH" else resistance
        for i in range(n_candles):
            ts = start_time + datetime.timedelta(minutes=5 * i)
            drift = step * 0.4 if trend_bias == "BULLISH" else -step * 0.4
            p += drift + np.random.normal(0, step * 0.3)
            o = p
            h = o + abs(np.random.normal(step * 0.6, step * 0.2))
            l = o - abs(np.random.normal(step * 0.6, step * 0.2))
            c = (h + l) / 2 + (step * 0.2 if trend_bias == "BULLISH" else -step * 0.2)
            v = int(np.random.randint(15000, 50000))

            opens.append(round(o, 2))
            highs.append(round(max(o, c, h), 2))
            lows.append(round(min(o, c, l), 2))
            closes.append(round(c, 2))
            volumes.append(v)
            timestamps.append(ts.strftime("%Y-%m-%d %H:%M"))

        # Pin the last candle close to current_price
        closes[-1] = round(current_price, 2)
        highs[-1] = max(highs[-1], current_price + step * 0.3)
        lows[-1] = min(lows[-1], current_price - step * 0.3)

        return pd.DataFrame({
            "timestamp": timestamps,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes
        })

