"""Synthetic board popularity metrics."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from ..utils import akshare_helper


@dataclass(frozen=True)
class BoardHotMetric:
    board: str
    date: date
    hot_score: float
    mentions: int


def fetch_board_hot(boards: Iterable[str], start: date, end: date) -> Dict[str, List[BoardHotMetric]]:
    result: Dict[str, List[BoardHotMetric]] = {}
    days = list(akshare_helper.iter_trading_days(start, end))
    for board in boards:
        seed = akshare_helper.seed_for(f"hot-{board}")
        rng = random.Random(seed)
        metrics: List[BoardHotMetric] = []
        for day in days:
            score = rng.uniform(0, 100)
            mentions = int(rng.uniform(10, 1000))
            metrics.append(
                BoardHotMetric(
                    board=board,
                    date=day,
                    hot_score=round(score, 2),
                    mentions=mentions,
                )
            )
        result[board] = metrics
    return result
