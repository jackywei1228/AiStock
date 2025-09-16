"""Board selection logic."""
from __future__ import annotations

from typing import Iterable, List, Sequence

from ..models.rps_predict import RpsCandidate
from ..models.strong_board import BoardScore


def select_primary_boards(scores: Sequence[BoardScore], top_n: int, min_score: float = 0.0) -> List[BoardScore]:
    """Select the strongest boards currently in an up-leg."""

    primary: List[BoardScore] = []
    for score in scores:
        if score.score < min_score and len(primary) >= top_n:
            continue
        primary.append(score)
        if len(primary) >= top_n:
            break
    return primary


def select_candidate_boards(
    candidates: Sequence[RpsCandidate],
    exclude: Iterable[str],
    top_n: int,
    min_predicted: float = 0.0,
) -> List[RpsCandidate]:
    """Identify next-in-line rotation candidates."""

    exclude_set = set(exclude)
    picks: List[RpsCandidate] = []
    for candidate in candidates:
        if candidate.board in exclude_set:
            continue
        if candidate.predicted < min_predicted:
            continue
        picks.append(candidate)
        if len(picks) >= top_n:
            break
    return picks


def select_top_boards(scores: Iterable[BoardScore], top_n: int) -> List[BoardScore]:
    return select_primary_boards(list(scores), top_n)
