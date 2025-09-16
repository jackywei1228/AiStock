"""Thin facsimile of the AKShare data access helpers.

The real project would proxy all AKShare calls through this module.  The
sample project simply exposes deterministic pseudo data so that higher
layers can be exercised in unit tests without touching the network.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class SyntheticBoard:
    code: str
    name: str
    members: List[str]


_BOARDS: Dict[str, SyntheticBoard] = {
    "BK001": SyntheticBoard("BK001", "半导体", ["SMIC", "JCET", "HSMC"]),
    "BK002": SyntheticBoard("BK002", "新能源", ["CATL", "BYD", "YONGXING"]),
    "BK003": SyntheticBoard("BK003", "消费电子", ["OPPO", "VIVO", "XIAOMI"]),
    "BK004": SyntheticBoard("BK004", "医药", ["BIOTEC", "HEALTH", "MED"]),
    "BK005": SyntheticBoard("BK005", "券商", ["GFSEC", "HAITONG", "CICC"]),
    "BK006": SyntheticBoard("BK006", "新能源车", ["TESLA", "NIO", "XPENG"]),
}


def seed_for(key: str) -> int:
    """Return a deterministic seed for ``key``."""

    return abs(hash(key)) % (2**32)


def iter_trading_days(start: date, end: date) -> Iterable[date]:
    """Yield daily dates including both end points."""

    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def random_walk(base: float, step: float, days: int, seed: int) -> List[float]:
    """Generate a simple geometric random walk."""

    rng = random.Random(seed)
    price = base
    series = []
    for _ in range(days):
        change = rng.uniform(-step, step)
        price = max(1.0, price * (1 + change))
        series.append(round(price, 2))
    return series


def list_boards() -> List[SyntheticBoard]:
    return list(_BOARDS.values())


def get_board(code: str) -> SyntheticBoard:
    return _BOARDS[code]
