"""
Interactive Plotly Chart Renderer for QUANT-VISION PRO.
Renders Candlesticks with EMAs, Order Blocks, FVGs, and Trade Plan (Entry, SL, TP1, TP2).
"""

from typing import List, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.models import Candle, OrderBlock, FairValueGap, PrecisionTradePlan


def create_interactive_chart(
    df: pd.DataFrame,
    order_blocks: Optional[List[OrderBlock]] = None,
    fvgs: Optional[List[FairValueGap]] = None,
    trade_plan: Optional[PrecisionTradePlan] = None,
    title: str = "QUANT-VISION PRO: Institutional Multi-Lens Chart"
) -> go.Figure:
    """
    Builds a professional 3-panel interactive TradingView-style Plotly chart.
    Panel 1: Candlesticks + EMAs + SMC Overlays (OB, FVG) + Trade Plan Lines
    Panel 2: Volume + 20-period Volume MA
    Panel 3: RSI (14)
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.65, 0.18, 0.17],
        subplot_titles=(title, "Volume & Institutional Flow", "RSI (14) Momentum")
    )

    x_vals = df['timestamp'] if 'timestamp' in df.columns else df.index

    # Panel 1: Candlestick
    fig.add_trace(
        go.Candlestick(
            x=x_vals,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Price",
            increasing_line_color="#089981",
            decreasing_line_color="#F23645",
            increasing_fillcolor="#089981",
            decreasing_fillcolor="#F23645"
        ),
        row=1, col=1
    )

    # Moving Averages
    if 'ema20' in df.columns:
        fig.add_trace(go.Scatter(x=x_vals, y=df['ema20'], mode='lines', line=dict(color='#2962FF', width=1.5), name="EMA 20"), row=1, col=1)
    if 'ema50' in df.columns:
        fig.add_trace(go.Scatter(x=x_vals, y=df['ema50'], mode='lines', line=dict(color='#FF9800', width=1.5), name="EMA 50"), row=1, col=1)
    if 'ema200' in df.columns:
        fig.add_trace(go.Scatter(x=x_vals, y=df['ema200'], mode='lines', line=dict(color='#9C27B0', width=2.0), name="EMA 200"), row=1, col=1)

    # Overlay Order Blocks
    if order_blocks:
        for ob in order_blocks[-4:]:  # Show recent 4 order blocks
            color = "rgba(8, 153, 129, 0.22)" if ob.type == "BULLISH_OB" else "rgba(242, 54, 69, 0.22)"
            border = "#089981" if ob.type == "BULLISH_OB" else "#F23645"
            fig.add_shape(
                type="rect",
                x0=x_vals.iloc[ob.candle_index],
                x1=x_vals.iloc[-1],
                y0=ob.low,
                y1=ob.high,
                fillcolor=color,
                line=dict(color=border, width=1, dash="dot"),
                row=1, col=1
            )
            fig.add_annotation(
                x=x_vals.iloc[-1],
                y=(ob.high + ob.low) / 2,
                text=f"{'Bullish' if ob.type == 'BULLISH_OB' else 'Bearish'} OB",
                showarrow=False,
                font=dict(size=9, color=border),
                xanchor="left",
                row=1, col=1
            )

    # Overlay Fair Value Gaps
    if fvgs:
        for f in fvgs[-3:]:
            color = "rgba(0, 188, 212, 0.18)" if f.type == "BULLISH_FVG" else "rgba(255, 152, 0, 0.18)"
            fig.add_shape(
                type="rect",
                x0=x_vals.iloc[f.candle_index],
                x1=x_vals.iloc[-1],
                y0=f.bottom,
                y1=f.top,
                fillcolor=color,
                line=dict(color="#00BCD4" if f.type == "BULLISH_FVG" else "#FF9800", width=1, dash="dash"),
                row=1, col=1
            )

    # Overlay Trade Plan Levels
    if trade_plan:
        last_x = x_vals.iloc[-1]
        first_x = x_vals.iloc[-15] if len(x_vals) >= 15 else x_vals.iloc[0]

        # Entry
        fig.add_shape(type="line", x0=first_x, x1=last_x, y0=trade_plan.entry_price, y1=trade_plan.entry_price,
                      line=dict(color="#2196F3", width=2, dash="dash"), row=1, col=1)
        fig.add_annotation(x=last_x, y=trade_plan.entry_price, text=f" ENTRY ₹{trade_plan.entry_price:.2f}",
                           showarrow=False, font=dict(color="#2196F3", size=10, weight="bold"), xanchor="left", row=1, col=1)

        # Stop-Loss
        fig.add_shape(type="line", x0=first_x, x1=last_x, y0=trade_plan.stop_loss, y1=trade_plan.stop_loss,
                      line=dict(color="#F44336", width=2, dash="solid"), row=1, col=1)
        fig.add_annotation(x=last_x, y=trade_plan.stop_loss, text=f" SL ₹{trade_plan.stop_loss:.2f}",
                           showarrow=False, font=dict(color="#F44336", size=10, weight="bold"), xanchor="left", row=1, col=1)

        # Target 1
        fig.add_shape(type="line", x0=first_x, x1=last_x, y0=trade_plan.target_1, y1=trade_plan.target_1,
                      line=dict(color="#4CAF50", width=1.5, dash="dashdot"), row=1, col=1)
        fig.add_annotation(x=last_x, y=trade_plan.target_1, text=f" TP1 ₹{trade_plan.target_1:.2f} (1:1.5)",
                           showarrow=False, font=dict(color="#4CAF50", size=10), xanchor="left", row=1, col=1)

        # Target 2
        fig.add_shape(type="line", x0=first_x, x1=last_x, y0=trade_plan.target_2, y1=trade_plan.target_2,
                      line=dict(color="#00E676", width=2, dash="dashdot"), row=1, col=1)
        fig.add_annotation(x=last_x, y=trade_plan.target_2, text=f" TP2 ₹{trade_plan.target_2:.2f} (1:2.8)",
                           showarrow=False, font=dict(color="#00E676", size=10, weight="bold"), xanchor="left", row=1, col=1)

    # Panel 2: Volume
    colors_vol = ['#089981' if c >= o else '#F23645' for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(x=x_vals, y=df['volume'], marker_color=colors_vol, name="Volume"), row=2, col=1)
    if 'vol_ma20' in df.columns:
        fig.add_trace(go.Scatter(x=x_vals, y=df['vol_ma20'], mode='lines', line=dict(color='#FFEB3B', width=1.2), name="Vol MA 20"), row=2, col=1)

    # Panel 3: RSI
    if 'rsi' in df.columns:
        fig.add_trace(go.Scatter(x=x_vals, y=df['rsi'], mode='lines', line=dict(color='#AB47BC', width=1.5), name="RSI (14)"), row=3, col=1)
        fig.add_hline(y=70, line=dict(color='#F23645', dash="dot", width=1), row=3, col=1)
        fig.add_hline(y=30, line=dict(color='#089981', dash="dot", width=1), row=3, col=1)

    # Layout styling (Dark Theme institutional look, optimized for both Desktop and Mobile)
    fig.update_layout(
        template="plotly_dark",
        height=620,
        autosize=True,
        margin=dict(l=25, r=45, t=45, b=25),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        dragmode="pan",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10))
    )

    return fig

