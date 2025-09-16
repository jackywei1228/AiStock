"""Persistence helpers for analysis results."""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List

from ..factors.leader_factor import LeaderCandidate
from ..models.strong_board import BoardScore
from .database import Database


def write_results(
    db: Database,
    run_date: date,
    board_scores: Iterable[BoardScore],
    leaders: Dict[str, List[LeaderCandidate]],
) -> None:
    iso_date = run_date.isoformat()
    for score in board_scores:
        db.append(
            "board_scores",
            {
                "run_date": iso_date,
                "board_code": score.board,
                "score": score.score,
                "breakdown": score.breakdown,
            },
        )
        for leader in leaders.get(score.board, []):
            db.append(
                "leader_candidates",
                {
                    "run_date": iso_date,
                    "board_code": score.board,
                    "symbol": leader.symbol,
                    "return_pct": leader.return_pct,
                    "avg_turnover": leader.avg_turnover,
                },
            )
