"""Board ranking model combining different factor scores."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..config import FactorWeights
from ..factors.capital_factor import CapitalComponents
from ..factors.hype_factor import HypeComponents
from ..factors.leader_factor import LeaderComponents, create_empty_leader_components
from ..factors.trend_factor import TrendComponents
from .multi_factor import combine_strength_score, score_from_breakdown


@dataclass(frozen=True)
class BoardScore:
    board: str
    name: str
    score: float
    breakdown: Dict[str, float]


def rank_boards(
    trend: Dict[str, TrendComponents],
    hype: Dict[str, HypeComponents],
    capital: Dict[str, CapitalComponents],
    leader: Dict[str, LeaderComponents],
    board_names: Dict[str, str],
    weights: FactorWeights,
) -> List[BoardScore]:
    """Return ranked boards based on the weighted factor sum."""

    scores: List[BoardScore] = []
    boards = set(trend.keys()) & set(hype.keys()) & set(capital.keys())
    for board in boards:
        leader_component = leader.get(board) or create_empty_leader_components(board)
        breakdown = combine_strength_score(
            trend[board], hype[board], capital[board], leader_component, weights
        )
        scores.append(
            BoardScore(
                board=board,
                name=board_names.get(board, board),
                score=score_from_breakdown(breakdown),
                breakdown={
                    "trend": breakdown.trend,
                    "hype": breakdown.hype,
                    "capital": breakdown.capital,
                    "leader": breakdown.leader,
                },
            )
        )

    scores.sort(key=lambda s: s.score, reverse=True)
    return scores
