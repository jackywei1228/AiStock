"""Synthetic board price history."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from ..utils import akshare_helper


@dataclass(frozen=True)
class BoardPriceBar:
    board: str
    date: date
    close: float
    volume: float
    turnover: float


def fetch_board_prices(boards: Iterable[str], start: date, end: date) -> Dict[str, List[BoardPriceBar]]:
    """Return pseudo price series for each board.

    The data is deterministic to keep the tests stable.  A seeded random
    walk is used to create reasonable looking price and volume series.
    """

    result: Dict[str, List[BoardPriceBar]] = {}
    days = list(akshare_helper.iter_trading_days(start, end))
    for board in boards:
        seed = akshare_helper.seed_for(f"price-{board}")
        closes = akshare_helper.random_walk(base=100.0, step=0.05, days=len(days), seed=seed)
        rng = random.Random(seed)
        series: List[BoardPriceBar] = []
        for idx, day in enumerate(days):
            # Allow the seeded RNG to generate deterministic but varied figures.
            volume = round(1_000_000 * (1 + rng.uniform(-0.3, 0.3)), 2)
            turnover = round(closes[idx] * volume / 10_000, 2)
            series.append(
                BoardPriceBar(
                    board=board,
                    date=day,
                    close=closes[idx],
                    volume=volume,
                    turnover=turnover,
                )
            )
        result[board] = series
    return result
