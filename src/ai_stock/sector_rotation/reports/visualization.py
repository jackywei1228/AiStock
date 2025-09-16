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
    boards: Sequence[BoardScore],
) -> str:
    """Return an aligned table summarising factor scores."""

    header = "Board   Name            Trend    Hype     Capital  Leader"
    lines = [header, "-" * len(header)]
    for score in boards:
        code = score.board
        leader_score = leader.get(code).score if code in leader else 0.0
        lines.append(
            f"{code:<7}{score.name:<15}{trend[code].score:>8.2f}{hype[code].score:>9.2f}"
            f"{capital[code].score:>9.2f}{leader_score:>9.2f}"
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
        label = f"{candidate.board} ({candidate.name})" if candidate.name else candidate.board
        lines.append(
            f"{label} -> readiness={candidate.predicted:.2f} next={next_score:.2f}"
        )
    return "\n".join(lines)
