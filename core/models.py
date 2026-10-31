"""
Data models for QUANT-VISION PRO.
Defines types for candles, SMC structures, book knowledge, scenarios, and trade execution plans.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class TrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"


class WyckoffPhase(str, Enum):
    ACCUMULATION = "Accumulation (Phase C/D Spring / SOS)"
    MARKUP = "Markup (Strong Trend Up)"
    DISTRIBUTION = "Distribution (Phase C/D UTAD / SOW)"
    MARKDOWN = "Markdown (Strong Trend Down)"
    CHOP_CONSOLIDATION = "Consolidation (Trading Range)"


class TradeAction(str, Enum):
    LONG = "LONG (BUY)"
    SHORT = "SHORT (SELL)"
    WAIT = "WAIT (NO-TRADE ZONE)"


@dataclass
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    index: int = 0
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    ema200: Optional[float] = None
    rsi: Optional[float] = None
    atr: Optional[float] = None
    vol_ma20: Optional[float] = None


@dataclass
class OrderBlock:
    type: str  # "BULLISH_OB" or "BEARISH_OB"
    high: float
    low: float
    candle_index: int
    mitigated: bool = False
    strength: float = 1.0


@dataclass
class FairValueGap:
    type: str  # "BULLISH_FVG" or "BEARISH_FVG"
    top: float
    bottom: float
    candle_index: int
    mitigated: bool = False


@dataclass
class LiquidityPool:
    type: str  # "BUYSIDE_LIQUIDITY" (BSL) or "SELLSIDE_LIQUIDITY" (SSL)
    price: float
    touches: int
    swept: bool = False


@dataclass
class PatternMatch:
    name: str
    type: str  # "CANDLESTICK", "SMC", "CLASSICAL_TA", "VSA"
    bias: str  # "BULLISH", "BEARISH", "NEUTRAL"
    description: str
    confidence: float  # 0.0 to 1.0
    candle_index: int


@dataclass
class BookRuleMatch:
    book: str
    author: str
    concept: str
    observation: str
    rule_quote: str


@dataclass
class ExpectedValueResult:
    win_probability: float  # 0.0 to 1.0
    loss_probability: float  # 0.0 to 1.0
    avg_profit: float
    avg_loss: float
    ev_amount: float
    risk_reward_ratio: float
    is_positive_ev: bool


@dataclass
class PrecisionTradePlan:
    action: TradeAction
    confluence_score: int  # 0 to 100
    entry_trigger: str
    entry_price: float
    stop_loss: float
    risk_points: float
    target_1: float
    reward_points_1: float
    rr_ratio_1: float
    target_2: float
    reward_points_2: float
    rr_ratio_2: float
    target_3_trailing: str
    position_size: int
    max_risk_amount: float
    potential_profit_tp1: float
    potential_profit_tp2: float
    ev_result: ExpectedValueResult
    failure_condition: str


@dataclass
class ChartScenario:
    path_id: str  # "Path A", "Path B", etc.
    title: str
    market_behavior: str
    trigger_condition: str
    trade_action: str
    entry: str
    stop_loss: str
    target: str
    is_recommended: bool = False


@dataclass
class FilterCheckResult:
    filter_name: str
    passed: bool
    verdict: str
    warning_message: Optional[str] = None


@dataclass
class LiveDecisionStep:
    condition: str
    instruction: str
    action_type: str  # "TRAIL_SL", "BOOK_PROFIT", "CANCEL_TRADE", "FLIP_SHORT", "HOLD"


@dataclass
class AnalysisOutput:
    asset_name: str
    timeframe: str
    current_price: float
    trend: TrendDirection
    wyckoff_phase: WyckoffPhase
    key_support: float
    key_resistance: float
    order_blocks: List[OrderBlock] = field(default_factory=list)
    fvgs: List[FairValueGap] = field(default_factory=list)
    liquidity_pools: List[LiquidityPool] = field(default_factory=list)
    patterns_detected: List[PatternMatch] = field(default_factory=list)
    book_matches: List[BookRuleMatch] = field(default_factory=list)
    retail_trap_analysis: str = ""
    scenarios_matrix: List[ChartScenario] = field(default_factory=list)
    primary_trade_plan: Optional[PrecisionTradePlan] = None
    filter_checks: List[FilterCheckResult] = field(default_factory=list)
    invalidation_warning: str = ""
    news_session_warning: str = ""
    decision_tree_steps: List[LiveDecisionStep] = field(default_factory=list)
    full_hinglish_markdown: str = ""

