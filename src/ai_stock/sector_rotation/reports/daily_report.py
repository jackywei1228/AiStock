"""Generation of the textual daily rotation report."""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List

from ..factors.leader_factor import LeaderCandidate
from ..models.strong_board import BoardScore


def build_daily_report(
    as_of: date,
    board_scores: Iterable[BoardScore],
    leaders: Dict[str, List[LeaderCandidate]],
    allocations: Dict[str, float],
    predictions: Dict[str, float],
) -> str:
    lines: List[str] = []
    lines.append(f"Sector rotation summary for {as_of.isoformat()}")
    lines.append("=")
    for score in board_scores:
        allocation = allocations.get(score.board, 0.0)
        prediction = predictions.get(score.board, 0.0)
        lines.append(
            f"{score.board}: score={score.score:.2f} allocation={allocation:,.0f} next={prediction:.2f}"
        )
        leader_details = leaders.get(score.board, [])
        if leader_details:
            leader_line = ", ".join(
                f"{candidate.symbol}({candidate.return_pct*100:.1f}%/{candidate.avg_turnover:.2f})"
                for candidate in leader_details
            )
            lines.append(f"  leaders: {leader_line}")
    return "\n".join(lines)
