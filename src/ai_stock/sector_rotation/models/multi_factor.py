"""Utility functions for combining factor outputs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from ..config import FactorWeights, RotationWeights
from ..factors.capital_factor import CapitalComponents
from ..factors.hype_factor import HypeComponents
from ..factors.leader_factor import LeaderComponents
from ..factors.rotation_factor import RotationComponents
from ..factors.trend_factor import TrendComponents


@dataclass(frozen=True)
class StrengthBreakdown:
    trend: float
    hype: float
    capital: float
    leader: float

    @property
    def as_dict(self) -> Dict[str, float]:  # pragma: no cover - convenience wrapper
        return {
            "trend": self.trend,
            "hype": self.hype,
            "capital": self.capital,
            "leader": self.leader,
        }


@dataclass(frozen=True)
class RotationBreakdown:
    relative_lag: float
    capital_spillover: float
    hype_spillover: float
    technical_readiness: float

    @property
    def as_dict(self) -> Dict[str, float]:  # pragma: no cover - convenience wrapper
        return {
            "relative_lag": self.relative_lag,
            "capital_spillover": self.capital_spillover,
            "hype_spillover": self.hype_spillover,
            "technical_readiness": self.technical_readiness,
        }


def combine_strength_score(
    trend: TrendComponents,
    hype: HypeComponents,
    capital: CapitalComponents,
    leader: LeaderComponents,
    weights: FactorWeights,
) -> StrengthBreakdown:
    """Return weighted strength score breakdown."""

    return StrengthBreakdown(
        trend=trend.score * weights.trend,
        hype=hype.score * weights.hype,
        capital=capital.score * weights.capital,
        leader=leader.score * weights.leader,
    )


def combine_rotation_score(
    rotation: RotationComponents,
    weights: RotationWeights,
) -> RotationBreakdown:
    """Return weighted rotation score breakdown."""

    return RotationBreakdown(
        relative_lag=rotation.catch_up * weights.relative_lag,
        capital_spillover=rotation.capital_follow_through * weights.capital_spillover,
        hype_spillover=rotation.hype_transmission * weights.hype_spillover,
        technical_readiness=rotation.technical_setup * weights.technical_readiness,
    )


def score_from_breakdown(breakdown: StrengthBreakdown) -> float:
    return breakdown.trend + breakdown.hype + breakdown.capital + breakdown.leader


def rotation_from_breakdown(breakdown: RotationBreakdown) -> float:
    return (
        breakdown.relative_lag
        + breakdown.capital_spillover
        + breakdown.hype_spillover
        + breakdown.technical_readiness
    )
