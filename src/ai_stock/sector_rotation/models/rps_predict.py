"""Simple RPS style prediction based on rotation components."""
from __future__ import annotations

from typing import Dict

from ..factors.rotation_factor import RotationComponents


def predict_next_session(rotation: Dict[str, RotationComponents], smoothing: float = 0.7) -> Dict[str, float]:
    """Create a lightweight next-session prediction.

    The estimate is a smoothed view of the current rotation score with
    the synergy component acting as a booster for consensus setups.
    """

    predictions: Dict[str, float] = {}
    for board, component in rotation.items():
        predictions[board] = component.score * smoothing + component.synergy
    return predictions
