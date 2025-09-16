"""Trading activity and sentiment oriented metrics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..data.board_hot import BoardHotMetric
from ..utils.indicators import moving_average


@dataclass(frozen=True)
class HypeComponents:
    hot_score: float
    mentions: float

    @property
    def score(self) -> float:
        return self.hot_score * 0.8 + self.mentions * 0.0005


def calculate_hype_factor(hot_metrics: Dict[str, List[BoardHotMetric]]) -> Dict[str, HypeComponents]:
    results: Dict[str, HypeComponents] = {}
    for board, metrics in hot_metrics.items():
        avg_hot = moving_average(m.hot_score for m in metrics)
        avg_mentions = moving_average(m.mentions for m in metrics)
        results[board] = HypeComponents(hot_score=avg_hot, mentions=avg_mentions)
    return results
