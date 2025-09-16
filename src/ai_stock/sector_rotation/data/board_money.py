"""Synthetic money flow statistics for boards."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from ..utils import akshare_helper


@dataclass(frozen=True)
class BoardMoneyFlow:
    board: str
    date: date
    net_inflow: float
    main_inflow: float


def fetch_money_flow(boards: Iterable[str], start: date, end: date) -> Dict[str, List[BoardMoneyFlow]]:
    result: Dict[str, List[BoardMoneyFlow]] = {}
    days = list(akshare_helper.iter_trading_days(start, end))
    for board in boards:
        seed = akshare_helper.seed_for(f"money-{board}")
        rng = random.Random(seed)
        flows: List[BoardMoneyFlow] = []
        for day in days:
            base = rng.uniform(-5_000_000, 5_000_000)
            main = base * rng.uniform(0.6, 1.1)
            flows.append(
                BoardMoneyFlow(
                    board=board,
                    date=day,
                    net_inflow=round(base, 2),
                    main_inflow=round(main, 2),
                )
            )
        result[board] = flows
    return result
