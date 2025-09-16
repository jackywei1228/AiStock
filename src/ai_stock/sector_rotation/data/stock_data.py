"""Synthetic stock level data used when picking leaders."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from ..utils import akshare_helper


@dataclass(frozen=True)
class StockBar:
    symbol: str
    date: date
    close: float
    turnover_rate: float


def fetch_stock_data(stocks: Iterable[str], start: date, end: date) -> Dict[str, List[StockBar]]:
    days = list(akshare_helper.iter_trading_days(start, end))
    result: Dict[str, List[StockBar]] = {}
    for symbol in stocks:
        seed = akshare_helper.seed_for(f"stock-{symbol}")
        closes = akshare_helper.random_walk(base=50.0, step=0.08, days=len(days), seed=seed)
        rng = random.Random(seed)
        bars: List[StockBar] = []
        for idx, day in enumerate(days):
            turnover_rate = round(rng.uniform(0.5, 8.0), 3)
            bars.append(
                StockBar(
                    symbol=symbol,
                    date=day,
                    close=closes[idx],
                    turnover_rate=turnover_rate,
                )
            )
        result[symbol] = bars
    return result
