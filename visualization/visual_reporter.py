"""
Visual Reporter for QUANT-VISION PRO.
Generates terminal cards, summary badges, and text-based decision flows.
"""

from core.models import AnalysisOutput, TradeAction


def render_terminal_dashboard(output: AnalysisOutput) -> str:
    plan = output.primary_trade_plan
    ev = plan.ev_result if plan else None

    lines = []
    lines.append("=" * 78)
    lines.append(f"  QUANT-VISION PRO :: INSTITUTIONAL TRADING CO-PILOT")
    lines.append(f"  Asset: {output.asset_name} ({output.timeframe}) | Price: ₹{output.current_price:.2f}")
    lines.append("=" * 78)

    lines.append(f"  VERDICT: {plan.action.value if plan else 'WAIT'} | CONFLUENCE SCORE: {plan.confluence_score if plan else 0}/100")
    lines.append(f"  Market Structure: {output.trend.value} | Wyckoff: {output.wyckoff_phase.value}")
    lines.append(f"  Support: ₹{output.key_support:.2f} | Resistance: ₹{output.key_resistance:.2f}")
    lines.append("-" * 78)

    if plan:
        lines.append(f"  [EXECUTION PLAN]")
        lines.append(f"  • Entry Trigger : {plan.entry_trigger}")
        lines.append(f"  • Stop-Loss     : ₹{plan.stop_loss:.2f} (Risk: {plan.risk_points:.2f} pts)")
        lines.append(f"  • Target 1 (TP1): ₹{plan.target_1:.2f} (Reward: {plan.reward_points_1:.2f} pts | R:R 1:1.5)")
        lines.append(f"  • Target 2 (TP2): ₹{plan.target_2:.2f} (Reward: {plan.reward_points_2:.2f} pts | R:R 1:2.8)")
        lines.append(f"  • Position Size : {plan.position_size} units (Max Risk: ₹{plan.max_risk_amount:,.2f})")
        if ev:
            lines.append(f"  • Math Expected Value (EV): +₹{ev.ev_amount:,.2f} per trade (Win-Rate: {ev.win_probability*100:.1f}%)")
    lines.append("-" * 78)

    lines.append("  [LOSS PREVENTION & FILTERS]")
    for f in output.filter_checks:
        status = "[PASS]" if f.passed else "[WARN]"
        lines.append(f"  {status} {f.filter_name}: {f.verdict}")

    lines.append("=" * 78)
    return "\n".join(lines)

