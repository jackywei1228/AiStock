"""Configuration objects for the sector rotation pipeline.

The goal of the package is to provide a lightweight but fully
functional example of the architecture sketched in the README.  The
configuration module defines a couple of data classes that keep the
pipeline wiring tidy and makes it easy to tweak weights or date ranges
when tests need deterministic behaviour.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict


@dataclass
class FactorWeights:
    """Weighting scheme for the strength score."""

    trend: float = 0.35
    hype: float = 0.25
    capital: float = 0.25
    leader: float = 0.15

    def as_dict(self) -> Dict[str, float]:
        return {
            "trend": self.trend,
            "hype": self.hype,
            "capital": self.capital,
            "leader": self.leader,
        }


@dataclass
class RotationWeights:
    """Weighting scheme for the rotation readiness score."""

    relative_lag: float = 0.4
    capital_spillover: float = 0.3
    hype_spillover: float = 0.2
    technical_readiness: float = 0.1

    def as_dict(self) -> Dict[str, float]:
        return {
            "relative_lag": self.relative_lag,
            "capital_spillover": self.capital_spillover,
            "hype_spillover": self.hype_spillover,
            "technical_readiness": self.technical_readiness,
        }


@dataclass
class AnalysisConfig:
    """Input configuration for the daily analysis run."""

    start_date: date
    end_date: date
    board_count: int = 6
    leaders_per_board: int = 2
    initial_cash: float = 1_000_000.0
    factor_weights: FactorWeights = field(default_factory=FactorWeights)
    rotation_weights: RotationWeights = field(default_factory=RotationWeights)

    @classmethod
    def daily_defaults(cls, as_of: date | None = None) -> "AnalysisConfig":
        """Return a configuration covering the trailing seven sessions."""

        as_of = as_of or date.today()
        start = as_of - timedelta(days=7)
        return cls(start_date=start, end_date=as_of)
