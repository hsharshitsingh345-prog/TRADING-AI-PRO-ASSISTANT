"""
Activity and Trade Analysis History Manager.
Persists past scans, setups, and user choices so traders can revisit past analyses anytime.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import datetime
import config

HISTORY_FILE = config.DATA_DIR / "trade_history.json"


class ActivityHistoryManager:
    @staticmethod
    def _ensure_file():
        if not HISTORY_FILE.parent.exists():
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not HISTORY_FILE.exists():
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    @classmethod
    def get_history(cls) -> List[Dict[str, Any]]:
        cls._ensure_file()
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return sorted(data, key=lambda x: x.get("timestamp_raw", ""), reverse=True)
        except Exception:
            return []

    @classmethod
    def save_analysis(
        cls,
        asset_name: str,
        timeframe: str,
        current_price: float,
        verdict: str,
        confluence_score: int,
        entry_price: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        quantity: int,
        lots: int,
        risk_amount: float,
        risk_pct: float,
        ev_amount: float,
        win_rate: float,
        market_context: str,
        wyckoff_phase: str = ""
    ) -> Dict[str, Any]:
        """
        Appends an analysis record to the persistent history store.
        """
        cls._ensure_file()
        now = datetime.datetime.now()
        record_id = f"SCAN_{now.strftime('%Y%m%d_%H%M%S')}_{len(asset_name)}"
        record = {
            "id": record_id,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp_raw": now.isoformat(),
            "asset_name": asset_name,
            "timeframe": timeframe,
            "current_price": round(current_price, 2),
            "verdict": verdict,
            "confluence_score": confluence_score,
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "target_1": round(target_1, 2),
            "target_2": round(target_2, 2),
            "quantity": quantity,
            "lots": lots,
            "risk_amount": round(risk_amount, 2),
            "risk_pct": round(risk_pct, 2),
            "ev_amount": round(ev_amount, 2),
            "win_rate": round(win_rate, 1),
            "market_context": market_context,
            "wyckoff_phase": wyckoff_phase
        }

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

        # Avoid exact duplicate within 10 seconds
        if history and history[0].get("asset_name") == asset_name and abs(history[0].get("current_price", 0) - current_price) < 0.01:
            history[0] = record  # update latest
        else:
            history.insert(0, record)

        # Keep last 100 scans
        history = history[:100]

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        return record

    @classmethod
    def clear_history(cls):
        cls._ensure_file()
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    @classmethod
    def delete_record(cls, record_id: str):
        cls._ensure_file()
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
            history = [r for r in history if r.get("id") != record_id]
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception:
            pass

