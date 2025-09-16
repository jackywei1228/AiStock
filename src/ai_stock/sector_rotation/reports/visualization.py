"""ASCII based visualisations for quick inspection."""
from __future__ import annotations

from typing import Iterable, List

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
        lines.append(f"{score.board:<6} | {bar}")
    return "\n".join(lines)
