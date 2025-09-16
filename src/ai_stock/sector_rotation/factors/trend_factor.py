"""Trend related factor calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from ..data.board_price import BoardPriceBar
from ..utils.indicators import moving_average, rate_of_change


@dataclass(frozen=True)
class TrendComponents:
    momentum: float
    ma_diff: float

    @property
    def score(self) -> float:
        return self.momentum * 70 + self.ma_diff


def calculate_trend_factor(prices: Dict[str, List[BoardPriceBar]]) -> Dict[str, TrendComponents]:
    """Calculate a compact trend score for each board."""

    results: Dict[str, TrendComponents] = {}
    for board, series in prices.items():
        closes = [bar.close for bar in series]
        momentum = rate_of_change(closes)
        ma = moving_average(closes[-3:])
        ma_diff = closes[-1] - ma
        results[board] = TrendComponents(momentum=momentum, ma_diff=ma_diff)
    return results
