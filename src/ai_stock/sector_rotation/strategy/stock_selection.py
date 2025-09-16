"""Pick candidate leader stocks for a set of boards."""
from __future__ import annotations

from typing import Dict, Iterable, List

from ..factors.leader_factor import LeaderCandidate
from ..models.strong_board import BoardScore


def _rank_candidates(candidates: Iterable[LeaderCandidate]) -> List[LeaderCandidate]:
    ranked = sorted(
        candidates,
        key=lambda c: (
            c.is_limit_up,
            c.turnover_share,
            c.pct_change,
            c.return_pct,
        ),
        reverse=True,
    )
    return ranked


def select_leaders(
    selected_boards: Iterable[BoardScore],
    candidates: Dict[str, List[LeaderCandidate]],
    per_board: int,
    min_turnover_share: float = 0.01,
) -> Dict[str, List[LeaderCandidate]]:
    picks: Dict[str, List[LeaderCandidate]] = {}
    for board in selected_boards:
        ranked = [c for c in _rank_candidates(candidates.get(board.board, [])) if c.turnover_share >= min_turnover_share]
        picks[board.board] = ranked[:per_board]
    return picks
