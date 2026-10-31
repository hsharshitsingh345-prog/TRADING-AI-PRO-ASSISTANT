"""
Engine 2: Book & Strategy Knowledge Base (RAG).
Maps live chart patterns to rules from John Murphy, Al Brooks, Steve Nison, SMC/ICT, Wyckoff, and Anna Coulling.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.models import BookRuleMatch, PatternMatch, WyckoffPhase
import config


class BookKnowledgeRAG:
    def __init__(self, rules_path: Optional[Path] = None):
        self.rules_path = rules_path or config.BOOK_RULES_PATH
        self.books_data = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        if not self.rules_path.exists():
            return []
        with open(self.rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("books", [])

    def match_rules(
        self,
        patterns: List[PatternMatch],
        wyckoff_phase: WyckoffPhase,
        is_above_emas: bool,
        volume_status: str,
        pullback_type: Optional[str] = None
    ) -> List[BookRuleMatch]:
        """
        Retrieves matching book rules based on active patterns, volume behavior, and trend.
        """
        matched: List[BookRuleMatch] = []
        pattern_names = [p.name.upper() for p in patterns]

        for book in self.books_data:
            author = book.get("author", "Institutional Quant")
            book_title = book.get("title", "")
            for rule in book.get("rules", []):
                rule_pattern = rule.get("pattern", "").upper()
                rule_quote = rule.get("rule_quote", "")
                concept = rule.get("condition", "")

                # Check pattern match
                if rule_pattern in pattern_names:
                    matching_pat = next(p for p in patterns if p.name.upper() == rule_pattern)
                    matched.append(
                        BookRuleMatch(
                            book=book_title,
                            author=author,
                            concept=rule.get("pattern"),
                            observation=f"Matched {matching_pat.name}: {matching_pat.description}",
                            rule_quote=rule_quote
                        )
                    )
                # Check moving average rule
                elif rule_pattern == "MOVING_AVERAGE_CONFLUENCE" and is_above_emas:
                    matched.append(
                        BookRuleMatch(
                            book=book_title,
                            author=author,
                            concept="20/50/200 EMA Confluence",
                            observation="Price trading firmly above 20, 50, and 200 EMA cluster.",
                            rule_quote=rule_quote
                        )
                    )
                # Check Volume VSA rules
                elif rule_pattern == "EFFORT_VS_RESULT_BULLISH" and volume_status == "INSTITUTIONAL_SURGE":
                    matched.append(
                        BookRuleMatch(
                            book=book_title,
                            author=author,
                            concept="Effort vs Result (VSA)",
                            observation="High volume surge with price closing decisively near candle high.",
                            rule_quote=rule_quote
                        )
                    )
                elif rule_pattern == "LOW_VOLUME_BREAKOUT_FAKEOUT" and volume_status == "LOW_VOLUME":
                    matched.append(
                        BookRuleMatch(
                            book=book_title,
                            author=author,
                            concept="Low Volume Warning (Coulling)",
                            observation="Breakout attempt lacking institutional volume participation.",
                            rule_quote=rule_quote
                        )
                    )
                # Wyckoff spring check
                elif rule_pattern == "WYCKOFF_SPRING" and ("SPRING" in pattern_names or "LIQUIDITY_SWEEP" in pattern_names):
                    matched.append(
                        BookRuleMatch(
                            book=book_title,
                            author=author,
                            concept="Phase C Spring / Liquidity Purge",
                            observation="Key support pierced and instantly reclaimed on volume absorption.",
                            rule_quote=rule_quote
                        )
                    )

        # Fallback if few matched
        if not matched:
            matched.append(
                BookRuleMatch(
                    book="Technical Analysis of the Financial Markets",
                    author="John J. Murphy",
                    concept="Structure & Momentum Equilibrium",
                    observation="Consolidation within dynamic support and resistance channels.",
                    rule_quote="Markets spend up to 70% of the time in trading ranges. Patience for clear breakout confirmation is mandatory."
                )
            )

        return matched

    def generate_retail_vs_smart_money_analysis(
        self,
        has_liquidity_sweep: bool,
        has_fvg: bool,
        has_order_block: bool,
        trend_bias: str,
        support_level: float,
        resistance_level: float
    ) -> str:
        """
        Synthesizes Thinkable Trading logic: Contrasting naive retail beliefs with institutional execution.
        """
        lines = []
        if has_liquidity_sweep:
            lines.append(
                f"• **Retail Trader Thinking:** 'Support level {support_level:.2f} par 3 baar price aaya hai, yeh strong support hai, main direct buy kar leta hoon.' Ya breakdown dekh kar aggressive sell order daal diya."
            )
            lines.append(
                f"• **Smart Money (Thinkable) Logic:** Books aur institutional mechanics kehte hain ki support ke neeche hazaron retailers ke Stop-Loss (Sell-Side Liquidity) baithe the. Market Makers ne pehle support todkar sabhi ke stops trigger kiye (Stop Hunt/Spring), unke panic sell orders se apni massive institutional buy orders fill kiye, aur ab price ko upward manipulate karenge. **Isliye retail breakdown par sell nahi, balki liquidity sweep confirmation ke baad institutional long entry banti hai.**"
            )
        elif has_order_block and has_fvg:
            lines.append(
                f"• **Retail Trader Thinking:** Price green candle dekh kar bhaagte hue high par FOMO buy karta hai, jahan SL bahut bada ho jata hai."
            )
            lines.append(
                f"• **Smart Money (Thinkable) Logic:** Smart money breakout ke top par buy nahi karti. Institutions unmitigated Bullish Order Block aur Fair Value Gap (FVG) par limit orders set karti hain (Discount Zone, <50% equilibrium). Hum sniper limit entry lenge jahan Risk chhota aur Reward maximum hoga."
            )
        else:
            lines.append(
                f"• **Retail Trader Thinking:** Breakout candle bante hi blind entry lena bina volume confirmation ya retest ke."
            )
            lines.append(
                f"• **Smart Money (Thinkable) Logic:** Intraday liquidity pools {resistance_level:.2f} ke upar baithe hain. Jab tak 15-minute candle decisively volume ke saath close na ho, yeh Bull Trap ban sakti hai. Wait for institutional footprint verification."
            )

        return "\n".join(lines)

