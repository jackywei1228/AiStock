"""Trend related factor calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from ..data.board_price import BoardPriceBar
from ..utils.indicators import moving_average, rate_of_change


HS300_SYMBOL = "000300"


@dataclass(frozen=True)
class TrendComponents:
    return_3d: float
    return_5d: float
    return_10d: float
    excess_vs_hs300: float
    ma_signal: float

    @property
    def score(self) -> float:
        return (
            self.return_3d * 200
            + self.return_5d * 150
            + self.return_10d * 100
            + self.excess_vs_hs300 * 120
            + self.ma_signal
        )


def calculate_trend_factor(
    prices: Dict[str, List[BoardPriceBar]],
    index_prices: Dict[str, List[BoardPriceBar]] | None = None,
    index_symbol: str = HS300_SYMBOL,
) -> Dict[str, TrendComponents]:
    """Calculate trend metrics for each board.

    ``index_prices`` is optional reference data (e.g. 沪深300). When not
    supplied the excess return component falls back to zero.
    """

    index_series: List[BoardPriceBar] | None = None
    if index_prices is not None:
        index_series = index_prices.get(index_symbol)

    results: Dict[str, TrendComponents] = {}
    for board, series in prices.items():
        closes = [bar.close for bar in series]
        return_3d = _window_return(closes, 3)
        return_5d = _window_return(closes, 5)
        return_10d = _window_return(closes, 10)
        ma_short = moving_average(closes[-5:])
        ma_long = moving_average(closes[-10:])
        ma_signal = ma_short - ma_long

        excess = 0.0
        if index_series:
            index_closes = [bar.close for bar in index_series]
            index_ret = _window_return(index_closes, 10)
            excess = return_10d - index_ret

        results[board] = TrendComponents(
            return_3d=return_3d,
            return_5d=return_5d,
            return_10d=return_10d,
            excess_vs_hs300=excess,
            ma_signal=ma_signal,
        )
    return results


def _window_return(closes: List[float], window: int) -> float:
    if len(closes) < 2:
        return 0.0
    window = min(window, len(closes) - 1)
    start = closes[-window - 1]
    end = closes[-1]
    if start == 0:
        return 0.0
    return (end - start) / start
