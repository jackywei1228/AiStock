"""Persistence helpers for analysis results."""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List, Sequence

from ..factors.leader_factor import LeaderCandidate
from ..models.rps_predict import RpsCandidate
from ..models.strong_board import BoardScore
from .database import Database


def write_results(
    db: Database,
    run_date: date,
    board_scores: Iterable[BoardScore],
    rotation_candidates: Sequence[RpsCandidate],
    leaders: Dict[str, List[LeaderCandidate]],
) -> None:
    iso_date = run_date.isoformat()
    for score in board_scores:
        db.append(
            "strong_boards",
            {
                "run_date": iso_date,
                "board_name": score.board,
                "score": score.score,
                "trend_score": float(score.breakdown.get("trend", 0.0)),
                "hype_score": float(score.breakdown.get("hype", 0.0)),
                "capital_score": float(score.breakdown.get("capital", 0.0)),
                "leader_score": float(score.breakdown.get("leader", 0.0)),
            },
        )
        for leader in leaders.get(score.board, []):
            db.append(
                "leaders",
                {
                    "run_date": iso_date,
                    "board_name": score.board,
                    "stock_code": leader.symbol,
                    "stock_name": leader.name,
                    "is_leader": 1,
                    "strength": leader.score,
                },
            )

    for candidate in rotation_candidates:
        breakdown = candidate.breakdown
        db.append(
            "rps_candidates",
            {
                "run_date": iso_date,
                "board_name": candidate.board,
                "rps_score": candidate.predicted,
                "relative_lag": float(breakdown.get("relative_lag", 0.0)),
                "capital_spillover": float(breakdown.get("capital_spillover", 0.0)),
                "hype_spillover": float(breakdown.get("hype_spillover", 0.0)),
                "tech_ready": float(breakdown.get("technical_readiness", 0.0)),
            },
        )
