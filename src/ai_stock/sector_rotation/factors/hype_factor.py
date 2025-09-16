"""Trading activity and sentiment oriented metrics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..data.board_hot import BoardHotMetric
from ..utils.indicators import moving_average


@dataclass(frozen=True)
class HypeComponents:
    avg_turnover_rate: float
    avg_turnover: float
    hot_trend: float
    hot_change: float

    @property
    def score(self) -> float:
        return (
            self.avg_turnover_rate * 10
            + self.avg_turnover / 1_000_000
            + self.hot_trend * 2
            + self.hot_change * 1.5
        )


def calculate_hype_factor(hot_metrics: Dict[str, List[BoardHotMetric]]) -> Dict[str, HypeComponents]:
    results: Dict[str, HypeComponents] = {}
    for board, metrics in hot_metrics.items():
        if not metrics:
            continue
        turnover_rates = [m.hot_score for m in metrics]
        mentions = [m.mentions for m in metrics]
        avg_turnover_rate = moving_average(turnover_rates)
        avg_turnover = moving_average(mentions)
        hot_trend = _momentum(turnover_rates)
        hot_change = _momentum(mentions)
        results[board] = HypeComponents(
            avg_turnover_rate=avg_turnover_rate,
            avg_turnover=avg_turnover,
            hot_trend=hot_trend,
            hot_change=hot_change,
        )
    return results


def _momentum(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    start = values[0]
    end = values[-1]
    if start == 0:
        return 0.0
    return (end - start) / start
