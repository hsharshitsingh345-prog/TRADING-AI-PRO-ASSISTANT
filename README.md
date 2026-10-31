# ⚡ QUANT-VISION PRO
### Institutional Multi-Segment Quant & Charting Co-Pilot

> **"Trading blind predictions is retail gambling. Mapping all market segments with positive mathematical expected value, disciplined position sizing, and responsive execution across laptop and mobile devices is institutional edge."**

---

## 🌟 Executive Overview
**QUANT-VISION PRO** is an institutional-grade algorithmic and multimodal trading co-pilot designed to simulate how tier-1 hedge fund quants and Smart Money market makers operate. Rather than giving a naive directional prediction, this system provides:
- **Mobile & Laptop Fully Responsive:** Tailored layout for desktop monitors, laptops, tablets, and smartphones with touch-friendly controls.
- **Persistent Activity & Trade History Store:** Past scans are permanently saved in `data/trade_history.json` and remain accessible anytime.
- **Primary "Process All Results" Button:** Controlled execution that updates all segments and logs activity without laggy auto-reruns.
- **All Market Trading Segments & AI Suggestions:** Options Buying, Options Selling/Writing (Credit Spreads), Futures Trading, Equity Cash (Intraday MIS & Swing CNC), Crypto Perpetuals, Commodities (Gold/Crude), and Forex.
- **Full User Control Over Quantity & Lots:** Choose between AI Auto-Risk sizing or custom user lots/quantity, with live Account Risk percentage recalculation.
- **Thinkable Trading (Second-Order Market Cognition):** Maps out All Chart Possibilities (Paths A through E) to profit under any market condition.

---

## 📱 Mobile & Laptop Deployment

The application is deployed on `0.0.0.0:8501` to allow simultaneous usage across both your laptop and mobile devices:

| Device | Access Link | Description |
| :--- | :--- | :--- |
| 💻 **Laptop / Desktop** | [http://localhost:8501](http://localhost:8501) | Full institutional multi-column view with widescreen Plotly charts. |
| 📱 **Mobile Phone (Same Wi-Fi)** | `http://10.86.40.97:8501` | Mobile-optimized touch interface, auto-collapsing drawer, and horizontal scrolling tabs. |

---

## ☁️ Cloud Deployment Options

### 1. Docker Deployment (AWS / GCP / DigitalOcean / Fly.io / Render)
```bash
# Build Docker image
docker build -t quant-vision-pro .

# Run Docker container
docker run -p 8501:8501 quant-vision-pro
```

### 2. Streamlit Community Cloud (1-Click Free Deployment)
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and select this repository.
3. Set main file path to `app.py`. The `.streamlit/config.toml` and `requirements.txt` will automatically configure the app!

---

## 📦 User Quantity & Lot Selection Engine

Traders have complete control over position sizing:
1. **AI Auto-Sizing (1-2% Rule):** System calculates conservative quantity based on capital and Stop-Loss distance.
2. **Custom Quantity / Lots (User Choice):**
   - **Lot Selector:** Pick 1, 2, 4, 10+ lots for indices (Nifty = 25 qty/lot, BankNifty = 15 qty/lot, Sensex = 10 qty/lot).
   - **Unit Selector:** Directly choose shares, coins, or units for equity, crypto, and commodities.
3. **Dynamic Account Risk Meter:**
   - 🟢 `SAFE SIZING (≤ 2.0% of Capital)`
   - 🟡 `MODERATE RISK (2.1% - 5.0% of Capital)`
   - 🔴 `HIGH DRAWDOWN RISK (> 5.0% of Capital)`

---

## 📁 Repository Structure
```
antproject2/
├── .streamlit/
│   └── config.toml                    # Server binding (0.0.0.0:8501) & institutional dark theme
├── Dockerfile                         # Production Docker container configuration
├── Procfile                           # Heroku / Render deployment descriptor
├── requirements.txt                   # Production Python package requirements
├── config.py                          # Global configuration, constants & model defaults
├── app.py                             # Upgraded Streamlit Web Cockpit (Laptop & Mobile Optimized)
├── run_cli.py                         # CLI co-pilot runner with custom quantity & history
├── README.md                          # Full system documentation
├── core/
│   ├── models.py                      # Strongly typed data models
│   ├── vision_engine.py               # Pattern recognition: Candlestick, SMC, S/R, Wyckoff, VSA
│   ├── knowledge_rag.py               # 6-pillar trading literature RAG system
│   ├── probability_engine.py          # Backtest probability & Positive EV engine
│   ├── sentiment_engine.py            # Macro calendar & Non-Profitable Trade Filter
│   ├── thinkable_engine.py            # Thinkable trading: 5-Path Matrix & Decision Tree
│   ├── trading_segments.py            # Multi-segment engine (Options, Futures, Cash, Crypto, FX)
│   ├── signal_exporter.py             # 1-Click Telegram alert & Webhook JSON generator
│   ├── history_manager.py             # Persistent Activity & Trade History store
│   ├── market_feed.py                 # Live market scanner & broker CSV parser
│   ├── multimodal_agent.py            # Gemini 2.5/Flash Vision API integration
│   └── quant_copilot.py               # Master Orchestrator producing 6-Section Hinglish Output
└── visualization/
    ├── chart_renderer.py              # Interactive Plotly candlestick engine (Mobile responsive)
    ├── gauge_renderer.py              # Visual Confluence Speedometer Gauge
    └── visual_reporter.py             # Formatter for terminal dashboards
```
