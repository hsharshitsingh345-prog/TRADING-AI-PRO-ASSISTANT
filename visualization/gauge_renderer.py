"""
Interactive Confluence Gauge and Risk Meter.
Renders an institutional speedometer for multi-book setup quality.
"""

import plotly.graph_objects as go


def create_confluence_gauge(score: int, title: str = "Setup Confluence Score") -> go.Figure:
    """
    Renders an institutional radial gauge (0-100).
    """
    # Determine bar color based on score
    if score >= 75:
        bar_color = "#00E676"  # Institutional High Probability Emerald
        status_text = "HIGH CONFLUENCE (INSTITUTIONAL)"
    elif score >= 60:
        bar_color = "#00BCD4"  # Moderate Probability Cyan
        status_text = "VALID SETUP (STANDARD RISK)"
    elif score >= 45:
        bar_color = "#FFB300"  # Amber
        status_text = "CHOP / LOW CONFLUENCE"
    else:
        bar_color = "#FF3366"  # Red / Avoid
        status_text = "HIGH RISK / AVOID TRADE"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>{title}</b><br><span style='font-size:12px;color:{bar_color};'>{status_text}</span>", 'font': {'size': 15, 'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#787B86", 'ticks': "outside"},
                'bar': {'color': bar_color, 'thickness': 0.28},
                'bgcolor': "rgba(30, 34, 45, 0.6)",
                'borderwidth': 1,
                'bordercolor': "#2A2E39",
                'steps': [
                    {'range': [0, 45], 'color': 'rgba(255, 51, 102, 0.15)'},
                    {'range': [45, 65], 'color': 'rgba(255, 179, 0, 0.15)'},
                    {'range': [65, 80], 'color': 'rgba(0, 188, 212, 0.15)'},
                    {'range': [80, 100], 'color': 'rgba(0, 230, 118, 0.20)'}
                ],
                'threshold': {
                    'line': {'color': "#00F5FF", 'width': 3},
                    'thickness': 0.75,
                    'value': 75
                }
            },
            number={'font': {'size': 38, 'color': bar_color, 'weight': 'bold'}, 'suffix': "/100"}
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=210,
        margin=dict(l=25, r=25, t=35, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

