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
    """Weighting scheme for the various factor models."""

    trend: float = 0.4
    hype: float = 0.2
    capital: float = 0.25
    rotation: float = 0.15

    def as_dict(self) -> Dict[str, float]:
        return {
            "trend": self.trend,
            "hype": self.hype,
            "capital": self.capital,
            "rotation": self.rotation,
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

    @classmethod
    def daily_defaults(cls, as_of: date | None = None) -> "AnalysisConfig":
        """Return a configuration covering the trailing seven sessions."""

        as_of = as_of or date.today()
        start = as_of - timedelta(days=7)
        return cls(start_date=start, end_date=as_of)
