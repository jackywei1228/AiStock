"""Pick candidate leader stocks for a set of boards."""
from __future__ import annotations

from typing import Dict, Iterable, List

from ..factors.leader_factor import LeaderCandidate
from ..models.strong_board import BoardScore


def select_leaders(
    selected_boards: Iterable[BoardScore],
    candidates: Dict[str, List[LeaderCandidate]],
    per_board: int,
) -> Dict[str, List[LeaderCandidate]]:
    picks: Dict[str, List[LeaderCandidate]] = {}
    for board in selected_boards:
        board_candidates = candidates.get(board.board, [])
        picks[board.board] = board_candidates[:per_board]
    return picks
