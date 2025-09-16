"""Sector rotation pipeline facade."""
from __future__ import annotations

from .config import AnalysisConfig, FactorWeights
from .main import run_daily_analysis

__all__ = ["run_daily_analysis", "AnalysisConfig", "FactorWeights"]
