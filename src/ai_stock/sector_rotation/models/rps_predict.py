"""Rotation prediction utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..config import RotationWeights
from ..factors.rotation_factor import RotationComponents
from ..models.strong_board import BoardScore
from .multi_factor import combine_rotation_score, rotation_from_breakdown


@dataclass(frozen=True)
class RpsCandidate:
    board: str
    predicted: float
    breakdown: Dict[str, float]


def predict_next_session(
    rotation: Dict[str, RotationComponents],
    weights: RotationWeights,
    smoothing: float = 0.7,
) -> Dict[str, float]:
    """Smooth rotation scores for short-term projection."""

    predictions: Dict[str, float] = {}
    for board, component in rotation.items():
        breakdown = combine_rotation_score(component, weights)
        base = rotation_from_breakdown(breakdown)
        boost = component.capital_follow_through + component.hype_transmission
        predictions[board] = base * smoothing + boost
    return predictions


def predict_rotation_candidates(
    strengths: Iterable[BoardScore],
    rotation: Dict[str, RotationComponents],
    weights: RotationWeights,
    top_n: int = 5,
    exclude_current: bool = True,
) -> List[RpsCandidate]:
    """Return next rotation candidates ranked by readiness."""

    exclude_set = {score.board for score in strengths} if exclude_current else set()
    candidates: List[RpsCandidate] = []
    for board, component in rotation.items():
        if board in exclude_set:
            continue
        breakdown = combine_rotation_score(component, weights)
        total = rotation_from_breakdown(breakdown)
        candidates.append(
            RpsCandidate(board=board, predicted=total, breakdown=breakdown.as_dict)
        )
    candidates.sort(key=lambda c: c.predicted, reverse=True)
    return candidates[:top_n]
