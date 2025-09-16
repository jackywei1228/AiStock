"""Leader stock identification."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..data.stock_data import StockBar
from ..utils.indicators import moving_average, rate_of_change


@dataclass(frozen=True)
class LeaderCandidate:
    symbol: str
    return_pct: float
    avg_turnover: float

    @property
    def score(self) -> float:
        return self.return_pct * 100 + self.avg_turnover


def identify_leaders(board_members: Dict[str, Iterable[str]], stock_history: Dict[str, List[StockBar]]) -> Dict[str, List[LeaderCandidate]]:
    results: Dict[str, List[LeaderCandidate]] = {}
    for board, members in board_members.items():
        candidates: List[LeaderCandidate] = []
        for symbol in members:
            history = stock_history.get(symbol)
            if not history:
                continue
            closes = [bar.close for bar in history]
            ret = rate_of_change(closes)
            avg_turnover = moving_average(bar.turnover_rate for bar in history)
            candidates.append(LeaderCandidate(symbol=symbol, return_pct=ret, avg_turnover=avg_turnover))
        candidates.sort(key=lambda c: (c.return_pct, c.avg_turnover), reverse=True)
        results[board] = candidates
    return results
