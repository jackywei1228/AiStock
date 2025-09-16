"""ASCII based visualisations for quick inspection."""
from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from ..factors.capital_factor import CapitalComponents
from ..factors.hype_factor import HypeComponents
from ..factors.leader_factor import LeaderComponents
from ..factors.trend_factor import TrendComponents
from ..models.rps_predict import RpsCandidate
from ..models.strong_board import BoardScore


def rotation_heatmap(scores: Iterable[BoardScore]) -> str:
    scores = list(scores)
    if not scores:
        return "(no data)"
    max_score = max(score.score for score in scores) or 1.0
    lines: List[str] = []
    for score in scores:
        ratio = max(0.0, score.score / max_score)
        filled = int(ratio * 10)
        bar = "#" * filled or "-"
        lines.append(f"{score.board:<6} | {bar} ({score.score:.2f})")
    return "\n".join(lines)


def factor_table(
    trend: Mapping[str, TrendComponents],
    hype: Mapping[str, HypeComponents],
    capital: Mapping[str, CapitalComponents],
    leader: Mapping[str, LeaderComponents],
    boards: Sequence[str],
) -> str:
    """Return an aligned table summarising factor scores."""

    header = "Board   Trend    Hype     Capital  Leader"
    lines = [header, "-" * len(header)]
    for board in boards:
        leader_score = leader.get(board).score if board in leader else 0.0
        lines.append(
            f"{board:<7}{trend[board].score:>8.2f}{hype[board].score:>9.2f}"
            f"{capital[board].score:>9.2f}{leader_score:>9.2f}"
        )
    return "\n".join(lines)


def rotation_pathway(
    candidates: Sequence[RpsCandidate],
    predictions: Mapping[str, float],
) -> str:
    """Represent candidate transitions via a simple text diagram."""

    if not candidates:
        return "(no rotation candidates)"

    lines = ["Rotation Pathway", "-" * 18]
    for candidate in candidates:
        next_score = predictions.get(candidate.board, 0.0)
        lines.append(
            f"{candidate.board} -> readiness={candidate.predicted:.2f} next={next_score:.2f}"
        )
    return "\n".join(lines)
