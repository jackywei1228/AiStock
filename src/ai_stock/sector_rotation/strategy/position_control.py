"""Position sizing helper."""
from __future__ import annotations

from statistics import mean
from typing import Dict, Iterable, List, Mapping

from ..models.strong_board import BoardScore


def assess_market_regime(
    strengths: Iterable[BoardScore],
    rotation_predictions: Mapping[str, float],
) -> Dict[str, float]:
    """Determine portfolio aggressiveness based on current breadth."""

    boards: List[BoardScore] = list(strengths)
    if not boards:
        return {"regime": "neutral", "multiplier": 0.5, "avg_strength": 0.0, "avg_rotation": 0.0}

    avg_strength = mean(score.score for score in boards)
    rotation_values = [rotation_predictions.get(score.board, 0.0) for score in boards]
    avg_rotation = mean(rotation_values) if rotation_values else 0.0

    if avg_strength >= 25 and avg_rotation >= 15:
        regime, multiplier = "bullish", 1.0
    elif avg_strength >= 15 and avg_rotation >= 8:
        regime, multiplier = "constructive", 0.8
    elif avg_strength <= 8 and avg_rotation <= 3:
        regime, multiplier = "defensive", 0.4
    else:
        regime, multiplier = "neutral", 0.6

    return {
        "regime": regime,
        "multiplier": multiplier,
        "avg_strength": avg_strength,
        "avg_rotation": avg_rotation,
    }


def allocate_portfolio(
    cash: float,
    selections: Iterable[BoardScore],
    regime: Mapping[str, float],
) -> Dict[str, float]:
    picks = list(selections)
    if not picks:
        return {}

    multiplier = float(regime.get("multiplier", 1.0))
    investable = cash * multiplier
    if investable <= 0:
        return {pick.board: 0.0 for pick in picks}
    per_board = investable / len(picks)
    return {pick.board: per_board for pick in picks}
