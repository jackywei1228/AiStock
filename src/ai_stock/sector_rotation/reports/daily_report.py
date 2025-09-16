"""Generation of the textual daily rotation report."""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List, Sequence

from ..factors.leader_factor import LeaderCandidate
from ..models.rps_predict import RpsCandidate
from ..models.strong_board import BoardScore


def _format_leaders(leaders: Sequence[LeaderCandidate]) -> str:
    return ", ".join(
        f"{candidate.symbol}({candidate.pct_change:.1f}%/{candidate.turnover_share*100:.1f}%)"
        + ("*" if candidate.is_limit_up else "")
        for candidate in leaders
    )


def _format_breakdown(mapping: Dict[str, float]) -> str:
    return ", ".join(f"{key}={value:.2f}" for key, value in mapping.items())


def build_daily_report(
    as_of: date,
    board_scores: Iterable[BoardScore],
    leaders: Dict[str, List[LeaderCandidate]],
    allocations: Dict[str, float],
    predictions: Dict[str, float],
    rotation_candidates: Sequence[RpsCandidate],
    candidate_boards: Sequence[RpsCandidate],
    regime_summary: Dict[str, float],
) -> str:
    lines: List[str] = []
    lines.append(f"Sector rotation summary for {as_of.isoformat()}")
    lines.append("=")
    lines.append(
        f"Regime: {regime_summary.get('regime', 'neutral')}"
        f" | Strength={regime_summary.get('avg_strength', 0.0):.2f}"
        f" | Rotation={regime_summary.get('avg_rotation', 0.0):.2f}"
        f" | Exposure={regime_summary.get('multiplier', 0.0):.1f}x"
    )
    lines.append("")

    lines.append("Top Boards")
    lines.append("-")
    for score in board_scores:
        allocation = allocations.get(score.board, 0.0)
        prediction = predictions.get(score.board, 0.0)
        lines.append(
            f"{score.board}: score={score.score:.2f} alloc={allocation:,.0f} next={prediction:.2f}"
        )
        leader_details = leaders.get(score.board, [])
        if leader_details:
            lines.append(f"  leaders: {_format_leaders(leader_details)}")
        if score.breakdown:
            lines.append(f"  factors: {_format_breakdown(score.breakdown)}")

    if rotation_candidates:
        lines.append("")
        lines.append("RPS Candidates")
        lines.append("-")
        for candidate in rotation_candidates:
            lines.append(
                f"{candidate.board}: rps={candidate.predicted:.2f}"
                f" ({_format_breakdown(candidate.breakdown)})"
            )

    if candidate_boards:
        lines.append("")
        lines.append("Next Rotation Watchlist")
        lines.append("-")
        for candidate in candidate_boards:
            lines.append(
                f"{candidate.board}: ready={candidate.predicted:.2f}"
                f" ({_format_breakdown(candidate.breakdown)})"
            )

    return "\n".join(lines)
