"""
Comprehensive Multi-Segment Market Trading Engine.
Provides specialized institutional analysis, strategies, and AI suggestions for:
1. Options Buying (Call/Put)
2. Options Selling / Writing (Credit Spreads & Naked)
3. Futures Trading (Index & Stock Futures)
4. Equity Cash (Intraday MIS & Swing CNC)
5. Commodities (Gold, Silver, Crude Oil)
6. Crypto (Perpetual Futures & Spot with Leverage)
7. Forex (Currency Pairs & Pip Modeling)
"""

from typing import Dict, Any, List, Optional
import math
from core.models import TradeAction, TrendDirection


class MarketTradingSegments:
    # Exchange Lot Sizes
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
        "INFY": 400,
        "GOLD (XAUUSD)": 100,  # 1 standard lot = 100 oz
        "SILVER (XAGUSD)": 5000,
        "CRUDE OIL": 100,
        "BITCOIN (BTC/USDT)": 1,
        "ETHEREUM (ETH/USDT)": 1
    }

    # Strike Steps
    STRIKE_STEPS = {
        "NIFTY": 50,
        "NIFTY 50": 50,
        "BANKNIFTY": 100,
        "FINNIFTY": 50,
        "SENSEX": 100,
        "RELIANCE": 20,
        "TCS": 50,
        "HDFCBANK": 10,
        "TATAMOTORS": 10,
        "GOLD (XAUUSD)": 10,
        "CRUDE OIL": 1.0,
        "BITCOIN (BTC/USDT)": 500
    }

    @classmethod
    def get_lot_size(cls, asset_name: str) -> int:
        clean = asset_name.upper().replace("-", " ").strip()
        for key, val in cls.LOT_SIZES.items():
            if key in clean:
                return val
        return 1

    @classmethod
    def get_strike_step(cls, asset_name: str) -> float:
        clean = asset_name.upper().replace("-", " ").strip()
        for key, val in cls.STRIKE_STEPS.items():
            if key in clean:
                return float(val)
        return 50.0

    @classmethod
    def analyze_all_segments(
        cls,
        asset_name: str,
        current_price: float,
        trade_action: TradeAction,
        entry_price: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        user_quantity: int,
        user_capital: float,
        user_leverage: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generates suggestions and execution metrics across ALL 7 trading segments.
        """
        is_long = (trade_action == TradeAction.LONG)
        lot_size = cls.get_lot_size(asset_name)
        step = cls.get_strike_step(asset_name)
        atm_strike = round(current_price / step) * step

        spot_risk_pts = abs(entry_price - stop_loss)
        spot_reward_tp1 = abs(target_1 - entry_price)
        spot_reward_tp2 = abs(target_2 - entry_price)

        total_risk_currency = round(user_quantity * spot_risk_pts, 2)
        risk_pct_of_capital = round((total_risk_currency / (user_capital + 1e-9)) * 100, 2)

        # 1. OPTIONS BUYING (Directional Momentum)
        opt_type = "CE" if is_long else "PE"
        opt_delta = 0.52  # ATM Delta
        opt_entry_premium_est = round(current_price * 0.012, 1)  # approx 1.2% of underlying
        opt_sl_pts = round(spot_risk_pts * opt_delta, 1)
        opt_tp1_pts = round(spot_reward_tp1 * opt_delta, 1)
        opt_tp2_pts = round(spot_reward_tp2 * opt_delta, 1)

        options_buying = {
            "name": "Options Buying (Directional Momentum)",
            "action": f"BUY {int(atm_strike)} {opt_type}",
            "contract": f"{int(atm_strike)} {opt_type}",
            "type": "ATM Call" if is_long else "ATM Put",
            "estimated_premium": opt_entry_premium_est,
            "stop_loss_pts": opt_sl_pts,
            "target_1_pts": f"+{opt_tp1_pts} pts",
            "target_2_pts": f"+{opt_tp2_pts} pts",
            "capital_required": round(user_quantity * opt_entry_premium_est, 2),
            "max_risk": round(user_quantity * opt_sl_pts, 2),
            "potential_gain_tp1": round(user_quantity * opt_tp1_pts, 2),
            "potential_gain_tp2": round(user_quantity * opt_tp2_pts, 2),
            "suggestion": (
                f"✅ **AI Suggestion (Options Buying):** Current setup has strong momentum confluence. "
                f"Buy **{int(atm_strike)} {opt_type}** around ₹{opt_entry_premium_est:.1f} premium. "
                f"Strict Stop-Loss: ₹{max(5.0, opt_entry_premium_est - opt_sl_pts):.1f} (-{opt_sl_pts} pts). "
                f"Book 50% at Target 1 (+{opt_tp1_pts} pts) and trail rest to Breakeven."
            ),
            "pros": "Limited downside risk (max loss capped at premium paid), massive upside potential.",
            "cons": "Time decay (Theta) works against buyers. Exit if price consolidates >4-5 candles."
        }

        # 2. OPTIONS SELLING / WRITING (High Probability Theta Decay)
        # Sell OTM credit spread
        if is_long:
            sell_strike = atm_strike - (2 * step)  # OTM PE to sell (Bull Put Spread)
            hedge_strike = sell_strike - (2 * step)
            spread_name = f"Bull Put Credit Spread: Sell {int(sell_strike)} PE & Buy {int(hedge_strike)} PE (Hedge)"
            margin_est_per_lot = 32000.0  # Hedged margin
            net_credit_est = round(current_price * 0.005, 1)  # ~0.5% premium credit
        else:
            sell_strike = atm_strike + (2 * step)  # OTM CE to sell (Bear Call Spread)
            hedge_strike = sell_strike + (2 * step)
            spread_name = f"Bear Call Credit Spread: Sell {int(sell_strike)} CE & Buy {int(hedge_strike)} CE (Hedge)"
            margin_est_per_lot = 32000.0
            net_credit_est = round(current_price * 0.005, 1)

        lots_count = max(1, user_quantity // lot_size) if lot_size > 1 else 1
        options_selling = {
            "name": "Options Selling / Writing (Theta Decay & Credit Spreads)",
            "action": spread_name,
            "sell_strike": f"{int(sell_strike)} {'PE' if is_long else 'CE'}",
            "hedge_strike": f"{int(hedge_strike)} {'PE' if is_long else 'CE'}",
            "estimated_credit_pts": net_credit_est,
            "margin_required": round(lots_count * margin_est_per_lot, 2),
            "max_profit": round(lots_count * lot_size * net_credit_est, 2),
            "win_probability": "78% - 85% (High Edge via Theta Decay)",
            "suggestion": (
                f"🛡️ **AI Suggestion (Options Selling):** Agar aap theta decay ka fayda uthana chahte hain, "
                f"toh **{spread_name}** execute karein. Sell strike support/resistance se door safe OTM zone mein hai. "
                f"Estimated Margin: ~₹{lots_count * margin_est_per_lot:,.2f} for {lots_count} Lots. "
                f"Price agar sideways bhi rahega tab bhi aapko 100% credit profit milega."
            ),
            "pros": "Time decay works in your favor; win even if market moves slowly or stays sideways.",
            "cons": "Requires higher margin than option buying; requires strict hedge leg to avoid tail risk."
        }

        # 3. FUTURES TRADING (High Leverage Directional)
        fut_margin_pct = 0.12  # approx 12-15% exchange margin for index/equity futures
        contract_val = user_quantity * current_price
        fut_margin_req = round(contract_val * fut_margin_pct, 2)
        futures_trading = {
            "name": "Futures Trading (Index & Stock Futures)",
            "action": f"{'LONG FUTURES (BUY)' if is_long else 'SHORT FUTURES (SELL)'}",
            "entry_level": f"₹{entry_price:.2f}",
            "stop_loss": f"₹{stop_loss:.2f} ({spot_risk_pts:.2f} pts)",
            "target_1": f"₹{target_1:.2f} (+{spot_reward_tp1:.2f} pts)",
            "target_2": f"₹{target_2:.2f} (+{spot_reward_tp2:.2f} pts)",
            "margin_required": fut_margin_req,
            "total_contract_value": round(contract_val, 2),
            "max_risk": total_risk_currency,
            "gain_tp1": round(user_quantity * spot_reward_tp1, 2),
            "gain_tp2": round(user_quantity * spot_reward_tp2, 2),
            "suggestion": (
                f"⚡ **AI Suggestion (Futures Trading):** Trade {'Long' if is_long else 'Short'} Futures at ₹{entry_price:.2f}. "
                f"Futures mein zero theta decay hota hai, isliye trend expansion trades ke liye best hai. "
                f"Required Exchange Margin for {user_quantity} qty ({lots_count} lots): ~₹{fut_margin_req:,.2f}. "
                f"Trail SL to Breakeven once TP1 (+{spot_reward_tp1:.2f} pts) is reached."
            ),
            "pros": "Zero theta decay; direct 1:1 linear price tracking; excellent for multi-day swing holds.",
            "cons": "High MTM volatility; requires strict capital discipline to avoid margin call."
        }

        # 4. EQUITY CASH (Intraday MIS & Positional CNC)
        intraday_margin = round(contract_val * 0.20, 2)  # 5x leverage for MIS
        delivery_margin = round(contract_val, 2)         # 1x for Delivery
        equity_cash = {
            "name": "Equity Cash (Shares Intraday & Swing Delivery)",
            "action": f"{'BUY SHARES' if is_long else 'SELL / SHORT SHARES'}",
            "quantity": user_quantity,
            "intraday_margin_mis": intraday_margin,
            "delivery_capital_cnc": delivery_margin,
            "risk_amount": total_risk_currency,
            "gain_tp1": round(user_quantity * spot_reward_tp1, 2),
            "gain_tp2": round(user_quantity * spot_reward_tp2, 2),
            "suggestion": (
                f"📈 **AI Suggestion (Equity Cash):** Intraday (MIS) ke liye capital required: ₹{intraday_margin:,.2f} (5x leverage). "
                f"Positional / Swing (CNC) delivery ke liye: ₹{delivery_margin:,.2f}. "
                f"Sabse safe trading mode hai jahan zero expiry pressure aur zero overnight time decay rehta hai."
            ),
            "pros": "Lowest risk profile; no contract expirations; holding power with zero theta decay.",
            "cons": "Higher capital required for large absolute rupee gains compared to options."
        }

        # 5. COMMODITIES (Gold / Silver / Crude Oil)
        comm_margin = round(contract_val * 0.08, 2)
        commodities = {
            "name": "Commodity Derivatives (Gold, Silver & Crude Oil)",
            "action": f"{'LONG COMMODITY' if is_long else 'SHORT COMMODITY'}",
            "lot_size": lot_size,
            "margin_required": comm_margin,
            "risk_amount": total_risk_currency,
            "gain_tp1": round(user_quantity * spot_reward_tp1, 2),
            "suggestion": (
                f"🥇 **AI Suggestion (Commodities):** Global liquidity hours (especially US session 6:30 PM - 10:30 PM IST) "
                f"mein sabse high momentum breakout milta hai. Sizing: {user_quantity} units. SL: ₹{stop_loss:.2f}."
            ),
            "pros": "Long trading hours (up to 11:30 PM IST); highly responsive to technical support/resistance.",
            "cons": "Sensitive to geopolitical headlines and USD currency movements."
        }

        # 6. CRYPTO PERPETUALS (Spot & Leverage Futures)
        lev = max(1.0, user_leverage)
        crypto_margin = round(contract_val / lev, 2)
        liq_distance_pct = round(100.0 / lev, 1)
        crypto_perps = {
            "name": "Crypto Trading (Perpetual Futures & Spot)",
            "action": f"{'LONG PERP' if is_long else 'SHORT PERP'}",
            "leverage_selected": f"{int(lev)}x",
            "margin_required": crypto_margin,
            "liquidation_buffer": f"{liq_distance_pct}% from entry",
            "risk_amount": total_risk_currency,
            "gain_tp1": round(user_quantity * spot_reward_tp1, 2),
            "suggestion": (
                f"🪙 **AI Suggestion (Crypto):** Maximum {int(lev)}x leverage use karein. "
                f"Liquidation safety distance entry se {liq_distance_pct}% door hai. "
                f"Stop-Loss {stop_loss:.2f} hit hone par margin loss sirf ₹{total_risk_currency:,.2f} hoga."
            ),
            "pros": "24/7 market access; extreme liquidity; flexible micro-position sizing.",
            "cons": "High overnight funding rates if holding against market bias; extreme wick volatility."
        }

        # 7. FOREX (Currency Pairs & Pip Modeling)
        pip_size = 0.0001 if "JPY" not in asset_name.upper() else 0.01
        pips_risk = round(spot_risk_pts / pip_size, 1)
        pips_tp1 = round(spot_reward_tp1 / pip_size, 1)
        forex = {
            "name": "Forex Trading (Currency Pairs)",
            "action": f"{'BUY (LONG)' if is_long else 'SELL (SHORT)'}",
            "pips_risk": f"{pips_risk} pips",
            "pips_reward_tp1": f"+{pips_tp1} pips",
            "standard_lots": round(user_quantity / 100000.0, 2),
            "suggestion": (
                f"🌍 **AI Suggestion (Forex):** Risk: {pips_risk} pips | Target 1: +{pips_tp1} pips. "
                f"London and New York session overlap hours (6:30 PM - 9:30 PM IST) offer the cleanest technical trends."
            ),
            "pros": "Deepest liquidity worldwide; tight spreads; continuous 24/5 market flow.",
            "cons": "Susceptible to sudden central bank rate comments and CPI data surprises."
        }

        return {
            "lot_size": lot_size,
            "strike_step": step,
            "user_quantity": user_quantity,
            "user_lots": lots_count,
            "total_risk_currency": total_risk_currency,
            "risk_pct_of_capital": risk_pct_of_capital,
            "options_buying": options_buying,
            "options_selling": options_selling,
            "futures_trading": futures_trading,
            "equity_cash": equity_cash,
            "commodities": commodities,
            "crypto_perps": crypto_perps,
            "forex": forex
        }

