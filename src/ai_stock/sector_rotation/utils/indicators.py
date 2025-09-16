"""Utility indicator calculations used by the sample factors."""
from __future__ import annotations

from typing import Iterable, List


def moving_average(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def rate_of_change(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    start = values[0]
    end = values[-1]
    if start == 0:
        return 0.0
    return (end - start) / start
