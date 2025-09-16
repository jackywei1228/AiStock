"""Rotation factor built on top of the other factor outputs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .capital_factor import CapitalComponents
from .hype_factor import HypeComponents
from .trend_factor import TrendComponents


@dataclass(frozen=True)
class RotationComponents:
    trend: float
    capital: float
    hype: float
    synergy: float

    @property
    def score(self) -> float:
        return self.trend * 0.5 + self.capital * 40 + self.hype * 0.2 + self.synergy


def calculate_rotation_factor(
    trend: Dict[str, TrendComponents],
    capital: Dict[str, CapitalComponents],
    hype: Dict[str, HypeComponents],
) -> Dict[str, RotationComponents]:
    """Combine factor components into an RPS style indicator."""

    results: Dict[str, RotationComponents] = {}
    for board in trend.keys():
        trend_score = trend[board].score
        capital_score = capital[board].score
        hype_score = hype[board].score
        # Highlight boards where all factors point in the same direction.
        synergy = 0.0
        if trend_score > 0 and capital_score > 0 and hype_score > 0:
            synergy = min(trend_score, capital_score, hype_score)
        results[board] = RotationComponents(
            trend=trend_score,
            capital=capital_score,
            hype=hype_score,
            synergy=synergy,
        )
    return results
