"""Board ranking model combining different factor scores."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..config import FactorWeights
from ..factors.capital_factor import CapitalComponents
from ..factors.hype_factor import HypeComponents
from ..factors.rotation_factor import RotationComponents
from ..factors.trend_factor import TrendComponents


@dataclass(frozen=True)
class BoardScore:
    board: str
    score: float
    breakdown: Dict[str, float]


def rank_boards(
    trend: Dict[str, TrendComponents],
    hype: Dict[str, HypeComponents],
    capital: Dict[str, CapitalComponents],
    rotation: Dict[str, RotationComponents],
    weights: FactorWeights,
) -> List[BoardScore]:
    """Return ranked boards based on the weighted factor sum."""

    scores: List[BoardScore] = []
    for board in rotation.keys():
        components = {
            "trend": trend[board].score,
            "hype": hype[board].score,
            "capital": capital[board].score,
            "rotation": rotation[board].score,
        }
        weighted = (
            components["trend"] * weights.trend
            + components["hype"] * weights.hype
            + components["capital"] * weights.capital
            + components["rotation"] * weights.rotation
        )
        scores.append(BoardScore(board=board, score=weighted, breakdown=components))

    scores.sort(key=lambda s: s.score, reverse=True)
    return scores
