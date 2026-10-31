"""
Command-Line Interface for QUANT-VISION PRO.
Enables rapid institutional analysis of any chart data file from the terminal.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
from core.quant_copilot import QuantVisionCopilot
from visualization.visual_reporter import render_terminal_dashboard
import config


def main():
    parser = argparse.ArgumentParser(description="QUANT-VISION PRO: Institutional Multi-Modal Quant Co-Pilot")
    parser.add_argument("--symbol", type=str, default="NIFTY 50", help="Market Symbol (e.g. NIFTY 50, BANKNIFTY, RELIANCE, GOLD (XAUUSD), BITCOIN (BTC/USDT))")
    parser.add_argument("--file", type=str, default=None, help="Optional path to custom OHLCV CSV file")
    parser.add_argument("--asset", type=str, default=None, help="Asset Name (defaults to symbol)")
    parser.add_argument("--timeframe", type=str, default="5 Min", help="Timeframe (e.g. 5 Min, 15 Min, 1 Hour)")
    parser.add_argument("--quantity", type=int, default=None, help="Custom quantity override (shares / units)")
    parser.add_argument("--capital", type=float, default=config.DEFAULT_CAPITAL, help="Trader Capital in INR / USD")
    parser.add_argument("--risk", type=float, default=config.DEFAULT_RISK_PER_TRADE, help="Max loss risk per trade")
    parser.add_argument("--context", type=str, default="Regular trading session, no major macro news", help="Market context or news")
    parser.add_argument("--output-md", type=str, default="analysis_report.md", help="Path to save markdown report")

    args = parser.parse_args()
    asset_name = args.asset or args.symbol

    from core.market_feed import MarketFeedManager
    from core.trading_segments import MarketTradingSegments

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        print(f"[*] Loading data from {file_path}...")
        df = MarketFeedManager.parse_broker_csv(file_path)
    else:
        print(f"[*] Scanning Market Feed for '{asset_name}'...")
        df = MarketFeedManager.generate_instrument_feed(asset_name)

    copilot = QuantVisionCopilot()
    print(f"[*] Running 4-Engine Quantitative Analysis on {asset_name} ({args.timeframe})...")
    output = copilot.analyze_market(
        df=df,
        asset_name=asset_name,
        timeframe=args.timeframe,
        user_capital=args.capital,
        user_max_risk=args.risk,
        market_context=args.context
    )

    if args.quantity and output.primary_trade_plan:
        output.primary_trade_plan.position_size = args.quantity
        output.primary_trade_plan.max_risk_amount = round(args.quantity * output.primary_trade_plan.risk_points, 2)
        print(f"[*] User custom quantity applied: {args.quantity} units (Total Risk: ₹{output.primary_trade_plan.max_risk_amount:,.2f})")

    # Print terminal dashboard
    print(render_terminal_dashboard(output))

    # Save to Persistent Activity History
    from core.history_manager import ActivityHistoryManager
    plan = output.primary_trade_plan
    ev = plan.ev_result if plan else None
    if plan and ev:
        ActivityHistoryManager.save_analysis(
            asset_name=asset_name,
            timeframe=args.timeframe,
            current_price=output.current_price,
            verdict=plan.action.value,
            confluence_score=plan.confluence_score,
            entry_price=plan.entry_price,
            stop_loss=plan.stop_loss,
            target_1=plan.target_1,
            target_2=plan.target_2,
            quantity=plan.position_size,
            lots=max(1, plan.position_size // MarketTradingSegments.get_lot_size(asset_name)),
            risk_amount=plan.max_risk_amount,
            risk_pct=round((plan.max_risk_amount / (args.capital + 1e-9)) * 100, 2),
            ev_amount=ev.ev_amount,
            win_rate=round(ev.win_probability * 100, 1),
            market_context=args.context,
            wyckoff_phase=output.wyckoff_phase.value
        )
        print(f"[+] Activity persisted to history store: {config.DATA_DIR / 'trade_history.json'}")

    # Save full Hinglish markdown
    out_path = Path(args.output_md)
    out_path.write_text(output.full_hinglish_markdown, encoding="utf-8")
    print(f"\n[+] Full 6-Section Hinglish Co-Pilot Report saved to: {out_path.resolve()}")


if __name__ == "__main__":
    main()

