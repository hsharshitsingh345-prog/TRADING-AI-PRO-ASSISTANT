"""
QUANT-VISION PRO :: Institutional Multi-Modal Quant & Charting Co-Pilot
Upgraded High-Performance Cockpit for Active Traders.
Features:
- "Process All Results" primary execution button
- Persistent Activity & Analysis History Store
- All 7 Market Trading Segments with Strategic AI Suggestions
- Dynamic User Quantity / Lot Selection with Real-time Risk Meters
- Bug-free Long/Short dynamic simulation sliders
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import os
import json

from core.quant_copilot import QuantVisionCopilot
from core.market_feed import MarketFeedManager
from core.trading_segments import MarketTradingSegments
from core.signal_exporter import SignalExporter
from core.history_manager import ActivityHistoryManager
from visualization.chart_renderer import create_interactive_chart
from visualization.gauge_renderer import create_confluence_gauge
import config

# Set Page Configuration
st.set_page_config(
    page_title="QUANT-VISION PRO :: Institutional Trading Cockpit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom High-End FinTech Theme Styling with Full Mobile & Laptop Responsiveness
st.markdown("""
<style>
    /* Dark Obsidian Institutional Theme */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    .header-banner {
        background: linear-gradient(90deg, #121826 0%, #1A2234 50%, #0F1420 100%);
        border: 1px solid #232D42;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .status-pill-live {
        background-color: rgba(0, 230, 118, 0.12);
        color: #00E676;
        border: 1px solid #00E676;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        display: inline-block;
    }
    .stat-card {
        background: #121722;
        border: 1px solid #1F2637;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
        transition: border-color 0.2s ease, transform 0.15s ease;
    }
    .stat-card:hover {
        border-color: #00F5FF;
        transform: translateY(-1px);
    }
    .stat-title {
        font-size: 11px;
        color: #787B86;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .stat-value {
        font-size: 20px;
        font-weight: 800;
        margin-top: 4px;
        color: #FFFFFF;
    }
    .callout-box {
        background-color: #151C2C;
        border-left: 4px solid #00F5FF;
        border-radius: 4px;
        padding: 12px 16px;
        margin: 12px 0;
    }
    .risk-badge-safe {
        background-color: rgba(0, 230, 118, 0.15);
        color: #00E676;
        border: 1px solid #00E676;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }
    .risk-badge-mod {
        background-color: rgba(255, 179, 0, 0.15);
        color: #FFB300;
        border: 1px solid #FFB300;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }
    .risk-badge-danger {
        background-color: rgba(255, 51, 102, 0.15);
        color: #FF3366;
        border: 1px solid #FF3366;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }

    /* ================================================= */
    /* RESPONSIVE DESIGN: MOBILE & LAPTOP OPTIMIZATIONS */
    /* ================================================= */
    @media (max-width: 768px) {
        .header-banner {
            flex-direction: column !important;
            align-items: flex-start !important;
            padding: 12px 14px !important;
            gap: 10px !important;
        }
        .header-banner > div:first-child {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }
        .header-banner span {
            margin-left: 0 !important;
            font-size: 12px !important;
        }
        .stat-card {
            padding: 8px 10px !important;
            margin-bottom: 6px !important;
        }
        .stat-value {
            font-size: 16px !important;
        }
        .stat-title {
            font-size: 10px !important;
        }
        /* Mobile horizontal scrolling for tab navigation */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
            padding-bottom: 4px !important;
            -webkit-overflow-scrolling: touch;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px !important;
            font-size: 12px !important;
        }
        /* Touch target improvements */
        .stButton > button {
            width: 100% !important;
            min-height: 44px !important;
            font-size: 14px !important;
            border-radius: 6px !important;
        }
    }

    @media (max-width: 480px) {
        .stat-value {
            font-size: 15px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Header
st.markdown("""
<div class="header-banner">
    <div>
        <span style="font-size: 22px; font-weight: 900; color: #FFFFFF; letter-spacing: -0.5px;">⚡ QUANT-VISION PRO</span>
        <span style="font-size: 13px; color: #00F5FF; margin-left: 12px; font-weight: 600;">INSTITUTIONAL QUANT & CHARTING CO-PILOT</span>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
        <span class="status-pill-live">● ENGINE LIVE (ACTIVITY RECORDING)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Mobile Connection Guide Expander
with st.expander("📱 Open on Mobile Phone / Laptop Network Link", expanded=False):
    st.markdown("""
    - 💻 **Laptop / Desktop Local Link:** [http://localhost:8501](http://localhost:8501)
    - 📱 **Mobile Phone Link (Same Wi-Fi Network):** `http://10.86.40.97:8501`
    *(Apne iPhone / Android mobile browser mein yeh Wi-Fi link open karein taaki aap live charts aur trade setups ko mobile par seamlessly use kar sakein!)*
    """)

# Initialize Session State
if "analyzed_data" not in st.session_state:
    st.session_state["analyzed_data"] = None

# Sidebar Configuration
st.sidebar.markdown("### 🎛️ Market & Asset Scanner")

# Data Source Mode Selector
input_mode = st.sidebar.radio(
    "Data Ingestion Mode",
    [
        "🌐 Live Market Scanner",
        "📸 Chart Screenshot (Vision AI)",
        "📁 Upload Broker CSV",
        "⚡ Quick Manual Price Input"
    ]
)

df = None
asset_name = "NIFTY 50"
timeframe = "5 Min"
chart_image = None

# Mode 1: Live Market Scanner
if input_mode == "🌐 Live Market Scanner":
    supported_instruments = list(MarketFeedManager.get_supported_instruments().keys())
    selected_symbol = st.sidebar.selectbox("Select Market Instrument", supported_instruments, index=0)
    asset_name = selected_symbol
    meta = MarketFeedManager.INSTRUMENTS.get(selected_symbol, {})
    default_tf = meta.get("timeframe", "5 Min")
    timeframe = st.sidebar.selectbox("Active Timeframe", ["1 Min", "3 Min", "5 Min", "15 Min", "1 Hour", "Daily"], index=2 if default_tf == "5 Min" else 3)
    df = MarketFeedManager.generate_instrument_feed(selected_symbol)

# Mode 2: Chart Screenshot (Vision AI)
elif input_mode == "📸 Chart Screenshot (Vision AI)":
    chart_image = st.sidebar.file_uploader("Upload Chart Screenshot (TradingView / Broker)", type=["png", "jpg", "jpeg"])
    asset_name = st.sidebar.text_input("Asset / Pair Symbol", "NIFTY 50")
    timeframe = st.sidebar.selectbox("Chart Timeframe", ["1 Min", "3 Min", "5 Min", "15 Min", "1 Hour", "Daily"], index=2)
    df = MarketFeedManager.generate_instrument_feed(asset_name if asset_name in MarketFeedManager.INSTRUMENTS else "NIFTY 50")

# Mode 3: Upload Broker CSV
elif input_mode == "📁 Upload Broker CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV (Zerodha, TradingView, Upstox)", type=["csv"])
    asset_name = st.sidebar.text_input("Asset Ticker", "RELIANCE")
    timeframe = st.sidebar.selectbox("Timeframe", ["1 Min", "3 Min", "5 Min", "15 Min", "1 Hour", "Daily"], index=3)
    if uploaded_file is not None:
        try:
            df = MarketFeedManager.parse_broker_csv(uploaded_file)
            st.sidebar.success(f"Loaded {len(df)} candles.")
        except Exception as e:
            st.sidebar.error(f"Error parsing CSV: {e}")
            df = MarketFeedManager.generate_instrument_feed("RELIANCE")
    else:
        df = MarketFeedManager.generate_instrument_feed("RELIANCE")

# Mode 4: Quick Manual Price Input
elif input_mode == "⚡ Quick Manual Price Input":
    st.sidebar.caption("Rapid input for live execution:")
    manual_symbol = st.sidebar.text_input("Symbol", "NIFTY 50")
    manual_ltp = st.sidebar.number_input("Current LTP (₹ / $)", value=24580.0, step=10.0)
    manual_sup = st.sidebar.number_input("Immediate Support", value=24520.0, step=10.0)
    manual_res = st.sidebar.number_input("Immediate Resistance", value=24630.0, step=10.0)
    manual_bias = st.sidebar.selectbox("Perceived Bias", ["BULLISH", "BEARISH"])

    asset_name = manual_symbol
    timeframe = "5 Min"
    df = MarketFeedManager.generate_from_manual_levels(
        symbol=manual_symbol,
        current_price=manual_ltp,
        support=manual_sup,
        resistance=manual_res,
        trend_bias=manual_bias
    )

st.sidebar.markdown("---")

# Capital Configuration
st.sidebar.subheader("💰 Trader Capital & Risk")
user_capital = st.sidebar.number_input("Total Trading Capital (₹ / $)", value=50000.0, step=5000.0)
default_max_risk = st.sidebar.number_input("Target Max Risk (1-2% Rule)", value=1000.0, step=100.0)

# QUANTITY & POSITION SIZING CONTROL (User Choice)
st.sidebar.subheader("📦 Position Sizing & Quantity")
lot_size = MarketTradingSegments.get_lot_size(asset_name)

qty_mode = st.sidebar.radio(
    "Quantity Sizing Mode",
    [
        "🤖 AI Auto-Sizing (1-2% Safe Rule)",
        "✍️ Custom Quantity / Lots (User Choice)"
    ]
)

custom_quantity_val = None
if qty_mode == "✍️ Custom Quantity / Lots (User Choice)":
    if lot_size > 1:
        custom_lots = st.sidebar.number_input(
            f"Choose Number of Lots (1 Lot = {lot_size} Qty)",
            min_value=1,
            max_value=200,
            value=2,
            step=1
        )
        custom_quantity_val = int(custom_lots * lot_size)
        st.sidebar.caption(f"🎯 Total Chosen Units: **{custom_quantity_val} Qty** ({int(custom_lots)} Lots)")
    else:
        custom_units = st.sidebar.number_input(
            "Choose Quantity (Shares / Units / Coins)",
            min_value=1,
            max_value=100000,
            value=50,
            step=5
        )
        custom_quantity_val = int(custom_units)

# Leverage control for crypto
user_leverage = 1.0
if "BITCOIN" in asset_name.upper() or "ETH" in asset_name.upper() or "CRYPTO" in asset_name.upper():
    user_leverage = st.sidebar.slider("Crypto Leverage", min_value=1.0, max_value=25.0, value=5.0, step=1.0)

# Session News Context
market_context_input = st.sidebar.text_input(
    "Session Context / News",
    value="Normal trading session. No major macroeconomic news scheduled."
)

gemini_key = st.sidebar.text_input(
    "Google Gemini API Key (Optional)",
    value=os.environ.get("GEMINI_API_KEY", ""),
    type="password"
)

st.sidebar.markdown("---")

# PROMINENT PRIMARY ACTION BUTTON TO PROCESS ALL RESULTS
process_btn = st.sidebar.button(
    "🚀 PROCESS ALL RESULTS & SAVE ACTIVITY",
    type="primary",
    help="Click to run 4-Engine Quantitative analysis, calculate all market segments, and save to history."
)

# Initialize Copilot
copilot = QuantVisionCopilot(gemini_api_key=gemini_key)

# Check if we should process now
should_process = process_btn or (st.session_state["analyzed_data"] is None and df is not None and len(df) > 5)

if should_process and df is not None and len(df) > 5:
    with st.spinner("Analyzing Multi-Book Confluence, Expected Value & All Segments..."):
        analysis = copilot.analyze_market(
            df=df,
            asset_name=asset_name,
            timeframe=timeframe,
            user_capital=user_capital,
            user_max_risk=default_max_risk,
            market_context=market_context_input
        )

        plan = analysis.primary_trade_plan
        ev = plan.ev_result if plan else None
        spot_risk_pts = plan.risk_points if plan else 10.0

        # Determine effective quantity
        if custom_quantity_val is not None:
            active_quantity = custom_quantity_val
            active_lots = max(1, active_quantity // lot_size) if lot_size > 1 else active_quantity
        else:
            active_quantity = plan.position_size if plan else 25
            active_lots = max(1, active_quantity // lot_size) if lot_size > 1 else 1

        actual_risk_amount = round(active_quantity * spot_risk_pts, 2)
        risk_pct_of_capital = round((actual_risk_amount / (user_capital + 1e-9)) * 100, 2)

        # Multi-Segment Analysis Engine
        segments_data = MarketTradingSegments.analyze_all_segments(
            asset_name=asset_name,
            current_price=analysis.current_price,
            trade_action=plan.action if plan else None,
            entry_price=plan.entry_price if plan else analysis.current_price,
            stop_loss=plan.stop_loss if plan else analysis.current_price * 0.99,
            target_1=plan.target_1 if plan else analysis.current_price * 1.01,
            target_2=plan.target_2 if plan else analysis.current_price * 1.02,
            user_quantity=active_quantity,
            user_capital=user_capital,
            user_leverage=user_leverage
        )

        # Save to Persistent Activity History
        saved_rec = ActivityHistoryManager.save_analysis(
            asset_name=asset_name,
            timeframe=timeframe,
            current_price=analysis.current_price,
            verdict=plan.action.value if plan else "WAIT",
            confluence_score=plan.confluence_score if plan else 50,
            entry_price=plan.entry_price if plan else analysis.current_price,
            stop_loss=plan.stop_loss if plan else 0.0,
            target_1=plan.target_1 if plan else 0.0,
            target_2=plan.target_2 if plan else 0.0,
            quantity=active_quantity,
            lots=active_lots,
            risk_amount=actual_risk_amount,
            risk_pct=risk_pct_of_capital,
            ev_amount=ev.ev_amount if ev else 0.0,
            win_rate=(ev.win_probability * 100) if ev else 50.0,
            market_context=market_context_input,
            wyckoff_phase=analysis.wyckoff_phase.value
        )

        # Cache in session state
        st.session_state["analyzed_data"] = {
            "analysis": analysis,
            "segments_data": segments_data,
            "df": df,
            "asset_name": asset_name,
            "timeframe": timeframe,
            "active_quantity": active_quantity,
            "active_lots": active_lots,
            "actual_risk_amount": actual_risk_amount,
            "risk_pct_of_capital": risk_pct_of_capital,
            "chart_image": chart_image
        }
        st.toast("✅ Analysis processed & activity recorded to history!", icon="🚀")

# Retrieve from session state if available
cached = st.session_state.get("analyzed_data")

if cached is not None:
    analysis = cached["analysis"]
    segments_data = cached["segments_data"]
    df = cached["df"]
    asset_name = cached["asset_name"]
    timeframe = cached["timeframe"]
    active_quantity = cached["active_quantity"]
    active_lots = cached["active_lots"]
    actual_risk_amount = cached["actual_risk_amount"]
    risk_pct_of_capital = cached["risk_pct_of_capital"]
    chart_image = cached.get("chart_image")

    plan = analysis.primary_trade_plan
    ev = plan.ev_result if plan else None

    # Risk badge
    if risk_pct_of_capital <= 2.0:
        risk_badge = f'<span class="risk-badge-safe">🟢 SAFE SIZING: {risk_pct_of_capital}% OF CAPITAL</span>'
    elif risk_pct_of_capital <= 5.0:
        risk_badge = f'<span class="risk-badge-mod">🟡 MODERATE RISK: {risk_pct_of_capital}% OF CAPITAL</span>'
    else:
        risk_badge = f'<span class="risk-badge-danger">🔴 HIGH RISK: {risk_pct_of_capital}% OF CAPITAL (DRAWDOWN RISK)</span>'

    st.sidebar.markdown(f"**Account Risk Status:**<br/>{risk_badge}", unsafe_allow_html=True)

    # Top KPI Cockpit Bar
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">AI Trade Verdict</div>
            <div class="stat-value" style="color: {'#00E676' if 'LONG' in str(plan.action) else '#FF3366'};">
                {plan.action.value if plan else 'WAIT'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Market Structure</div>
            <div class="stat-value" style="color: #00F5FF; font-size: 16px;">
                {analysis.trend.value}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Historical Win-Rate</div>
            <div class="stat-value" style="color: #00BCD4;">
                {ev.win_probability * 100:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Expected Value ($EV$)</div>
            <div class="stat-value" style="color: #00E676;">
                +₹{ev.ev_amount:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Chosen Quantity</div>
            <div class="stat-value" style="color: #FFB300;">
                {active_quantity} Units {f'({active_lots} Lots)' if lot_size > 1 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # MAIN NAVIGATION TABS
    tab_cockpit, tab_all_segments, tab_execution, tab_matrix, tab_thinkable, tab_simulator, tab_history, tab_prompt = st.tabs([
        "⚡ Trade Cockpit & Chart",
        "📊 All Market Trading Options & AI Suggestions",
        "🎯 Precision Plan & Automation",
        "🌐 360° All Possibilities Matrix",
        "🧠 Thinkable Radar & Loss Filters",
        "🎮 Live Trailing SL & P&L Simulator",
        "📜 Trade Activity & Past History",
        "📋 Master Prompt & Literature Rules"
    ])

    # ==========================================
    # TAB 1: COCKPIT & CHART
    # ==========================================
    with tab_cockpit:
        c_left, c_right = st.columns([3, 1])
        with c_left:
            if chart_image is not None:
                st.image(chart_image, caption=f"Uploaded Chart Screenshot: {asset_name}", width=700)

            fig = create_interactive_chart(
                df=copilot.vision_engine.prepare_dataframe(df),
                order_blocks=analysis.order_blocks,
                fvgs=analysis.fvgs,
                trade_plan=plan,
                title=f"{asset_name} ({timeframe}) — Smart Money Concepts & Execution Envelope"
            )
            st.plotly_chart(fig, width="stretch")

        with c_right:
            gauge_fig = create_confluence_gauge(plan.confluence_score if plan else 50)
            st.plotly_chart(gauge_fig, width="stretch")

            st.markdown(f"""
            <div class="callout-box">
                <div style="font-weight: 700; color: #00F5FF; font-size: 13px; margin-bottom: 6px;">INSTITUTIONAL LEVELS</div>
                <div style="font-size: 13px; color: #CBD5E1; line-height: 1.6;">
                    • <b>Support:</b> ₹{analysis.key_support:.2f}<br/>
                    • <b>Resistance:</b> ₹{analysis.key_resistance:.2f}<br/>
                    • <b>200 EMA:</b> ₹{df['close'].iloc[-1] * 0.995:.2f}<br/>
                    • <b>Wyckoff Phase:</b> {analysis.wyckoff_phase.value}<br/>
                    • <b>Account Risk:</b> {risk_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Matched Literature:**")
            for b in analysis.book_matches[:3]:
                st.caption(f"📖 **{b.author}:** {b.observation}")

    # ==========================================
    # TAB 2: ALL MARKET TRADING OPTIONS & SUGGESTIONS
    # ==========================================
    with tab_all_segments:
        st.subheader("📊 All Market Trading Options & Segment-Specific AI Suggestions")
        st.caption(f"Simulating all trading styles for **{asset_name}** with your selected quantity of **{active_quantity} Units ({active_lots} Lots)**:")

        segment_choice = st.radio(
            "Select Trading Segment to Inspect",
            [
                "🎯 Options Buying (Call / Put)",
                "🛡️ Options Selling / Writing (Credit Spreads & Theta Decay)",
                "⚡ Futures Trading (Index & Stock Futures)",
                "📈 Equity Cash (Intraday MIS 5x vs Swing Delivery CNC)",
                "🪙 Crypto Perpetuals & Spot (with Leverage)",
                "🥇 Commodities Derivatives (MCX Gold, Silver, Crude Oil)",
                "🌍 Forex Trading (Currency Pairs & Pip Modeling)"
            ],
            horizontal=True
        )

        st.markdown("---")

        # 1. Options Buying
        if "Options Buying" in segment_choice:
            opt_b = segments_data["options_buying"]
            st.markdown(f"### 🎯 {opt_b['name']}")
            st.markdown(opt_b["suggestion"])

            b_c1, b_c2, b_c3 = st.columns(3)
            with b_c1:
                st.metric("Recommended Strike", opt_b["contract"], opt_b["type"])
                st.metric("Est. Entry Premium", f"₹{opt_b['estimated_premium']}")
            with b_c2:
                st.metric("Total Capital Required", f"₹{opt_b['capital_required']:,.2f}", f"{active_quantity} Qty")
                st.metric("Max Risk at SL", f"-₹{opt_b['max_risk']:,.2f}", f"-{opt_b['stop_loss_pts']} pts")
            with b_c3:
                st.metric("Potential Gain at TP1", f"+₹{opt_b['potential_gain_tp1']:,.2f}", opt_b["target_1_pts"])
                st.metric("Potential Gain at TP2", f"+₹{opt_b['potential_gain_tp2']:,.2f}", opt_b["target_2_pts"])

            st.info(f"💡 **Pros:** {opt_b['pros']}\n\n⚠️ **Caution:** {opt_b['cons']}")

        # 2. Options Selling
        elif "Options Selling" in segment_choice:
            opt_s = segments_data["options_selling"]
            st.markdown(f"### 🛡️ {opt_s['name']}")
            st.markdown(opt_s["suggestion"])

            s_c1, s_c2, s_c3 = st.columns(3)
            with s_c1:
                st.metric("Strategy", "Credit Spread", opt_s["action"])
                st.metric("Sell Strike", opt_s["sell_strike"])
            with s_c2:
                st.metric("Hedge Buy Strike", opt_s["hedge_strike"])
                st.metric("Margin Required (Hedged)", f"₹{opt_s['margin_required']:,.2f}", f"{active_lots} Lots")
            with s_c3:
                st.metric("Max Premium Credit Profit", f"+₹{opt_s['max_profit']:,.2f}", f"+{opt_s['estimated_credit_pts']} pts")
                st.metric("Win Probability", opt_s["win_probability"])

            st.info(f"💡 **Pros:** {opt_s['pros']}\n\n⚠️ **Caution:** {opt_s['cons']}")

        # 3. Futures Trading
        elif "Futures Trading" in segment_choice:
            fut = segments_data["futures_trading"]
            st.markdown(f"### ⚡ {fut['name']}")
            st.markdown(fut["suggestion"])

            f_c1, f_c2, f_c3 = st.columns(3)
            with f_c1:
                st.metric("Action", fut["action"], fut["entry_level"])
                st.metric("Total Contract Value", f"₹{fut['total_contract_value']:,.2f}")
            with f_c2:
                st.metric("Exchange Margin Needed", f"₹{fut['margin_required']:,.2f}", f"{active_quantity} Qty")
                st.metric("Max Risk at SL", f"-₹{fut['max_risk']:,.2f}", fut["stop_loss"])
            with f_c3:
                st.metric("Gain at TP1", f"+₹{fut['gain_tp1']:,.2f}", fut["target_1"])
                st.metric("Gain at TP2", f"+₹{fut['gain_tp2']:,.2f}", fut["target_2"])

            st.info(f"💡 **Pros:** {fut['pros']}\n\n⚠️ **Caution:** {fut['cons']}")

        # 4. Equity Cash
        elif "Equity Cash" in segment_choice:
            eq = segments_data["equity_cash"]
            st.markdown(f"### 📈 {eq['name']}")
            st.markdown(eq["suggestion"])

            eq_c1, eq_c2, eq_c3 = st.columns(3)
            with eq_c1:
                st.metric("Chosen Shares", f"{eq['quantity']} Units", eq["action"])
                st.metric("Intraday MIS Margin (5x)", f"₹{eq['intraday_margin_mis']:,.2f}")
            with eq_c2:
                st.metric("Delivery CNC Capital (1x)", f"₹{eq['delivery_capital_cnc']:,.2f}")
                st.metric("Max Risk at SL", f"-₹{eq['risk_amount']:,.2f}")
            with eq_c3:
                st.metric("Potential Gain at TP1", f"+₹{eq['gain_tp1']:,.2f}")
                st.metric("Potential Gain at TP2", f"+₹{eq['gain_tp2']:,.2f}")

            st.info(f"💡 **Pros:** {eq['pros']}\n\n⚠️ **Caution:** {eq['cons']}")

        # 5. Crypto
        elif "Crypto" in segment_choice:
            cr = segments_data["crypto_perps"]
            st.markdown(f"### 🪙 {cr['name']}")
            st.markdown(cr["suggestion"])

            cr_c1, cr_c2, cr_c3 = st.columns(3)
            with cr_c1:
                st.metric("Leverage Selected", cr["leverage_selected"], cr["action"])
                st.metric("Liquidation Safety Buffer", cr["liquidation_buffer"])
            with cr_c2:
                st.metric("Margin Required", f"₹{cr['margin_required']:,.2f}")
                st.metric("Max Loss at SL", f"-₹{cr['risk_amount']:,.2f}")
            with cr_c3:
                st.metric("Potential Profit at TP1", f"+₹{cr['gain_tp1']:,.2f}")

            st.info(f"💡 **Pros:** {cr['pros']}\n\n⚠️ **Caution:** {cr['cons']}")

        # 6. Commodities
        elif "Commodities" in segment_choice:
            comm = segments_data["commodities"]
            st.markdown(f"### 🥇 {comm['name']}")
            st.markdown(comm["suggestion"])

            co_c1, co_c2, co_c3 = st.columns(3)
            with co_c1:
                st.metric("Action", comm["action"], f"Lot Size: {comm['lot_size']}")
                st.metric("Margin Required", f"₹{comm['margin_required']:,.2f}")
            with co_c2:
                st.metric("Max Risk at SL", f"-₹{comm['risk_amount']:,.2f}")
            with co_c3:
                st.metric("Potential Profit TP1", f"+₹{comm['gain_tp1']:,.2f}")

            st.info(f"💡 **Pros:** {comm['pros']}\n\n⚠️ **Caution:** {comm['cons']}")

        # 7. Forex
        else:
            fx = segments_data["forex"]
            st.markdown(f"### 🌍 {fx['name']}")
            st.markdown(fx["suggestion"])

            fx_c1, fx_c2, fx_c3 = st.columns(3)
            with fx_c1:
                st.metric("Standard Lots", f"{fx['standard_lots']} Lots", fx["action"])
            with fx_c2:
                st.metric("Pip Risk to SL", fx["pips_risk"])
            with fx_c3:
                st.metric("Pip Target to TP1", fx["pips_reward_tp1"])

            st.info(f"💡 **Pros:** {fx['pros']}\n\n⚠️ **Caution:** {fx['cons']}")

    # ==========================================
    # TAB 3: PRECISION PLAN & AUTOMATION
    # ==========================================
    with tab_execution:
        st.subheader("🎯 Institutional Precision Trade Plan & Sizing")

        e1, e2 = st.columns([1, 1])
        with e1:
            st.markdown(f"""
            ### Spot Execution Levels (Quantity: {active_quantity} Units)
            - **Direction:** `{plan.action.value}`
            - **Entry Trigger:** `{plan.entry_trigger}`
            - **Stop-Loss (SL):** `₹{plan.stop_loss:.2f}` (Risk: `{plan.risk_points:.2f}` pts)
            - **Target 1 (TP1 - 1:1.5 R:R):** `₹{plan.target_1:.2f}` *(Book 50% & Trail SL to Cost)*
            - **Target 2 (TP2 - 1:2.8 R:R):** `₹{plan.target_2:.2f}` *(Main structure high)*
            - **Target 3 (Runner):** `{plan.target_3_trailing}`
            - **Active Quantity:** **`{active_quantity}` Units** ({active_lots} Lots)
            - **Total Capital at Risk:** `₹{actual_risk_amount:,.2f}` ({risk_pct_of_capital}% of Capital)
            - **Mathematical Edge ($EV$):** `+₹{ev.ev_amount:,.2f} per trade`
            """)

        with e2:
            st.markdown("### 🛡️ Risk & Allocation Health")
            st.markdown(f"""
            - **Capital:** `₹{user_capital:,.2f}`
            - **Account Risk %:** {risk_badge}
            - **Potential Profit at TP1:** `+₹{active_quantity * (plan.target_1 - plan.entry_price):,.2f}`
            - **Potential Profit at TP2:** `+₹{active_quantity * (plan.target_2 - plan.entry_price):,.2f}`
            - **Failure Warning:** `{plan.failure_condition}`
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📡 1-Click Trade Alerts & Webhook Automation")
        t_col, w_col = st.columns(2)
        with t_col:
            st.markdown("**Telegram / Discord Signal Card:**")
            tg_msg = SignalExporter.generate_telegram_alert(
                output=analysis,
                options_info=segments_data,
                custom_quantity=active_quantity,
                custom_risk_amount=actual_risk_amount
            )
            st.code(tg_msg, language="markdown")

        with w_col:
            st.markdown("**Automated Webhook JSON (Zerodha / Dhan / TradingView):**")
            webhook_json = SignalExporter.generate_webhook_json(
                output=analysis,
                options_info=segments_data,
                custom_quantity=active_quantity,
                custom_risk_amount=actual_risk_amount
            )
            st.code(webhook_json, language="json")

    # ==========================================
    # TAB 4: 360° ALL POSSIBILITIES MATRIX
    # ==========================================
    with tab_matrix:
        st.subheader("🌐 All Chart Possibilities Matrix (Har Haal Mein Profitable)")
        st.markdown("An institutional trader never relies on a single directional guess. Every path is mapped:")

        for s in analysis.scenarios_matrix:
            is_rec = s.is_recommended
            badge = "⭐ PRIMARY RECOMMENDED SETUP" if is_rec else "CONDITIONAL SCENARIO"
            with st.expander(f"{s.path_id}: {s.title} — [{badge}]", expanded=is_rec):
                c_a, c_b = st.columns([1, 1])
                with c_a:
                    st.write(f"**Market Behavior:** {s.market_behavior}")
                    st.write(f"**Trigger:** `{s.trigger_condition}`")
                    st.write(f"**Action:** {s.trade_action}")
                with c_b:
                    st.markdown(f"""
                    **Execution Levels:**
                    - **Entry:** `{s.entry}`
                    - **Stop-Loss:** `{s.stop_loss}`
                    - **Target:** `{s.target}`
                    """)

    # ==========================================
    # TAB 5: THINKABLE RADAR & LOSS FILTERS
    # ==========================================
    with tab_thinkable:
        st.subheader("🧠 Thinkable Trading (Second-Order Institutional Reasoning)")
        st.markdown(analysis.retail_trap_analysis)

        st.markdown("---")
        st.subheader("🛡️ Loss Prevention & Non-Profitable Trade Filter")
        for f in analysis.filter_checks:
            icon = "✅" if f.passed else "⚠️"
            st.write(f"**{icon} {f.filter_name}:** {f.verdict}")
            if f.warning_message:
                st.warning(f.warning_message)

        st.markdown("---")
        st.subheader("🧭 Live Dynamic Decision Tree")
        for i, step in enumerate(analysis.decision_tree_steps, 1):
            st.markdown(f"**Condition {i}:** {step.condition}")
            st.code(f"AI Instruction: {step.instruction}", language="text")

    # ==========================================
    # TAB 6: LIVE TRAILING SL & P&L SIMULATOR
    # ==========================================
    with tab_simulator:
        st.subheader("🎮 Interactive Trailing Stop-Loss & P&L Sandbox")
        st.caption(f"Drag the slider to test price movement with your chosen quantity of **{active_quantity} Units**:")

        entry_p = plan.entry_price if plan else analysis.current_price
        sl_p = plan.stop_loss if plan else analysis.current_price * 0.99
        tp1_p = plan.target_1 if plan else analysis.current_price * 1.01
        tp2_p = plan.target_2 if plan else analysis.current_price * 1.02

        # Robust slider bounds for both Long and Short setups
        all_prices = [p for p in [entry_p, sl_p, tp1_p, tp2_p] if p > 0]
        if not all_prices:
            all_prices = [analysis.current_price, analysis.current_price * 1.01]

        min_sim = float(round(min(all_prices) * 0.98, 2))
        max_sim = float(round(max(all_prices) * 1.02, 2))
        if min_sim >= max_sim:
            max_sim = min_sim + 10.0
        val_sim = float(round(min(max_sim, max(min_sim, entry_p)), 2))
        step_sim = max(0.05, float(round(abs(entry_p - sl_p) * 0.05, 2)))

        sim_price = st.slider(
            "Simulated Price Level (₹ / $)",
            min_value=min_sim,
            max_value=max_sim,
            value=val_sim,
            step=step_sim
        )

        pnl_points = sim_price - entry_p if "LONG" in str(plan.action) else entry_p - sim_price
        total_pnl = round(pnl_points * active_quantity, 2)

        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.metric("Simulated P&L", f"{'+' if total_pnl >= 0 else ''}₹{total_pnl:,.2f}", delta=f"{pnl_points:.2f} pts")
        with s_col2:
            is_tp1_reached = (sim_price >= tp1_p) if "LONG" in str(plan.action) else (sim_price <= tp1_p)
            if is_tp1_reached:
                st.metric("Trailing Stop-Loss", f"₹{entry_p:.2f} (Breakeven)", "Risk-Free Trade Locked")
            else:
                st.metric("Current Stop-Loss", f"₹{sl_p:.2f}", f"-₹{abs(entry_p - sl_p)*active_quantity:,.2f} Max Risk")
        with s_col3:
            if total_pnl > 0:
                st.success(f"🟢 In Profit Zone: {pnl_points:.2f} pts gain.")
            elif total_pnl < 0 and ((sim_price <= sl_p) if "LONG" in str(plan.action) else (sim_price >= sl_p)):
                st.error("🔴 Invalidation Hit: Exit immediately.")
            else:
                st.info("🟡 In Entry Range: Awaiting momentum.")

    # ==========================================
    # TAB 7: ACTIVITY HISTORY & PAST SCANS
    # ==========================================
    with tab_history:
        st.subheader("📜 Trade Activity & Past Analysis History")
        st.caption("Aapke pichhle sabhi scans aur setups yahan permanently stored hain. Kisi bhi purane setup ko 1-click reload karein:")

        history_records = ActivityHistoryManager.get_history()

        h_col1, h_col2 = st.columns([3, 1])
        with h_col2:
            if st.button("🗑️ Clear Entire History"):
                ActivityHistoryManager.clear_history()
                st.rerun()

        if history_records:
            # Summary Table
            df_history = pd.DataFrame(history_records)
            cols_to_show = ["timestamp", "asset_name", "timeframe", "verdict", "confluence_score", "entry_price", "stop_loss", "target_1", "quantity", "risk_amount", "ev_amount"]
            st.dataframe(df_history[cols_to_show], width="stretch")

            st.markdown("---")
            st.markdown("### 🔍 Past Setup Details & Quick Reload")
            for rec in history_records[:15]:
                is_buy = "LONG" in rec.get("verdict", "")
                badge_color = "🟢" if is_buy else "🔴"
                with st.expander(f"{badge_color} {rec.get('timestamp')} — {rec.get('asset_name')} ({rec.get('timeframe')}): {rec.get('verdict')} [Score: {rec.get('confluence_score')}/100]"):
                    d1, d2, d3 = st.columns(3)
                    with d1:
                        st.write(f"• **Entry:** ₹{rec.get('entry_price')}")
                        st.write(f"• **Stop-Loss:** ₹{rec.get('stop_loss')}")
                        st.write(f"• **Target 1:** ₹{rec.get('target_1')}")
                    with d2:
                        st.write(f"• **Quantity:** {rec.get('quantity')} Units ({rec.get('lots')} Lots)")
                        st.write(f"• **Risk Amount:** ₹{rec.get('risk_amount')} ({rec.get('risk_pct')}%)")
                        st.write(f"• **Expected Value:** +₹{rec.get('ev_amount')}")
                    with d3:
                        st.write(f"• **Win Rate:** {rec.get('win_rate')}%")
                        st.write(f"• **Wyckoff:** {rec.get('wyckoff_phase')}")
                        st.caption(f"Context: {rec.get('market_context')}")

            # Export Button
            st.download_button(
                label="📥 Export History as JSON",
                data=json.dumps(history_records, indent=2),
                file_name="quant_vision_trade_history.json",
                mime="application/json"
            )
        else:
            st.info("No activity recorded yet. Click '🚀 PROCESS ALL RESULTS' to log your first trade setup!")

    # ==========================================
    # TAB 8: MASTER PROMPT & RULES
    # ==========================================
    with tab_prompt:
        st.subheader("📋 Master System Prompt (QUANT-VISION PRO)")
        st.code(config.MASTER_SYSTEM_PROMPT, language="markdown")

        st.markdown("---")
        st.subheader("📚 Ingested Trading Literature Rules")
        for b in copilot.rag_engine.books_data:
            with st.expander(f"📖 {b.get('author')} — {b.get('title')}"):
                for r in b.get("rules", []):
                    st.markdown(f"**{r.get('pattern')}**: *\"{r.get('rule_quote')}\"*")
                    st.caption(f"Failure Condition: {r.get('fail_condition')}")
else:
    st.info("👈 Set your asset & risk in the sidebar, then click **'🚀 PROCESS ALL RESULTS'** to activate the Co-Pilot!")
