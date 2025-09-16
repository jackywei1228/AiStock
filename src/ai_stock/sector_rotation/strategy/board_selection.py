"""Board selection logic."""
from __future__ import annotations

from typing import Iterable, List

from ..models.strong_board import BoardScore


def select_top_boards(scores: Iterable[BoardScore], top_n: int) -> List[BoardScore]:
    return list(scores)[:top_n]
