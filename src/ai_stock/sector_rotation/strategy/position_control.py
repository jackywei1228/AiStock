"""Position sizing helper."""
from __future__ import annotations

from typing import Dict, Iterable

from ..models.strong_board import BoardScore


def allocate_equally(cash: float, selections: Iterable[BoardScore]) -> Dict[str, float]:
    picks = list(selections)
    if not picks:
        return {}
    per_board = cash / len(picks)
    return {pick.board: per_board for pick in picks}
