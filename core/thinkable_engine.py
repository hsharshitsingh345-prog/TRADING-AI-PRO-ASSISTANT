"""
"Thinkable Trading" Engine (Second-Order Institutional Cognition).
Generates the 5-Path "All Chart Possibilities" Matrix and the Live Dynamic Decision Tree.
"""

from typing import List, Dict, Any, Optional
from core.models import ChartScenario, LiveDecisionStep, Candle, TrendDirection, OrderBlock, FairValueGap
import config


class ThinkableTradingEngine:
    def __init__(self):
        pass

    def generate_all_possibilities_matrix(
        self,
        current_candle: Candle,
        key_support: float,
        key_resistance: float,
        order_blocks: List[OrderBlock],
        fvgs: List[FairValueGap],
        trend: TrendDirection
    ) -> List[ChartScenario]:
        """
        Maps out ALL 5 chart possibilities (Paths A through E) so the user is prepared
        and can extract profit under every conceivable market path.
        """
        c = current_candle.close
        atr = current_candle.atr or (c * 0.005)

        # Path A: Clean Breakout (Continuation)
        breakout_trigger = round(key_resistance + 0.1 * atr, 2)
        target_a = round(key_resistance + 2.5 * atr, 2)
        sl_a = round(key_resistance - 0.8 * atr, 2)

        scenario_a = ChartScenario(
            path_id="Path A",
            title="Clean Breakout (Trend Continuation)",
            market_behavior="High volume ke saath resistance tod kar candle upar close ho.",
            trigger_condition=f"Candle close above ₹{breakout_trigger:.2f} with Volume > 1.5x 20-MA.",
            trade_action="Momentum Buy (Long): Retest ya breakout candle high cross par entry.",
            entry=f"Above ₹{breakout_trigger:.2f}",
            stop_loss=f"₹{sl_a:.2f} (Breakout candle low)",
            target=f"₹{target_a:.2f} (1:2.5 R:R / Next Swing High)",
            is_recommended=(trend == TrendDirection.BULLISH)
        )

        # Path B: Bull Trap / Fakeout (Liquidity Grab)
        wick_high = round(key_resistance + 0.4 * atr, 2)
        trap_entry = round(key_resistance - 0.1 * atr, 2)
        trap_sl = round(wick_high + 0.3 * atr, 2)
        trap_target = round(key_support + 0.2 * atr, 2)

        scenario_b = ChartScenario(
            path_id="Path B",
            title="Bull Trap / Fakeout (Liquidity Grab Reversal)",
            market_behavior="Resistance ke upar wick maare (retail breakout buyers fasaane) aur wapas range ke andar close de.",
            trigger_condition=f"Price pierces ₹{wick_high:.2f} but closes back below ₹{key_resistance:.2f} with Bearish Pinbar.",
            trade_action="Trap Reversal (Short): Jahan retail fasa hai, wahan institutional short.",
            entry=f"Inside Range Close at ₹{trap_entry:.2f}",
            stop_loss=f"₹{trap_sl:.2f} (Wick high + buffer)",
            target=f"₹{trap_target:.2f} (Opposite Range Support / Fast 1:3 Move)",
            is_recommended=False
        )

        # Path C: Deep Pullback (SMC / Discount Entry)
        # 61.8% Fibonacci of range
        fib_discount = round(key_support + 0.382 * (key_resistance - key_support), 2)
        discount_sl = round(key_support - 0.5 * atr, 2)
        discount_tp = round(key_resistance + 1.5 * atr, 2)

        scenario_c = ChartScenario(
            path_id="Path C",
            title="Deep Pullback (SMC / Discount Entry)",
            market_behavior="Breakout se pehle neeche Bullish Order Block / Fair Value Gap ya 61.8% Fib tak dip maare.",
            trigger_condition=f"Price retraces to ₹{fib_discount:.2f} (Discount Zone <50%) aur rejection wick banaye.",
            trade_action="Sniper Limit Buy: Saste discount price par chhote SL ke saath maximum reward trade.",
            entry=f"At FVG / 61.8% Fib zone: ₹{fib_discount:.2f}",
            stop_loss=f"₹{discount_sl:.2f} (Below Order Block Low)",
            target=f"₹{discount_tp:.2f} (Previous Swing High & Structure Expansion)",
            is_recommended=(trend == TrendDirection.BULLISH)
        )

        # Path D: Sideways / ChopZone (Consolidation)
        chop_buy = round(key_support + 0.15 * (key_resistance - key_support), 2)
        chop_sell = round(key_resistance - 0.15 * (key_resistance - key_support), 2)
        chop_sl = round(key_support - 0.4 * atr, 2)

        scenario_d = ChartScenario(
            path_id="Path D",
            title="Sideways / ChopZone (Consolidation)",
            market_behavior="Low volume, candles ek dusre ke andar (Inside Bars), ADX < 20, directionless churn.",
            trigger_condition=f"Price remains bound between ₹{key_support:.2f} and ₹{key_resistance:.2f} with declining volume.",
            trade_action="Range Scalping ya Option Selling: Trend trade avoid karein, boundaries par scalp karein.",
            entry=f"Bottom 10% of Range (₹{chop_buy:.2f})",
            stop_loss=f"₹{chop_sl:.2f} (Tight Range Break)",
            target=f"₹{chop_sell:.2f} (Top 90% of Range)",
            is_recommended=(trend == TrendDirection.SIDEWAYS)
        )

        # Path E: Black Swan / News Spike
        scenario_e = ChartScenario(
            path_id="Path E",
            title="Black Swan / High-Impact News Spike",
            market_behavior="High-impact news se dono taraf badi-badi wicks (Stop-Loss hunting both sides).",
            trigger_condition="Sudden 3x ATR candle spikes during macro release window.",
            trade_action="Wait & Straddle Strategy: Pehle 15-minute high/low mark karke decisive breakout par trade karein.",
            entry="Post-News Structure Break (Candle close confirmation)",
            stop_loss="Mid-point of News Candle",
            target="Volatility Expansion Target (2.0x ATR)",
            is_recommended=False
        )

        return [scenario_a, scenario_b, scenario_c, scenario_d, scenario_e]

    def generate_live_decision_tree(
        self,
        entry_price: float,
        stop_loss: float,
        tp1: float,
        tp2: float,
        is_long: bool = True
    ) -> List[LiveDecisionStep]:
        """
        Builds the live If-This-Then-That dynamic execution tree for real-time monitoring.
        """
        steps = []
        if is_long:
            be_price = entry_price + 0.1 * (entry_price - stop_loss)
            steps.append(
                LiveDecisionStep(
                    condition=f"Price reaches TP1 (₹{tp1:.2f}) within 1-3 candles (Strong Momentum):",
                    instruction=f"Book 50% quantity instantly to lock cash-flow. Move Stop-Loss to Breakeven (₹{be_price:.2f}). Trade is now 100% Risk-Free.",
                    action_type="BOOK_PROFIT"
                )
            )
            steps.append(
                LiveDecisionStep(
                    condition=f"Price moves up but stalls around ₹{(entry_price + tp1)/2:.2f} for >4-5 candles (Time Decay / Exhaustion):",
                    instruction="Momentum dying out. Book 70-80% position right now and do not wait for full target. Protect capital from mean reversion.",
                    action_type="BOOK_PROFIT"
                )
            )
            steps.append(
                LiveDecisionStep(
                    condition=f"Price rejects upper zone and forms Bearish Pinbar or breaks below ₹{entry_price:.2f}:",
                    instruction=f"Cancel Long. Institutional rejection spotted. Exit long immediately; if candle closes below ₹{entry_price - (entry_price - stop_loss)*0.5:.2f}, consider flipping to SHORT.",
                    action_type="CANCEL_TRADE"
                )
            )
            steps.append(
                LiveDecisionStep(
                    condition=f"Price stays trapped between ₹{stop_loss:.2f} and ₹{entry_price:.2f} with dead volume:",
                    instruction="DO NOT OVERTRADE. Capital Protection Mode Active. Alert trigger ka wait karein.",
                    action_type="HOLD"
                )
            )
        else:
            steps.append(
                LiveDecisionStep(
                    condition=f"Price drops quickly to TP1 (₹{tp1:.2f}) in < 15 mins:",
                    instruction=f"Book 50% profit. Trail Stop-Loss to Cost (₹{entry_price:.2f}) for a zero-risk runner.",
                    action_type="BOOK_PROFIT"
                )
            )
            steps.append(
                LiveDecisionStep(
                    condition="Price struggles to make lower lows across 4 consecutive candles:",
                    instruction="Seller absorption detected. Tighten SL to previous bar high or take early 75% exit.",
                    action_type="BOOK_PROFIT"
                )
            )
            steps.append(
                LiveDecisionStep(
                    condition=f"Price reclaims above ₹{entry_price:.2f} with strong green candle:",
                    instruction="Bearish thesis invalidated. Close short trade immediately to avoid getting caught in short squeeze.",
                    action_type="CANCEL_TRADE"
                )
            )

        return steps

