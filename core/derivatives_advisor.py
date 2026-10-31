"""
Derivatives, Options & Leverage Advisor.
Provides strike selection (ATM/ITM), delta-adjusted option premium targets,
lot size calculations, and crypto/forex leverage risk modeling.
"""

from typing import Dict, Any, Optional
import math
from core.models import TradeAction


class DerivativesAdvisor:
    # Standard lot sizes
    LOT_SIZES = {
        "NIFTY": 25,
        "NIFTY 50": 25,
        "BANKNIFTY": 15,
        "FINNIFTY": 25,
        "MIDCPNIFTY": 50,
        "SENSEX": 10,
        "BANKEX": 15,
        "RELIANCE": 250,
        "TCS": 175,
        "HDFCBANK": 550,
        "TATAMOTORS": 700,
        "INFY": 400
    }

    # Strike step sizes
    STRIKE_STEPS = {
        "NIFTY": 50,
        "NIFTY 50": 50,
        "BANKNIFTY": 100,
        "FINNIFTY": 50,
        "SENSEX": 100,
        "RELIANCE": 20,
        "TCS": 50,
        "HDFCBANK": 10,
        "TATAMOTORS": 10
    }

    @classmethod
    def get_lot_size(cls, asset_name: str) -> int:
        clean = asset_name.upper().replace("-", " ").strip()
        for key, val in cls.LOT_SIZES.items():
            if key in clean:
                return val
        return 1  # Default for cash shares / crypto / forex

    @classmethod
    def get_strike_step(cls, asset_name: str) -> float:
        clean = asset_name.upper().replace("-", " ").strip()
        for key, val in cls.STRIKE_STEPS.items():
            if key in clean:
                return float(val)
        return 50.0

    @classmethod
    def calculate_options_strategy(
        cls,
        asset_name: str,
        current_price: float,
        trade_action: TradeAction,
        entry_price: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        total_quantity: int
    ) -> Dict[str, Any]:
        """
        Calculates recommended options strikes, delta-adjusted targets, and lot sizing.
        """
        lot_size = cls.get_lot_size(asset_name)
        step = cls.get_strike_step(asset_name)

        # ATM Strike
        atm_strike = round(current_price / step) * step

        is_bullish = (trade_action == TradeAction.LONG)
        opt_type = "CE" if is_bullish else "PE"

        # Slight ITM / ATM Strike
        if is_bullish:
            recommended_strike = atm_strike  # ATM CE
            itm_strike = atm_strike - step   # ITM CE
        else:
            recommended_strike = atm_strike  # ATM PE
            itm_strike = atm_strike + step   # ITM PE

        # Delta estimate for ATM is approx 0.50
        delta = 0.50
        spot_risk = abs(entry_price - stop_loss)
        spot_reward_tp1 = abs(target_1 - entry_price)
        spot_reward_tp2 = abs(target_2 - entry_price)

        opt_risk_pts = round(spot_risk * delta, 1)
        opt_tp1_pts = round(spot_reward_tp1 * delta, 1)
        opt_tp2_pts = round(spot_reward_tp2 * delta, 1)

        # Lot calculation
        calculated_lots = max(1, total_quantity // lot_size) if lot_size > 1 else total_quantity
        effective_qty = calculated_lots * lot_size if lot_size > 1 else calculated_lots

        return {
            "is_options_applicable": lot_size > 1 or "NIFTY" in asset_name.upper() or "BANK" in asset_name.upper(),
            "lot_size": lot_size,
            "recommended_lots": calculated_lots,
            "effective_quantity": effective_qty,
            "recommended_contract": f"{int(recommended_strike)} {opt_type}",
            "itm_contract": f"{int(itm_strike)} {opt_type}",
            "estimated_delta": delta,
            "option_sl_points": opt_risk_pts,
            "option_tp1_points": opt_tp1_pts,
            "option_tp2_points": opt_tp2_pts,
            "option_risk_per_lot": round(opt_risk_pts * lot_size, 2) if lot_size > 1 else round(opt_risk_pts, 2),
            "option_profit_tp1_per_lot": round(opt_tp1_pts * lot_size, 2) if lot_size > 1 else round(opt_tp1_pts, 2),
            "option_profit_tp2_per_lot": round(opt_tp2_pts * lot_size, 2) if lot_size > 1 else round(opt_tp2_pts, 2),
        }

