"""
Engine 1: Vision & Pattern Engine.
Analyzes Candlesticks, Smart Money Concepts (SMC: Order Blocks, FVG, Liquidity Sweeps),
Wyckoff Phases, Classical S/R, and Volume Spread Analysis (VSA).
"""

from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from core.models import (
    Candle, OrderBlock, FairValueGap, LiquidityPool, PatternMatch,
    TrendDirection, WyckoffPhase
)
import config


class VisionPatternEngine:
    def __init__(self, atr_period: int = config.ATR_PERIOD):
        self.atr_period = atr_period

    def prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches OHLCV dataframe with EMAs, RSI, ATR, and Volume Moving Average.
        """
        data = df.copy()
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in data.columns:
                data[col] = data[col].astype(float)

        # EMAs
        data['ema20'] = data['close'].ewm(span=config.EMA_FAST, adjust=False).mean()
        data['ema50'] = data['close'].ewm(span=config.EMA_MID, adjust=False).mean()
        data['ema200'] = data['close'].ewm(span=config.EMA_SLOW, adjust=False).mean()

        # ATR (Average True Range)
        prev_close = data['close'].shift(1)
        tr1 = data['high'] - data['low']
        tr2 = (data['high'] - prev_close).abs()
        tr3 = (data['low'] - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        data['atr'] = tr.rolling(window=self.atr_period, min_periods=1).mean()

        # RSI (14)
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-9)
        data['rsi'] = 100 - (100 / (1 + rs))

        # Volume MA
        data['vol_ma20'] = data['volume'].rolling(window=20, min_periods=1).mean()

        return data

    def extract_candles(self, df: pd.DataFrame) -> List[Candle]:
        candles = []
        for i, row in df.iterrows():
            candles.append(
                Candle(
                    timestamp=str(row.get('timestamp', f'T_{i}')),
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['volume']),
                    index=int(i),
                    ema20=float(row.get('ema20', 0)),
                    ema50=float(row.get('ema50', 0)),
                    ema200=float(row.get('ema200', 0)),
                    rsi=float(row.get('rsi', 50)),
                    atr=float(row.get('atr', 1.0)),
                    vol_ma20=float(row.get('vol_ma20', 1.0))
                )
            )
        return candles

    def detect_candlestick_patterns(self, candles: List[Candle]) -> List[PatternMatch]:
        """
        Detects premier candlestick formations: Engulfing, Pinbars, Morning/Evening Star, Inside Bar.
        """
        patterns: List[PatternMatch] = []
        if len(candles) < 3:
            return patterns

        n = len(candles)
        # Scan last 10 candles for relevant formations
        start_idx = max(2, n - 10)

        for i in range(start_idx, n):
            c = candles[i]
            prev = candles[i - 1]
            prev2 = candles[i - 2]

            body = abs(c.close - c.open)
            candle_range = c.high - c.low + 1e-9
            upper_wick = c.high - max(c.open, c.close)
            lower_wick = min(c.open, c.close) - c.low

            prev_body = abs(prev.close - prev.open)
            prev_bullish = prev.close > prev.open
            curr_bullish = c.close > c.open

            # 1. Bullish Engulfing
            if not prev_bullish and curr_bullish and (c.close >= prev.open) and (c.open <= prev.close) and (body > prev_body * 1.05):
                patterns.append(
                    PatternMatch(
                        name="BULLISH_ENGULFING",
                        type="CANDLESTICK",
                        bias="BULLISH",
                        description=f"Strong bullish candle completely engulfs preceding bearish candle at bar {i}",
                        confidence=0.85,
                        candle_index=i
                    )
                )

            # 2. Bearish Engulfing
            elif prev_bullish and not curr_bullish and (c.open >= prev.close) and (c.close <= prev.open) and (body > prev_body * 1.05):
                patterns.append(
                    PatternMatch(
                        name="BEARISH_ENGULFING",
                        type="CANDLESTICK",
                        bias="BEARISH",
                        description=f"Bearish candle engulfs preceding green candle at bar {i}",
                        confidence=0.85,
                        candle_index=i
                    )
                )

            # 3. Hammer / Bullish Pinbar (long lower wick, tiny upper wick)
            if lower_wick >= 2.0 * body and upper_wick <= 0.3 * candle_range:
                patterns.append(
                    PatternMatch(
                        name="HAMMER_PINBAR",
                        type="CANDLESTICK",
                        bias="BULLISH",
                        description=f"Bullish rejection pinbar with lower wick {lower_wick:.2f} absorbing sell pressure at bar {i}",
                        confidence=0.80,
                        candle_index=i
                    )
                )

            # 4. Shooting Star / Bearish Pinbar (long upper wick, tiny lower wick)
            elif upper_wick >= 2.0 * body and lower_wick <= 0.3 * candle_range:
                patterns.append(
                    PatternMatch(
                        name="SHOOTING_STAR",
                        type="CANDLESTICK",
                        bias="BEARISH",
                        description=f"Bearish shooting star pinbar with upper wick {upper_wick:.2f} rejecting highs at bar {i}",
                        confidence=0.80,
                        candle_index=i
                    )
                )

            # 5. Morning Star (3-candle sequence: bear, star, strong bull)
            if (not prev2.close > prev2.open) and (abs(prev.close - prev.open) < candle_range * 0.35) and curr_bullish and (c.close > (prev2.open + prev2.close) / 2):
                patterns.append(
                    PatternMatch(
                        name="MORNING_STAR",
                        type="CANDLESTICK",
                        bias="BULLISH",
                        description=f"Morning Star reversal pattern completed across bars {i-2} to {i}",
                        confidence=0.88,
                        candle_index=i
                    )
                )

            # 6. Inside Bar
            if c.high <= prev.high and c.low >= prev.low:
                patterns.append(
                    PatternMatch(
                        name="INSIDE_BAR_BREAKOUT",
                        type="CANDLESTICK",
                        bias="NEUTRAL",
                        description=f"Inside Bar compression formed inside previous candle range at bar {i}",
                        confidence=0.72,
                        candle_index=i
                    )
                )

        return patterns

    def detect_order_blocks(self, candles: List[Candle]) -> List[OrderBlock]:
        """
        Detects Bullish and Bearish Order Blocks based on aggressive institutional displacement.
        """
        obs: List[OrderBlock] = []
        n = len(candles)
        if n < 6:
            return obs

        for i in range(2, n - 2):
            c_curr = candles[i]
            c_next1 = candles[i + 1]
            c_next2 = candles[i + 2]

            # Bullish Order Block: Red candle followed by strong multi-candle up move breaking highs
            if c_curr.close < c_curr.open:  # Down candle
                impulse_up = (c_next2.close - c_curr.high)
                atr = c_curr.atr or 1.0
                if impulse_up > 1.2 * atr and c_next1.close > c_next1.open:
                    # Check if subsequently mitigated
                    mitigated = any(candles[j].low <= c_curr.high for j in range(i + 3, n))
                    obs.append(
                        OrderBlock(
                            type="BULLISH_OB",
                            high=c_curr.high,
                            low=c_curr.low,
                            candle_index=i,
                            mitigated=mitigated,
                            strength=round(impulse_up / atr, 2)
                        )
                    )

            # Bearish Order Block: Green candle followed by strong downward displacement
            elif c_curr.close > c_curr.open:  # Up candle
                impulse_down = (c_curr.low - c_next2.close)
                atr = c_curr.atr or 1.0
                if impulse_down > 1.2 * atr and c_next1.close < c_next1.open:
                    mitigated = any(candles[j].high >= c_curr.low for j in range(i + 3, n))
                    obs.append(
                        OrderBlock(
                            type="BEARISH_OB",
                            high=c_curr.high,
                            low=c_curr.low,
                            candle_index=i,
                            mitigated=mitigated,
                            strength=round(impulse_down / atr, 2)
                        )
                    )

        return obs

    def detect_fair_value_gaps(self, candles: List[Candle]) -> List[FairValueGap]:
        """
        Detects Bullish FVGs (imbalance: Low[i+2] > High[i]) and Bearish FVGs.
        """
        fvgs: List[FairValueGap] = []
        n = len(candles)
        if n < 4:
            return fvgs

        for i in range(n - 3):
            c0 = candles[i]
            c1 = candles[i + 1]
            c2 = candles[i + 2]

            # Bullish FVG: Gap between candle 0 High and candle 2 Low
            if c2.low > c0.high and c1.close > c1.open:
                # Check if mitigated by future candles
                mitigated = any(candles[j].low <= c0.high for j in range(i + 3, n))
                fvgs.append(
                    FairValueGap(
                        type="BULLISH_FVG",
                        top=c2.low,
                        bottom=c0.high,
                        candle_index=i + 1,
                        mitigated=mitigated
                    )
                )

            # Bearish FVG: Gap between candle 0 Low and candle 2 High
            elif c2.high < c0.low and c1.close < c1.open:
                mitigated = any(candles[j].high >= c0.low for j in range(i + 3, n))
                fvgs.append(
                    FairValueGap(
                        type="BEARISH_FVG",
                        top=c0.low,
                        bottom=c2.high,
                        candle_index=i + 1,
                        mitigated=mitigated
                    )
                )

        return fvgs

    def detect_liquidity_sweeps(self, candles: List[Candle]) -> Tuple[List[LiquidityPool], List[PatternMatch]]:
        """
        Detects Sell-Side Liquidity (SSL) & Buy-Side Liquidity (BSL) sweeps / Stop Hunts.
        """
        pools: List[LiquidityPool] = []
        patterns: List[PatternMatch] = []
        n = len(candles)
        if n < 15:
            return pools, patterns

        # Find swing lows and swing highs in past 30 bars
        window = min(30, n - 2)
        recent_candles = candles[-window:]

        swing_lows = []
        swing_highs = []
        for i in range(2, len(recent_candles) - 2):
            c = recent_candles[i]
            if c.low < recent_candles[i-1].low and c.low < recent_candles[i-2].low and \
               c.low < recent_candles[i+1].low and c.low < recent_candles[i+2].low:
                swing_lows.append((c.low, c.index))

            if c.high > recent_candles[i-1].high and c.high > recent_candles[i-2].high and \
               c.high > recent_candles[i+1].high and c.high > recent_candles[i+2].high:
                swing_highs.append((c.high, c.index))

        last_candle = candles[-1]
        prev_candle = candles[-2]

        # Check for Sell-Side Liquidity Sweep (Spring)
        for s_low, idx in swing_lows:
            pools.append(LiquidityPool(type="SELLSIDE_LIQUIDITY", price=s_low, touches=1))
            # If last or prev candle pierced below swing low with wick, but closed above
            for c in [prev_candle, last_candle]:
                if c.low < s_low and c.close > s_low and c.index > idx:
                    patterns.append(
                        PatternMatch(
                            name="LIQUIDITY_SWEEP",
                            type="SMC",
                            bias="BULLISH",
                            description=f"Sell-Side Liquidity swept at {s_low:.2f} with quick wick reclaim (Wyckoff Spring / Stop Hunt)",
                            confidence=0.90,
                            candle_index=c.index
                        )
                    )
                    break

        # Check for Buy-Side Liquidity Sweep (Upthrust / Bull Trap)
        for s_high, idx in swing_highs:
            pools.append(LiquidityPool(type="BUYSIDE_LIQUIDITY", price=s_high, touches=1))
            for c in [prev_candle, last_candle]:
                if c.high > s_high and c.close < s_high and c.index > idx:
                    patterns.append(
                        PatternMatch(
                            name="LIQUIDITY_SWEEP",
                            type="SMC",
                            bias="BEARISH",
                            description=f"Buy-Side Liquidity swept at {s_high:.2f} followed by rejection back into range (UTAD / Bull Trap)",
                            confidence=0.88,
                            candle_index=c.index
                        )
                    )
                    break

        return pools, patterns

    def calculate_support_resistance(self, candles: List[Candle]) -> Tuple[float, float]:
        """
        Finds the primary active support and resistance levels.
        """
        highs = [c.high for c in candles[-40:]]
        lows = [c.low for c in candles[-40:]]
        last_close = candles[-1].close

        # Candidate resistance: minimum swing high strictly above current close
        candidates_r = [h for h in highs if h > last_close * 1.001]
        res = min(candidates_r) if candidates_r else max(highs)

        # Candidate support: maximum swing low strictly below current close
        candidates_s = [l for l in lows if l < last_close * 0.999]
        sup = max(candidates_s) if candidates_s else min(lows)

        return round(sup, 2), round(res, 2)

    def determine_trend_and_wyckoff(
        self, candles: List[Candle]
    ) -> Tuple[TrendDirection, WyckoffPhase, str]:
        """
        Identifies trend direction and Wyckoff phase.
        """
        last = candles[-1]
        c = last.close
        ema20 = last.ema20 or c
        ema50 = last.ema50 or c
        ema200 = last.ema200 or c

        # Trend Determination
        if c > ema20 and ema20 > ema50:
            trend = TrendDirection.BULLISH
        elif c < ema20 and ema20 < ema50:
            trend = TrendDirection.BEARISH
        else:
            trend = TrendDirection.SIDEWAYS

        # Volume status
        vol = last.volume
        vol_ma = last.vol_ma20 or 1.0
        if vol > config.VOLUME_SURGE_THRESHOLD * vol_ma:
            vol_status = "INSTITUTIONAL_SURGE"
        elif vol < 0.8 * vol_ma:
            vol_status = "LOW_VOLUME"
        else:
            vol_status = "NORMAL_VOLUME"

        # Wyckoff Phase Identification
        if trend == TrendDirection.BULLISH and c > ema200:
            phase = WyckoffPhase.MARKUP
        elif trend == TrendDirection.BEARISH and c < ema200:
            phase = WyckoffPhase.MARKDOWN
        elif trend == TrendDirection.SIDEWAYS:
            # Check if near lows (Accumulation) or near highs (Distribution)
            high_40 = max(x.high for x in candles[-30:])
            low_40 = min(x.low for x in candles[-30:])
            mid = (high_40 + low_40) / 2
            if c < mid:
                phase = WyckoffPhase.ACCUMULATION
            else:
                phase = WyckoffPhase.DISTRIBUTION
        else:
            phase = WyckoffPhase.CHOP_CONSOLIDATION

        return trend, phase, vol_status

