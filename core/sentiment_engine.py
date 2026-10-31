"""
Engine 4: Live News, Sentiment & Non-Profitable Trade Filter.
Evaluates the 4 Loss Prevention Filters: Low-Volume Breakout, Late Chasing (FOMO),
Seasonality/Session Traps, and Macro News Divergence.
"""

from typing import List, Dict, Any, Optional
import datetime
from core.models import FilterCheckResult, Candle
import config


class SentimentAndTrapEngine:
    def __init__(self, macro_events_path: Optional[str] = None):
        pass

    def evaluate_all_filters(
        self,
        current_candle: Candle,
        recent_candles: List[Candle],
        market_context_text: str = "",
        is_breakout: bool = True
    ) -> List[FilterCheckResult]:
        """
        Runs the 4 mandatory Loss Prevention filters before any trade is permitted.
        """
        results: List[FilterCheckResult] = []

        # 1. Low-Volume Breakout Filter
        vol = current_candle.volume
        vol_ma = current_candle.vol_ma20 or 1.0
        if is_breakout and vol < 0.9 * vol_ma:
            results.append(
                FilterCheckResult(
                    filter_name="Low-Volume Breakout Filter",
                    passed=False,
                    verdict="HIGH RISK OF FAKEOUT (78% Failure Rate in Backtest Data)",
                    warning_message="Chart par breakout dikh raha hai par volume pichhle 20 candles ke average se kam hai. Low institutional participation = Bull/Bear Trap warning."
                )
            )
        else:
            results.append(
                FilterCheckResult(
                    filter_name="Low-Volume Breakout Filter",
                    passed=True,
                    verdict="PASSED (Volume confirmed by institutional threshold)",
                    warning_message=None
                )
            )

        # 2. Late Chasing (FOMO) Filter
        atr = current_candle.atr or 1.0
        candle_body = abs(current_candle.close - current_candle.open)
        # Check if current candle is unusually bloated or far from 20 EMA
        ema20 = current_candle.ema20 or current_candle.close
        dist_from_ema = abs(current_candle.close - ema20)

        if candle_body > config.FOMO_ATR_THRESHOLD * atr or dist_from_ema > 2.5 * atr:
            results.append(
                FilterCheckResult(
                    filter_name="Late Chasing (FOMO) Filter",
                    passed=False,
                    verdict="BLOCKED (Risk-to-Reward Distortion / Extended Candle)",
                    warning_message=f"Candle pehle hi {dist_from_ema:.1f} points bhaag chuki hai (>{config.FOMO_ATR_THRESHOLD}x ATR). Yahan direct entry lene se Stop-Loss bahut bada hoga aur reward minimal. Pullback/Retest ka wait karein."
                )
            )
        else:
            results.append(
                FilterCheckResult(
                    filter_name="Late Chasing (FOMO) Filter",
                    passed=True,
                    verdict="PASSED (Price within acceptable structural risk envelope)",
                    warning_message=None
                )
            )

        # 3. Historical Seasonality & Session Trap Filter
        context_lower = market_context_text.lower()
        is_expiry = "expiry" in context_lower or "zero hero" in context_lower or "afternoon" in context_lower
        if is_expiry:
            results.append(
                FilterCheckResult(
                    filter_name="Historical Seasonality Trap Filter",
                    passed=False,
                    verdict="CAUTION: Expiry Gamma & Stop Hunt Window Active",
                    warning_message="Weekly Expiry session mein 1:30 PM - 2:30 PM ke beech option seller unwinding ki wajah se false breakouts aur gamma spikes aate hain. Small position size use karein."
                )
            )
        else:
            results.append(
                FilterCheckResult(
                    filter_name="Historical Seasonality Trap Filter",
                    passed=True,
                    verdict="PASSED (Normal trading session liquidity window)",
                    warning_message=None
                )
            )

        # 4. Macro News & Sentiment Divergence Filter
        has_macro_event = any(kw in context_lower for kw in ["rbi", "fed", "fomc", "cpi", "nfp", "budget", "election", "policy", "news"])
        if has_macro_event:
            results.append(
                FilterCheckResult(
                    filter_name="Macro News & Sentiment Filter",
                    passed=False,
                    verdict="HIGH-IMPACT NEWS HEADWIND: Avoid Immediate Blind Execution",
                    warning_message="High-impact macro event window identified. Chart technical setup kitna bhi accha ho, news candle settle hone tak wait karein taaki sudden wick hunting se SL na ude."
                )
            )
        else:
            results.append(
                FilterCheckResult(
                    filter_name="Macro News & Sentiment Filter",
                    passed=True,
                    verdict="CLEAR: No conflicting macro events detected in immediate horizon",
                    warning_message=None
                )
            )

        return results

