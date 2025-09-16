"""Leader stock identification and aggregation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from ..data.stock_data import BoardComponentQuote, StockBar
from ..utils.indicators import moving_average, rate_of_change


@dataclass(frozen=True)
class LeaderCandidate:
    symbol: str
    name: str
    return_pct: float
    pct_change: float
    turnover_share: float
    is_limit_up: bool

    @property
    def score(self) -> float:
        limit_bonus = 5 if self.is_limit_up else 0
        return self.return_pct * 100 + self.turnover_share * 100 + self.pct_change + limit_bonus


@dataclass(frozen=True)
class LeaderComponents:
    board: str
    limit_up_count: int
    leader_turnover_share: float
    avg_leader_return: float
    leader_symbols: List[str]

    @property
    def score(self) -> float:
        return (
            self.limit_up_count * 15
            + self.leader_turnover_share * 120
            + self.avg_leader_return * 90
        )


def create_empty_leader_components(board: str) -> LeaderComponents:
    return LeaderComponents(
        board=board,
        limit_up_count=0,
        leader_turnover_share=0.0,
        avg_leader_return=0.0,
        leader_symbols=[],
    )


def calculate_leader_factor(
    board_quotes: Dict[str, List[BoardComponentQuote]],
    stock_history: Dict[str, List[StockBar]],
    top_n: int = 3,
    limit_threshold: float = 9.5,
) -> Tuple[Dict[str, List[LeaderCandidate]], Dict[str, LeaderComponents]]:
    """Return leader candidates and aggregated board level metrics."""

    leader_candidates: Dict[str, List[LeaderCandidate]] = {}
    leader_components: Dict[str, LeaderComponents] = {}

    for board, quotes in board_quotes.items():
        if not quotes:
            continue
        sorted_quotes = sorted(quotes, key=lambda item: item.pct_change, reverse=True)
        selected = sorted_quotes[:top_n]

        candidates: List[LeaderCandidate] = []
        limit_up_count = 0
        turnover_share = 0.0
        returns: List[float] = []

        for quote in selected:
            history = stock_history.get(quote.symbol, [])
            if history:
                ret = rate_of_change([bar.close for bar in history])
            else:
                ret = quote.pct_change / 100.0
            turnover_share += quote.turnover_share
            is_limit_up = quote.pct_change >= limit_threshold
            if is_limit_up:
                limit_up_count += 1
            returns.append(ret)
            candidates.append(
                LeaderCandidate(
                    symbol=quote.symbol,
                    name=quote.name,
                    return_pct=ret,
                    pct_change=quote.pct_change,
                    turnover_share=quote.turnover_share,
                    is_limit_up=is_limit_up,
                )
            )

        if not candidates:
            continue

        avg_return = sum(returns) / len(returns) if returns else 0.0
        leader_candidates[board] = candidates
        leader_components[board] = LeaderComponents(
            board=board,
            limit_up_count=limit_up_count,
            leader_turnover_share=turnover_share,
            avg_leader_return=avg_return,
            leader_symbols=[candidate.symbol for candidate in candidates],
        )

    return leader_candidates, leader_components
